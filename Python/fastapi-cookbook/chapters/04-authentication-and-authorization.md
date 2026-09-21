# Chapter 4 — Authentication and Authorization

> **Project:** `saas_app`

---

## 🎯 What This Chapter Covers

A full SaaS auth stack: JWT tokens with python-jose, Role-Based Access Control (RBAC) by chaining dependencies, GitHub OAuth 2.0 social login, TOTP-based Multi-Factor Authentication, and API key authentication. Each mechanism is an independent router you compose into the app.

---

## 🧠 Auth Concepts First

Before code, understand the difference between **authentication** and **authorization**:

- **Authentication** — Who are you? (login, tokens, sessions)
- **Authorization** — What are you allowed to do? (roles, permissions, ownership)

FastAPI handles both through `Depends()` chains. Every protected endpoint declares a dependency on a function that checks auth — and you chain those functions to add more layers.

```
Request with "Authorization: Bearer <token>"
    ↓
get_current_user(token) → decodes JWT → finds user in DB → returns User
    ↓ (if caller needs premium)
get_premium_user(user) → checks user.role == "premium" → returns User (or 401)
    ↓
Your endpoint logic runs
```

---

## 🔑 JWT Authentication — Full Implementation

JWT (JSON Web Token) is a signed string containing claims (`sub` = subject/username, `exp` = expiry). The server signs it with a secret key — anyone can read it, but only the server can generate valid ones.

```python
# auth/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status

# In production: use a cryptographically random secret
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = "your-256-bit-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(subject: str) -> str:
    """
    Create a JWT token for a given subject (usually username or user_id).
    The token expires after ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    payload = {
        "sub": subject,                                          # who the token is for
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),                               # issued at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    """
    Decode a JWT token and return the subject.
    Raises HTTPException if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=401, detail="Token has no subject")
        return subject
    except JWTError as e:
        # JWTError covers: expired, invalid signature, malformed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

```python
# auth/security.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from auth.jwt import create_access_token, decode_token
from database import get_session
from models import User

router = APIRouter(tags=["auth"])

