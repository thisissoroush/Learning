# Chapter 4 — Authentication and Authorization

> **Project:** `saas_app`
> **Source:** [GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook/tree/main/Chapter04)

---

## 🎯 What This Chapter Covers

A full SaaS authentication system: JWT, Role-Based Access Control (RBAC), GitHub OAuth, Multi-Factor Authentication (MFA), API keys, and user sessions.

---

## 🏗️ App Structure

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=get_engine())  # create tables on startup
    yield

app = FastAPI(title="Saas application", lifespan=lifespan)

# Each auth mechanism is its own router
app.include_router(security.router)        # JWT login/register
app.include_router(premium_access.router)  # subscription tiers
app.include_router(rbac.router)            # role-based access
app.include_router(github_login.router)    # OAuth
app.include_router(mfa.router)             # MFA
app.include_router(user_session.router)    # session management
app.include_router(api_key.router)         # API key auth
```

---

## 🔑 JWT Authentication

```python
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_access_token(token: str, session: Session):
    """Decode JWT and return the user from DB."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = session.query(User).filter(User.username == username).first()
        return user
    except JWTError:
        return None

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> UserWithRole:
    user = decode_access_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )
    return UserWithRole(username=user.username, email=user.email, role=user.role)
```

---

## 👥 Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

class Role(str, Enum):
    free = "free"
    premium = "premium"
    admin = "admin"

def get_premium_user(
    current_user: Annotated[get_current_user, Depends()],
):
    if current_user.role != Role.premium:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )
    return current_user

router = APIRouter()

@router.get("/welcome/all-users")
def all_user_can_access(
    user: Annotated[get_current_user, Depends()],
):
    return {f"Hello {user.username}, welcome to your space"}

@router.get("/welcome/premium-user")
def only_premium_user_can_access(
    user: Annotated[get_premium_user, Depends()],
):
    return {f"Hello {user.username}, welcome to your premium space"}
```

**Pattern:** chain dependencies — `get_premium_user` calls `get_current_user` internally. Add more roles by adding more dependency functions.

---

## 🐙 GitHub OAuth Login

```python
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

GITHUB_CLIENT_ID = "your_client_id"
GITHUB_CLIENT_SECRET = "your_client_secret"

router = APIRouter()

@router.get("/login/github")
def github_login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
    )

@router.get("/login/github/callback")
async def github_callback(code: str):
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={"client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code},
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        github_user = user_resp.json()

    return {"username": github_user["login"], "email": github_user.get("email")}

def resolve_github_token(authorization: str = Header(None)):
    """Middleware-style: extract GitHub user from Bearer token in header."""
    if not authorization:
        raise HTTPException(status_code=403, detail="token not valid")
    token = authorization.removeprefix("Bearer ")
    # verify token with GitHub and return user
    ...
```

---

## 🔐 Multi-Factor Authentication (MFA)

```python
import pyotp
from fastapi import APIRouter

router = APIRouter()

@router.post("/mfa/setup")
def setup_mfa(user: CurrentUser = Depends(get_current_user)):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    # Store secret in DB for this user
    return {
        "secret": secret,
        "qr_uri": totp.provisioning_uri(user.email, issuer_name="SaasApp"),
    }

@router.post("/mfa/verify")
def verify_mfa(
    code: str,
    user: CurrentUser = Depends(get_current_user),
):
    secret = get_user_mfa_secret(user.username)  # from DB
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    return {"message": "MFA verified"}
```

---

## 🗝️ API Key Authentication

```python
from fastapi import APIRouter, Security
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

router = APIRouter()

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    valid_keys = get_valid_api_keys()   # from DB
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@router.get("/api-data")
def get_api_data(api_key: str = Security(verify_api_key)):
    return {"data": "protected content", "authenticated_with": "api_key"}
```

---

## 🔑 Key Takeaways

- Use `lifespan` context manager for startup logic — `Base.metadata.create_all()` on startup
- Chain `Depends()` for layered auth: `get_admin` → calls `get_premium` → calls `get_current_user`
- `Annotated[ReturnType, Depends()]` is the modern type-safe way to declare dependencies
- GitHub OAuth: redirect → code → exchange for token → get user info — three steps
- MFA with `pyotp`: generate secret → store in DB → verify TOTP code on each login
- `APIKeyHeader` for API key auth; `OAuth2PasswordBearer` for Bearer tokens — both via `Depends`/`Security`
- Split each auth mechanism into its own `APIRouter` — composable and testable independently