# CryptContext manages password hashing — bcrypt is industry standard
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# oauth2_scheme extracts the Bearer token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# This function is used as a Depends() — it's called on EVERY request to a protected endpoint
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Extract and verify the token, then load the user from the database."""
    username = decode_token(token)   # raises 401 if invalid
    user = session.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user

@router.post("/auth/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Login with username + password, get back a JWT token.
    Form-encoded body (application/x-www-form-urlencoded), NOT JSON.
    """
    user = session.query(User).filter(User.username == form_data.username).first()

    # Always compare both username and password — never reveal which was wrong
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/register", status_code=201)
def register(username: str, password: str, session: Session = Depends(get_session)):
    existing = session.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(username=username, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    return {"message": "Account created"}
```

---

## 👥 Role-Based Access Control (RBAC) — Chained Dependencies

RBAC is implemented by chaining `Depends()`. Each function in the chain adds one more requirement.

```python
# auth/rbac.py
from enum import Enum
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from auth.security import get_current_user
from models import User

class Role(str, Enum):
    free = "free"
    premium = "premium"
    admin = "admin"

# Level 1: just needs to be logged in
def require_authenticated(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    return user   # get_current_user already validates the token

# Level 2: must be premium or admin
def require_premium(
    user: Annotated[User, Depends(get_current_user)],  # runs get_current_user first
) -> User:
    if user.role not in (Role.premium, Role.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,   # 403, not 401 — authenticated but not authorized
            detail="Premium subscription required",
        )
    return user

# Level 3: must be admin
def require_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


router = APIRouter(tags=["access"])

# Free tier: any logged-in user
@router.get("/dashboard")
def dashboard(user: Annotated[User, Depends(require_authenticated)]):
    return {"message": f"Welcome, {user.username}!"}

# Premium tier: only premium + admin
@router.get("/premium/analytics")
def premium_analytics(user: Annotated[User, Depends(require_premium)]):
    return {"message": f"Analytics for {user.username}", "data": [...]}

# Admin only
@router.delete("/admin/users/{user_id}")
def admin_delete_user(
    user_id: int,
    admin: Annotated[User, Depends(require_admin)],
    session: Session = Depends(get_session),
):
    # admin is the authenticated admin user making this request
    target = session.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(target)
    session.commit()
    return {"message": f"Deleted user {user_id}"}
```

**The key distinction: 401 vs 403**
- `401 Unauthorized` — you're not logged in at all (missing/invalid token)
- `403 Forbidden` — you're logged in but don't have permission for this resource

---

## 🐙 GitHub OAuth Login — The Three-Step Flow

OAuth 2.0 lets users log in with their GitHub account instead of creating a password. The flow has three steps:

```
Step 1: User clicks "Login with GitHub"
        → Your server redirects them to GitHub's authorization page
        → URL includes your client_id so GitHub knows who's asking

Step 2: User approves on GitHub
        → GitHub redirects back to YOUR callback URL with a one-time code
        → e.g. https://yourapp.com/login/github/callback?code=abc123

Step 3: Your server exchanges the code for a GitHub access token
        → GET https://api.github.com/user with the token → get user's profile
        → Issue your OWN JWT token and return it to the client
```

```python
# auth/github.py
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from auth.jwt import create_access_token
from models import User
from database import get_session

router = APIRouter(tags=["oauth"])

GITHUB_CLIENT_ID = "your_github_client_id"       # from GitHub Apps settings
GITHUB_CLIENT_SECRET = "your_github_client_secret"
GITHUB_REDIRECT_URI = "http://localhost:8000/login/github/callback"

@router.get("/login/github")
def initiate_github_login():
    """
    Step 1: Redirect the user to GitHub's OAuth authorization page.
    GitHub shows a consent screen: "Application X wants to access your account"
    """
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        "&scope=user:email"   # what data we're asking for
    )
    return RedirectResponse(url=github_auth_url)

@router.get("/login/github/callback")
async def github_callback(
    code: str,    # GitHub sends this as a query param after user approves
    session = Depends(get_session),
):
    """
    Step 2 + 3: Exchange the code for a token, fetch user info, issue our own token.
    """
    async with httpx.AsyncClient() as client:
        # Exchange code → GitHub access token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},   # ask for JSON, not query string
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        token_data = token_response.json()
        github_token = token_data.get("access_token")
        if not github_token:
            raise HTTPException(status_code=400, detail="GitHub denied access")

        # Use GitHub token to fetch user's profile
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        github_user = user_response.json()
        github_username = github_user["login"]
        github_email = github_user.get("email")

    # Find or create a user in our database
    user = session.query(User).filter(User.github_id == github_user["id"]).first()
    if not user:
        user = User(
            username=github_username,
            email=github_email,
            github_id=github_user["id"],
            role=Role.free,
        )
        session.add(user)
        session.commit()

    # Issue our own JWT — client uses this from now on
    our_token = create_access_token(subject=user.username)
    return {"access_token": our_token, "token_type": "bearer"}
```

---

## 🔐 Multi-Factor Authentication (TOTP)

TOTP (Time-based One-Time Password) generates a 6-digit code that changes every 30 seconds. The user's authenticator app (Google Authenticator, Authy) and your server share a secret key and generate the same code independently.

```python
# auth/mfa.py
import pyotp
from fastapi import APIRouter, Depends, HTTPException
from auth.security import get_current_user
from models import User

router = APIRouter(prefix="/mfa", tags=["mfa"])

@router.post("/setup")
def setup_mfa(user: User = Depends(get_current_user), session = Depends(get_session)):
    """
    Generate a TOTP secret for this user and return a QR code URI.
    The user scans the URI with their authenticator app.
    """
    secret = pyotp.random_base32()   # 32-character base32 string
    totp = pyotp.TOTP(secret)

    # Store the secret (encrypted) in the DB — needed to verify codes later
    user.totp_secret = secret
    user.mfa_enabled = False    # not enabled until they verify it works
    session.commit()

    # provisioning_uri creates the otpauth:// URL that authenticator apps understand
    qr_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="MyApp",
    )

    return {
        "secret": secret,    # show this as text backup
        "qr_uri": qr_uri,    # show this as a QR code (use qrcode library)
        "message": "Scan the QR code with your authenticator app, then call /mfa/verify"
    }

@router.post("/verify")
def verify_and_enable_mfa(
    code: str,
    user: User = Depends(get_current_user),
    session = Depends(get_session),
):
    """
    Verify the user's first TOTP code to confirm MFA is set up correctly.
    Enables MFA on their account.
    """
    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="MFA not set up yet. Call /mfa/setup first.")

    totp = pyotp.TOTP(user.totp_secret)

    # valid_window=1 allows 1 interval before/after current time (clock drift tolerance)
    if not totp.verify(code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid code. Try again.")

    user.mfa_enabled = True
    session.commit()
    return {"message": "MFA enabled successfully"}

@router.post("/validate")
def validate_mfa_code(
    code: str,
    user: User = Depends(get_current_user),
):
    """Called during login to validate the TOTP code (second factor)."""
    if not user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA not enabled for this account")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid MFA code")

    return {"message": "MFA validated"}
```

---

## 🗝️ API Key Authentication

API keys are simpler than JWT for machine-to-machine requests (scripts, integrations) where you don't need short-lived tokens.

```python
# auth/api_key.py
from fastapi import APIRouter, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader, APIKeyQuery
from sqlalchemy.orm import Session
from database import get_session
from models import ApiKey

router = APIRouter(tags=["api-key"])

# APIKeyHeader reads from an HTTP header: X-API-Key: abc123
# APIKeyQuery reads from a query param: ?api_key=abc123
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEY_QUERY = APIKeyQuery(name="api_key", auto_error=False)

def get_api_key(
    header_key: str | None = Security(API_KEY_HEADER),
    query_key: str | None = Security(API_KEY_QUERY),
    session: Session = Depends(get_session),
) -> ApiKey:
    """
    Accept API key from either header or query param.
    Header is preferred (query params end up in server logs).
    """
    raw_key = header_key or query_key
    if not raw_key:
        raise HTTPException(
            status_code=403,
            detail="API key required. Pass X-API-Key header or ?api_key= query param.",
        )

    # Look up in DB — keys should be stored hashed (like passwords)
    api_key = session.query(ApiKey).filter(ApiKey.key == raw_key).first()
    if not api_key or not api_key.is_active:
        raise HTTPException(status_code=403, detail="Invalid or revoked API key")

    return api_key

@router.get("/data")
def get_protected_data(api_key: ApiKey = Security(get_api_key)):
    return {
        "data": "protected content",
        "accessed_by": api_key.name,   # key name, e.g. "production-integration"
    }

@router.post("/keys", status_code=201)
def create_api_key(
    name: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Issue a new API key for the authenticated user."""
    import secrets
    raw_key = secrets.token_urlsafe(32)    # 43-character random key
    api_key = ApiKey(
        key=raw_key,
        name=name,
        owner_id=user.id,
        is_active=True,
    )
    session.add(api_key)
    session.commit()
    return {"key": raw_key, "name": name, "warning": "Save this key — it won't be shown again"}
```

---

## 🔑 Key Takeaways

| Concept | The "why" |
|---------|-----------|
| Chain `Depends()` for roles | Each function adds one auth requirement — `require_admin` calls `require_premium` calls `get_current_user` |
| 401 vs 403 | 401 = not authenticated (wrong/missing token), 403 = authenticated but no permission |
| `OAuth2PasswordRequestForm` expects form data | It's the OAuth2 spec — use `data=` not `json=` when testing |
| `valid_window=1` in TOTP | Allows 1 period (30s) drift for clock sync — without it, users get false rejections |
| API key in header, not query param | Query params end up in server logs — credentials shouldn't |
| `auto_error=False` on APIKeyHeader | Allows fallback to another source (e.g. try header, then query param) |
| `secrets.token_urlsafe(32)` | Cryptographically random — never use `uuid4()` for security tokens |
