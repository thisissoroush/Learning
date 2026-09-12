# Spring Security Interview Questions

> Covers Spring Security 6.x (Spring Boot 3.x). Topics span authentication, authorization, filters, OAuth2, JWT, testing, and architecture patterns from junior to architect level.

---

## 🟢 Junior

### 1. What is the difference between Authentication and Authorization?

**A:** Authentication answers *"Who are you?"* — it verifies the identity of a user (e.g., valid username/password). Authorization answers *"What are you allowed to do?"* — it checks whether the authenticated principal has permission to access a resource.

```
Request → Authentication (identity check) → Authorization (permission check) → Resource
```

In Spring Security:
- **Authentication** is represented by the `Authentication` object stored in `SecurityContext`.
- **Authorization** is enforced by `AuthorizationFilter` (and method-level annotations like `@PreAuthorize`).

```java
// After authentication, check what the user can do
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
boolean isAdmin = auth.getAuthorities().stream()
    .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
```

---

### 2. What is `SecurityFilterChain` and why is it important?

**A:** `SecurityFilterChain` is the primary building block of Spring Security. It is a chain of `javax.servlet.Filter` instances that intercepts incoming HTTP requests and applies security rules. Each filter in the chain handles a specific concern (authentication, CSRF, session, headers, etc.).

In Spring Security 6, you define it as a `@Bean`:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults());
        return http.build();
    }
}
```

Key built-in filters (in order): `SecurityContextHolderFilter`, `UsernamePasswordAuthenticationFilter`, `BasicAuthenticationFilter`, `ExceptionTranslationFilter`, `AuthorizationFilter`.

---

### 3. What is `UserDetailsService` and how do you implement it?

**A:** `UserDetailsService` is a core interface Spring Security uses to load user data during authentication. It has a single method: `loadUserByUsername(String username)`.

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserRepository userRepository;

    public CustomUserDetailsService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByEmail(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));

        return org.springframework.security.core.userdetails.User.builder()
            .username(user.getEmail())
            .password(user.getPassword())          // must be encoded
            .roles(user.getRole().name())          // e.g., "ADMIN" → "ROLE_ADMIN"
            .accountExpired(!user.isActive())
            .build();
    }
}
```

---

### 4. What is `PasswordEncoder` and why must you never store plain-text passwords?

**A:** `PasswordEncoder` is the interface for hashing passwords. Spring Security ships with several implementations; **BCryptPasswordEncoder** is the recommended default because BCrypt is a slow, salted, adaptive hash function — it is computationally expensive for attackers to brute-force.

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // strength 12 (default is 10)
}

// Encoding at registration
String raw = "mysecretpassword";
String encoded = passwordEncoder.encode(raw);  // $2a$12$...

// Verifying at login (done internally by DaoAuthenticationProvider)
boolean matches = passwordEncoder.matches(raw, encoded); // true
```

Never store raw passwords. Even MD5/SHA-1 are insufficient — they are fast and rainbow-table-vulnerable.

---

### 5. What is the difference between `hasRole()` and `hasAuthority()`?

**A:** Both check the `GrantedAuthority` list of the authenticated user, but with a key naming convention difference:

| Method | Prefix added automatically | Example authority string |
|---|---|---|
| `hasRole("ADMIN")` | `ROLE_` prepended | checks for `ROLE_ADMIN` |
| `hasAuthority("ROLE_ADMIN")` | None | checks for exactly `ROLE_ADMIN` |
| `hasAuthority("orders:read")` | None | checks for `orders:read` |

```java
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/admin/**").hasRole("ADMIN")           // looks for ROLE_ADMIN
    .requestMatchers("/orders").hasAuthority("orders:read")  // looks for orders:read
);
```

Use `hasRole` for coarse-grained roles; `hasAuthority` for fine-grained permissions/scopes.

---

### 6. What is CSRF and how does Spring Security protect against it?

**A:** Cross-Site Request Forgery (CSRF) tricks an authenticated user's browser into sending a malicious request to your server using their existing session cookie.

Spring Security's `CsrfFilter` generates a unique token per session and requires it on state-changing requests (POST, PUT, DELETE). The token is validated on each such request.

```java
// CSRF enabled by default for browser apps. To customize:
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()) // for SPAs
);

// For pure REST APIs with stateless JWT, CSRF can be disabled:
http.csrf(AbstractHttpConfigurer::disable);
```

In Thymeleaf, the token is injected automatically into forms via `th:action`.

---

### 7. What is CORS and how do you configure it in Spring Security?

**A:** CORS (Cross-Origin Resource Sharing) is a browser mechanism that restricts JavaScript from making requests to a different origin. Spring Security must be configured to allow legitimate cross-origin requests *before* security checks run.

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .cors(cors -> cors.configurationSource(corsConfigurationSource()))
        // ... rest of config
        ;
    return http.build();
}

@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://myfrontend.com"));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("*"));
    config.setAllowCredentials(true);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

> ⚠️ Never use `allowedOrigins("*")` with `allowCredentials(true)` — browsers block this combination.

---

### 8. What is Basic Authentication and how do you enable it?

**A:** HTTP Basic Authentication sends `Base64(username:password)` in the `Authorization` header on every request. It is simple but requires HTTPS to be secure (credentials are not encrypted by Base64 alone).

```java
http
    .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
    .httpBasic(Customizer.withDefaults()); // enables Basic Auth
```

A request looks like:
```
GET /api/data HTTP/1.1
Authorization: Basic dXNlcjpwYXNzd29yZA==
```

Suitable for machine-to-machine APIs in trusted environments; for browsers, prefer Form Login or OAuth2.

---

### 9. What is Form Login and how does it work in Spring Security?

**A:** Form Login presents an HTML login page. On submit, `UsernamePasswordAuthenticationFilter` intercepts POST `/login`, extracts credentials, delegates to `AuthenticationManager`, and on success stores the `Authentication` in the `SecurityContext` (typically in a session).

```java
http
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/login", "/public/**").permitAll()
        .anyRequest().authenticated()
    )
    .formLogin(form -> form
        .loginPage("/login")                     // custom login page
        .loginProcessingUrl("/perform-login")    // POST endpoint
        .defaultSuccessUrl("/dashboard", true)
        .failureUrl("/login?error=true")
    )
    .logout(logout -> logout
        .logoutUrl("/logout")
        .logoutSuccessUrl("/login?logout=true")
        .invalidateHttpSession(true)
        .deleteCookies("JSESSIONID")
    );
```

---

### 10. What is `SecurityContext` and `SecurityContextHolder`?

**A:** `SecurityContext` holds the current `Authentication` object (the logged-in user's principal, credentials, and authorities). `SecurityContextHolder` is a thread-local container that stores the `SecurityContext` for the duration of a request.

```java
// Reading the current user anywhere in the application:
Authentication auth = SecurityContextHolder.getContext().getAuthentication();

if (auth != null && auth.isAuthenticated()) {
    String username = auth.getName();
    Collection<? extends GrantedAuthority> roles = auth.getAuthorities();
}

// Setting it manually (e.g., in a JWT filter):
SecurityContext context = SecurityContextHolder.createEmptyContext();
UsernamePasswordAuthenticationToken token =
    new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
context.setAuthentication(token);
SecurityContextHolder.setContext(context);
```

The default storage strategy is `ThreadLocal` (`MODE_THREADLOCAL`). For reactive apps, `ReactiveSecurityContextHolder` is used instead.

---

## 🟡 Mid

### 11. What is `AuthenticationManager` and `AuthenticationProvider`, and how do they relate?

**A:** `AuthenticationManager` is the top-level interface with a single method `authenticate(Authentication)`. Its standard implementation is `ProviderManager`, which delegates to a list of `AuthenticationProvider` instances — each handling a specific authentication type.

```
Request → AuthenticationManager (ProviderManager)
               ↓ iterates providers
          DaoAuthenticationProvider  ← handles username/password
          JwtAuthenticationProvider  ← handles JWT tokens
          LdapAuthenticationProvider ← handles LDAP
```

```java
// Custom AuthenticationProvider
@Component
public class OtpAuthenticationProvider implements AuthenticationProvider {

    @Override
    public Authentication authenticate(Authentication auth) throws AuthenticationException {
        String username = auth.getName();
        String otp = (String) auth.getCredentials();

        if (!otpService.isValid(username, otp)) {
            throw new BadCredentialsException("Invalid OTP");
        }
        UserDetails user = userDetailsService.loadUserByUsername(username);
        return new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
    }

    @Override
    public boolean supports(Class<?> authentication) {
        return OtpAuthenticationToken.class.isAssignableFrom(authentication);
    }
}

// Wiring it in:
@Bean
public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
    return config.getAuthenticationManager();
}
```

---

### 12. How do you implement a custom filter with `OncePerRequestFilter`?

**A:** `OncePerRequestFilter` guarantees a filter executes exactly once per request (important for filter chains that may forward internally). It is the right base class for JWT parsing, audit logging, tenant resolution, etc.

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;
    private final UserDetailsService userDetailsService;

    public JwtAuthenticationFilter(JwtTokenProvider jwtTokenProvider,
                                   UserDetailsService userDetailsService) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.userDetailsService = userDetailsService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {

        String header = request.getHeader(HttpHeaders.AUTHORIZATION);

        if (header == null || !header.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = header.substring(7);

        if (jwtTokenProvider.validateToken(token)) {
            String username = jwtTokenProvider.extractUsername(token);
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);

            UsernamePasswordAuthenticationToken auth =
                new UsernamePasswordAuthenticationToken(
                    userDetails, null, userDetails.getAuthorities());
            auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));

            SecurityContextHolder.getContext().setAuthentication(auth);
        }

        filterChain.doFilter(request, response);
    }
}

// Register it before UsernamePasswordAuthenticationFilter:
http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
```

---

### 13. How does method-level security work? What is the difference between `@PreAuthorize`, `@PostAuthorize`, and `@Secured`?

**A:** Enable method security with `@EnableMethodSecurity` (Spring Security 6+). Each annotation intercepts method calls via AOP proxies.

| Annotation | When evaluated | SpEL support | Recommendation |
|---|---|---|---|
| `@PreAuthorize` | Before method executes | ✅ Yes | ✅ Preferred |
| `@PostAuthorize` | After method returns | ✅ Yes (access `returnObject`) | Use for data filtering |
| `@Secured` | Before method executes | ❌ No (roles only) | Legacy; prefer `@PreAuthorize` |

```java
@Configuration
@EnableMethodSecurity  // replaces @EnableGlobalMethodSecurity in Spring Security 6
public class MethodSecurityConfig {}

// Service layer:
@Service
public class OrderService {

    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
    public Order getOrder(Long orderId, Long userId) { ... }

    @PostAuthorize("returnObject.ownerId == authentication.principal.id")
    public Order findOrder(Long orderId) { ... }

    @PreAuthorize("hasAuthority('orders:delete')")
    public void deleteOrder(Long orderId) { ... }

    @Secured({"ROLE_ADMIN", "ROLE_MANAGER"})
    public List<Order> getAllOrders() { ... }
}
```

---

### 14. How do you configure session management in Spring Security?

**A:** Session management controls how sessions are created, used, and expired.

```java
http.sessionManagement(session -> session
    // Session creation policies:
    // ALWAYS    - always create a session
    // IF_REQUIRED - create only when needed (default)
    // NEVER     - never create, but use existing
    // STATELESS - never create or use sessions (JWT APIs)
    .sessionCreationPolicy(SessionCreationPolicy.STATELESS)

    // Concurrent session control (for browser apps):
    .maximumSessions(1)                   // max 1 concurrent session per user
    .maxSessionsPreventsLogin(false)      // false = expire old session; true = reject new login
    .expiredUrl("/session-expired")
);
```

For stateless JWT REST APIs:
```java
http.sessionManagement(session -> session
    .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
);
```

---

### 15. How do you configure an OAuth2 Resource Server for JWT validation?

**A:** An OAuth2 Resource Server validates JWTs on every request. Spring Security 6 has built-in support.

```xml
<!-- pom.xml dependency -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.myapp.com          # OIDC discovery
          # OR:
          jwk-set-uri: https://auth.myapp.com/.well-known/jwks.json
```

```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/public/**").permitAll()
            .anyRequest().authenticated()
        )
        .oauth2ResourceServer(oauth2 -> oauth2
            .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthenticationConverter()))
        )
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .csrf(AbstractHttpConfigurer::disable);
    return http.build();
}

// Map JWT claims to Spring Security authorities:
@Bean
public JwtAuthenticationConverter jwtAuthenticationConverter() {
    JwtGrantedAuthoritiesConverter converter = new JwtGrantedAuthoritiesConverter();
    converter.setAuthorityPrefix("ROLE_");
    converter.setAuthoritiesClaimName("roles");  // custom claim name

    JwtAuthenticationConverter jwtConverter = new JwtAuthenticationConverter();
    jwtConverter.setJwtGrantedAuthoritiesConverter(converter);
    return jwtConverter;
}
```

---

### 16. How do you enforce HTTPS and configure security headers?

**A:** Spring Security's `HeadersConfigurer` and `requiresChannel` handle these concerns.

```java
http
    // Force HTTPS on all requests:
    .requiresChannel(channel -> channel
        .anyRequest().requiresSecure()
    )
    // Security headers:
    .headers(headers -> headers
        // HTTP Strict Transport Security (HSTS) - tells browsers to always use HTTPS
        .httpStrictTransportSecurity(hsts -> hsts
            .includeSubDomains(true)
            .maxAgeInSeconds(31536000) // 1 year
            .preload(true)
        )
        // Prevent clickjacking
        .frameOptions(frame -> frame.deny())
        // Content Security Policy - restrict resource loading
        .contentSecurityPolicy(csp -> csp
            .policyDirectives(
                "default-src 'self'; " +
                "script-src 'self' 'nonce-{RANDOM}'; " +
                "style-src 'self' https://fonts.googleapis.com; " +
                "img-src 'self' data:; " +
                "frame-ancestors 'none'"
            )
        )
        // Prevent MIME-type sniffing
        .contentTypeOptions(Customizer.withDefaults())
        // Referrer Policy
        .referrerPolicy(referrer -> referrer
            .policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN)
        )
    );
```

---

### 17. How do you test Spring Security with `@WithMockUser` and `SecurityMockMvcRequestPostProcessors`?

**A:** Spring Security Test provides two complementary approaches:

**`@WithMockUser`** — injects a fake `Authentication` into `SecurityContext` for the test method:

```java
@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @WithMockUser(username = "alice", roles = {"USER"})
    void getOrder_asUser_returns200() throws Exception {
        mockMvc.perform(get("/api/orders/1"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(username = "admin", authorities = {"ROLE_ADMIN", "orders:delete"})
    void deleteOrder_asAdmin_returns204() throws Exception {
        mockMvc.perform(delete("/api/orders/1"))
            .andExpect(status().isNoContent());
    }

    @Test
    void getOrder_unauthenticated_returns401() throws Exception {
        mockMvc.perform(get("/api/orders/1"))
            .andExpect(status().isUnauthorized());
    }
}
```

**`SecurityMockMvcRequestPostProcessors`** — applies authentication inline per request (useful for parameterized tests):

```java
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;

@Test
void getOrder_withJwt_returns200() throws Exception {
    mockMvc.perform(get("/api/orders/1")
            .with(jwt()
                .authorities(new SimpleGrantedAuthority("ROLE_USER"))
                .jwt(token -> token.claim("sub", "alice").claim("email", "alice@example.com"))
            ))
        .andExpect(status().isOk());
}

@Test
void createOrder_withCsrf_returns201() throws Exception {
    mockMvc.perform(post("/api/orders")
            .with(user("alice").roles("USER"))
            .with(csrf())
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"item\": \"book\"}"))
        .andExpect(status().isCreated());
}
```

---

### 18. What is Remember-Me authentication and how does it work?

**A:** Remember-Me allows a user to stay logged in across browser sessions via a persistent cookie.

Spring Security provides two implementations:
- **Simple Hash-Based** (default) — stores `HMAC(username + expirationTime + password + key)` in cookie. Stateless but invalidated by password changes.
- **Persistent Token** (database-backed) — stores a random series+token in DB. More secure; supports invalidation.

```java
// Simple hash-based:
http.rememberMe(remember -> remember
    .key("my-secret-key-min-32-chars-long!!")
    .tokenValiditySeconds(7 * 24 * 60 * 60) // 7 days
    .rememberMeParameter("remember-me")       // form checkbox name
);

// Persistent token (requires a PersistentTokenRepository bean):
@Bean
public PersistentTokenRepository persistentTokenRepository(DataSource dataSource) {
    JdbcTokenRepositoryImpl repo = new JdbcTokenRepositoryImpl();
    repo.setDataSource(dataSource);
    repo.setCreateTableOnStartup(false); // create the table manually
    return repo;
}

http.rememberMe(remember -> remember
    .tokenRepository(persistentTokenRepository)
    .userDetailsService(userDetailsService)
    .tokenValiditySeconds(7 * 24 * 60 * 60)
);
```

---

### 19. What is the difference between a Role and an Authority in Spring Security?

**A:** In Spring Security, both roles and authorities are represented as `GrantedAuthority` strings. The distinction is purely conventional:

- **Authority** (fine-grained): any string, e.g., `orders:read`, `users:delete`, `reports:export`
- **Role** (coarse-grained): a group of permissions, conventionally prefixed with `ROLE_`, e.g., `ROLE_ADMIN`, `ROLE_USER`

```java
// Granting both:
List<GrantedAuthority> authorities = List.of(
    new SimpleGrantedAuthority("ROLE_MANAGER"),   // role
    new SimpleGrantedAuthority("orders:approve"), // fine-grained authority
    new SimpleGrantedAuthority("reports:read")    // fine-grained authority
);

// Checking in SpEL:
@PreAuthorize("hasRole('MANAGER') and hasAuthority('orders:approve')")
public void approveOrder(Long orderId) { ... }
```

Best practice: Use roles for broad access control, authorities for granular permissions. Map roles → sets of authorities in your service layer.

---

### 20. How does OAuth2 Social Login (e.g., Google, GitHub) work in Spring Security?

**A:** Spring Security's `spring-boot-starter-oauth2-client` provides turnkey social login via the Authorization Code Flow.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-oauth2-client</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            scope: openid, profile, email
          github:
            client-id: ${GITHUB_CLIENT_ID}
            client-secret: ${GITHUB_CLIENT_SECRET}
            scope: read:user, user:email
```

```java
http
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/", "/login").permitAll()
        .anyRequest().authenticated()
    )
    .oauth2Login(oauth2 -> oauth2
        .loginPage("/login")
        .defaultSuccessUrl("/dashboard", true)
        .userInfoEndpoint(userInfo -> userInfo
            .userService(customOAuth2UserService()) // map OAuth2User → your domain User
        )
    );
```

```java
@Service
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    @Override
    public OAuth2User loadUser(OAuth2UserRequest request) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(request);
        String email = oAuth2User.getAttribute("email");
        // Find or create local user, assign roles, etc.
        return new CustomOAuth2User(oAuth2User, localUser.getAuthorities());
    }
}
```

---

## 🔴 Senior

### 21. How do you design and implement JWT token validation from scratch (without using Spring's `oauth2ResourceServer`)?

**A:** Full manual JWT pipeline using `jjwt` (JJWT library):

```xml
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
```

```java
@Component
public class JwtTokenProvider {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration-ms:3600000}") // 1 hour
    private long expirationMs;

    private SecretKey signingKey() {
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
    }

    public String generateToken(Authentication authentication) {
        UserDetails userDetails = (UserDetails) authentication.getPrincipal();
        List<String> roles = userDetails.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .toList();

        return Jwts.builder()
            .subject(userDetails.getUsername())
            .claim("roles", roles)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expirationMs))
            .signWith(signingKey())
            .compact();
    }

    public Claims validateAndExtract(String token) {
        try {
            return Jwts.parser()
                .verifyWith(signingKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
        } catch (ExpiredJwtException e) {
            throw new TokenExpiredException("JWT has expired");
        } catch (JwtException e) {
            throw new InvalidTokenException("JWT is invalid: " + e.getMessage());
        }
    }

    public String extractUsername(String token) {
        return validateAndExtract(token).getSubject();
    }

    public List<String> extractRoles(String token) {
        return validateAndExtract(token).get("roles", List.class);
    }

    public boolean validateToken(String token) {
        try {
            validateAndExtract(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
```

Pair this with a `JwtAuthenticationFilter extends OncePerRequestFilter` (see Q12).

---

### 22. How do you implement concurrent session control and what are the trade-offs?

**A:** Concurrent session control limits how many simultaneous sessions a user can have.

```java
// 1. Register HttpSessionEventPublisher to track sessions:
@Bean
public HttpSessionEventPublisher httpSessionEventPublisher() {
    return new HttpSessionEventPublisher();
}

// 2. Configure in SecurityFilterChain:
http.sessionManagement(session -> session
    .maximumSessions(2)
    .maxSessionsPreventsLogin(false) // false = expire oldest; true = block new login
    .expiredUrl("/session-expired")
    .sessionRegistry(sessionRegistry())
);

@Bean
public SessionRegistry sessionRegistry() {
    return new SessionRegistryImpl();
}
```

**Querying active sessions:**
```java
@Autowired
private SessionRegistry sessionRegistry;

public List<String> getActiveSessions() {
    return sessionRegistry.getAllPrincipals().stream()
        .filter(principal -> !sessionRegistry.getAllSessions(principal, false).isEmpty())
        .map(principal -> ((UserDetails) principal).getUsername())
        .toList();
}

// Force logout a user:
public void forceLogout(String username) {
    sessionRegistry.getAllPrincipals().stream()
        .filter(p -> ((UserDetails) p).getUsername().equals(username))
        .flatMap(p -> sessionRegistry.getAllSessions(p, false).stream())
        .forEach(SessionInformation::expireNow);
}
```

**Trade-offs:**
- Works only for session-based (stateful) apps — not applicable to stateless JWT
- In clustered environments, requires a distributed `SessionRegistry` (e.g., backed by Redis via Spring Session)

---

### 23. How do you implement multi-tenancy security in Spring Security?

**A:** Multi-tenancy security ensures users can only access data from their own tenant. Common approaches:

**Approach 1: Tenant from JWT claims + custom filter**
```java
@Component
public class TenantContextFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();

        if (auth instanceof JwtAuthenticationToken jwt) {
            String tenantId = jwt.getToken().getClaimAsString("tenant_id");
            TenantContext.setTenantId(tenantId);
        }

        try {
            chain.doFilter(request, response);
        } finally {
            TenantContext.clear(); // always clean up ThreadLocal
        }
    }
}

// ThreadLocal holder:
public class TenantContext {
    private static final ThreadLocal<String> CURRENT_TENANT = new ThreadLocal<>();

    public static void setTenantId(String tenantId) { CURRENT_TENANT.set(tenantId); }
    public static String getTenantId() { return CURRENT_TENANT.get(); }
    public static void clear() { CURRENT_TENANT.remove(); }
}
```

**Approach 2: Tenant-scoped `AuthenticationProvider`**
```java
@Component
public class TenantAwareAuthenticationProvider implements AuthenticationProvider {

    private final Map<String, UserDetailsService> tenantUserDetailsServices;

    @Override
    public Authentication authenticate(Authentication auth) throws AuthenticationException {
        String tenantId = ((TenantAwareAuthenticationToken) auth).getTenantId();
        UserDetailsService uds = tenantUserDetailsServices.get(tenantId);
        if (uds == null) throw new BadCredentialsException("Unknown tenant: " + tenantId);

        UserDetails user = uds.loadUserByUsername(auth.getName());
        // validate password, build token...
        return new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
    }

    @Override
    public boolean supports(Class<?> auth) {
        return TenantAwareAuthenticationToken.class.isAssignableFrom(auth);
    }
}
```

**Approach 3: Data-layer enforcement via `@PostFilter` / query parameters**
```java
@PreAuthorize("hasRole('USER')")
@PostFilter("filterObject.tenantId == authentication.details.tenantId")
public List<Order> getAllOrders() {
    return orderRepository.findAll(); // filtered post-execution
}
```

---

### 24. How do you implement a custom `AuthenticationEntryPoint` and `AccessDeniedHandler`?

**A:** These hooks control the HTTP response when security exceptions occur:
- `AuthenticationEntryPoint` → 401 Unauthorized (not authenticated)
- `AccessDeniedHandler` → 403 Forbidden (authenticated but lacks permission)

```java
@Component
public class ApiAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private final ObjectMapper objectMapper;

    @Override
    public void commence(HttpServletRequest request,
                         HttpServletResponse response,
                         AuthenticationException authException) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        objectMapper.writeValue(response.getWriter(), Map.of(
            "error", "UNAUTHORIZED",
            "message", "Authentication required",
            "timestamp", Instant.now().toString()
        ));
    }
}

@Component
public class ApiAccessDeniedHandler implements AccessDeniedHandler {

    private final ObjectMapper objectMapper;

    @Override
    public void handle(HttpServletRequest request,
                       HttpServletResponse response,
                       AccessDeniedException accessDeniedException) throws IOException {
        response.setStatus(HttpServletResponse.SC_FORBIDDEN);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        objectMapper.writeValue(response.getWriter(), Map.of(
            "error", "FORBIDDEN",
            "message", "You do not have permission to access this resource",
            "timestamp", Instant.now().toString()
        ));
    }
}

// Wire into SecurityFilterChain:
http.exceptionHandling(ex -> ex
    .authenticationEntryPoint(apiAuthenticationEntryPoint)
    .accessDeniedHandler(apiAccessDeniedHandler)
);
```

---

### 25. How does Spring Security's filter ordering work and how can you customize it?

**A:** Spring Security inserts its filter chain as a single `FilterChainProxy` servlet filter (ordered by default at `SecurityProperties.DEFAULT_FILTER_ORDER = -100`). Inside the chain, filters execute in a fixed order.

```
Request
  │
  ▼
FilterChainProxy (order -100)
  │
  ├── DisableEncodeUrlFilter
  ├── WebAsyncManagerIntegrationFilter
  ├── SecurityContextHolderFilter
  ├── HeaderWriterFilter
  ├── CorsFilter
  ├── CsrfFilter
  ├── LogoutFilter
  ├── UsernamePasswordAuthenticationFilter
  ├── DefaultLoginPageGeneratingFilter
  ├── BasicAuthenticationFilter
  ├── RequestCacheAwareFilter
  ├── SecurityContextHolderAwareRequestFilter
  ├── RememberMeAuthenticationFilter
  ├── AnonymousAuthenticationFilter
  ├── ExceptionTranslationFilter
  └── AuthorizationFilter
```

Adding custom filters at specific positions:
```java
// Before a known filter:
http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);

// After a known filter:
http.addFilterAfter(tenantFilter, SecurityContextHolderFilter.class);

// At a specific position (replacing a standard filter):
http.addFilterAt(customAuthFilter, UsernamePasswordAuthenticationFilter.class);
```

> ⚠️ Never register a custom filter **both** as a `@Bean` AND via `http.addFilterBefore()` — Spring Boot auto-registers `@Bean` filters in the servlet container, causing double execution.

---

### 26. How do you handle token refresh and token revocation with JWT?

**A:** JWTs are stateless by nature — once issued, they are valid until expiry. Managing revocation requires additional infrastructure.

**Token Refresh pattern (Access + Refresh tokens):**
```java
@RestController
@RequestMapping("/auth")
public class AuthController {

    // Short-lived access token (15 min), long-lived refresh token (7 days)
    @PostMapping("/refresh")
    public ResponseEntity<TokenResponse> refresh(@RequestBody @Valid RefreshRequest req) {
        String refreshToken = req.refreshToken();

        // 1. Validate refresh token signature and expiry
        if (!jwtProvider.validateToken(refreshToken)) {
            throw new InvalidTokenException("Refresh token invalid or expired");
        }

        // 2. Check it hasn't been revoked (e.g., from Redis blacklist or DB)
        if (tokenStore.isRevoked(refreshToken)) {
            throw new InvalidTokenException("Refresh token revoked");
        }

        String username = jwtProvider.extractUsername(refreshToken);
        UserDetails user = userDetailsService.loadUserByUsername(username);

        // 3. Issue new access token (optionally rotate refresh token)
        String newAccessToken = jwtProvider.generateAccessToken(user);
        String newRefreshToken = jwtProvider.generateRefreshToken(user);

        // 4. Revoke old refresh token (token rotation)
        tokenStore.revoke(refreshToken);
        tokenStore.store(newRefreshToken);

        return ResponseEntity.ok(new TokenResponse(newAccessToken, newRefreshToken));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@RequestBody LogoutRequest req) {
        tokenStore.revoke(req.accessToken());   // add to blacklist
        tokenStore.revoke(req.refreshToken());
        return ResponseEntity.noContent().build();
    }
}
```

**Redis-backed token store for revocation:**
```java
@Service
public class RedisTokenStore {

    private final StringRedisTemplate redis;

    public void revoke(String token) {
        long ttl = jwtProvider.getRemainingExpiry(token);
        redis.opsForValue().set("revoked:" + token, "1", ttl, TimeUnit.MILLISECONDS);
    }

    public boolean isRevoked(String token) {
        return Boolean.TRUE.equals(redis.hasKey("revoked:" + token));
    }
}
```

---

### 27. How do you write a custom `@WithMockUser`-like annotation for domain-specific security contexts?

**A:** Use `@WithSecurityContext` to create a reusable test annotation that sets up a complex `SecurityContext` matching your domain model:

```java
// 1. Define the annotation:
@Retention(RetentionPolicy.RUNTIME)
@WithSecurityContext(factory = WithMockTenantUserSecurityContextFactory.class)
public @interface WithMockTenantUser {
    String username() default "alice";
    String tenantId() default "tenant-1";
    String[] roles() default {"ROLE_USER"};
}

// 2. Implement the factory:
public class WithMockTenantUserSecurityContextFactory
    implements WithSecurityContextFactory<WithMockTenantUser> {

    @Override
    public SecurityContext createSecurityContext(WithMockTenantUser annotation) {
        List<GrantedAuthority> authorities = Arrays.stream(annotation.roles())
            .map(SimpleGrantedAuthority::new)
            .collect(Collectors.toList());

        TenantUserDetails principal = new TenantUserDetails(
            annotation.username(),
            annotation.tenantId(),
            authorities
        );

        Authentication auth = new UsernamePasswordAuthenticationToken(
            principal, null, authorities);

        SecurityContext context = SecurityContextHolder.createEmptyContext();
        context.setAuthentication(auth);
        return context;
    }
}

// 3. Use in tests:
@Test
@WithMockTenantUser(username = "alice", tenantId = "acme-corp", roles = {"ROLE_ADMIN"})
void adminCanDeleteOrder() throws Exception {
    mockMvc.perform(delete("/api/orders/1"))
        .andExpect(status().isNoContent());
}
```

---

## 🏛️ Architect

### 28. How would you design a Spring Authorization Server for a microservices architecture?

**A:** Spring Authorization Server (SAS) implements the OAuth2 Authorization Server role, issuing access tokens that microservices validate as Resource Servers.

**Authorization Server setup:**
```xml
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-oauth2-authorization-server</artifactId>
</dependency>
```

```java
@Configuration
@EnableWebSecurity
public class AuthorizationServerConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain authorizationServerSecurityFilterChain(HttpSecurity http)
            throws Exception {
        OAuth2AuthorizationServerConfiguration.applyDefaultSecurity(http);

        http.getConfigurer(OAuth2AuthorizationServerConfigurer.class)
            .oidc(Customizer.withDefaults())                // Enable OpenID Connect 1.0
            .tokenGenerator(tokenGenerator())
            .authorizationService(authorizationService())   // custom persistence
            ;

        http.exceptionHandling(ex -> ex
            .defaultAuthenticationEntryPointFor(
                new LoginUrlAuthenticationEntryPoint("/login"),
                new MediaTypeRequestMatcher(MediaType.TEXT_HTML)
            )
        );

        return http.build();
    }

    @Bean
    @Order(2)
    public SecurityFilterChain defaultSecurityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
            .formLogin(Customizer.withDefaults());
        return http.build();
    }

    @Bean
    public RegisteredClientRepository registeredClientRepository() {
        RegisteredClient apiClient = RegisteredClient.withId(UUID.randomUUID().toString())
            .clientId("api-client")
            .clientSecret(passwordEncoder().encode("secret"))
            .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
            .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
            .authorizationGrantType(AuthorizationGrantType.REFRESH_TOKEN)
            .authorizationGrantType(AuthorizationGrantType.CLIENT_CREDENTIALS)
            .redirectUri("https://myapp.com/login/oauth2/code/myapp")
            .scope(OidcScopes.OPENID)
            .scope(OidcScopes.PROFILE)
            .scope("orders:read")
            .scope("orders:write")
            .tokenSettings(TokenSettings.builder()
                .accessTokenTimeToLive(Duration.ofMinutes(15))
                .refreshTokenTimeToLive(Duration.ofDays(7))
                .reuseRefreshTokens(false)
                .build())
            .build();

        return new InMemoryRegisteredClientRepository(apiClient);
    }

    @Bean
    public JWKSource<SecurityContext> jwkSource() {
        RSAKey rsaKey = Jwks.generateRsa();
        JWKSet jwkSet = new JWKSet(rsaKey);
        return (jwkSelector, context) -> jwkSelector.select(jwkSet);
    }

    @Bean
    public AuthorizationServerSettings authorizationServerSettings() {
        return AuthorizationServerSettings.builder()
            .issuer("https://auth.mycompany.com")
            .build();
    }

    // Custom token claims (add tenant, permissions, etc.):
    @Bean
    public OAuth2TokenCustomizer<JwtEncodingContext> tokenCustomizer() {
        return context -> {
            if (context.getTokenType().equals(OAuth2TokenType.ACCESS_TOKEN)) {
                Authentication principal = context.getPrincipal();
                Set<String> authorities = principal.getAuthorities().stream()
                    .map(GrantedAuthority::getAuthority)
                    .collect(Collectors.toSet());
                context.getClaims()
                    .claim("authorities", authorities)
                    .claim("tenant_id", getTenantId(principal));
            }
        };
    }
}
```

**Microservice Resource Server (validates tokens from SAS):**
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.mycompany.com
```

**Architecture diagram:**
```
Browser/App
    │ Authorization Code Flow
    ▼
Spring Authorization Server (auth.mycompany.com)
    │ issues signed JWT
    ▼
API Gateway
    │ forwards JWT
    ├── Order Service (Resource Server)  ← validates via JWKS
    ├── User Service  (Resource Server)  ← validates via JWKS
    └── Payment Service (Resource Server) ← validates via JWKS
```

---

### 29. How would you architect a zero-trust security model for a Spring-based microservices platform?

**A:** Zero-trust assumes no network location is inherently trusted. Every service-to-service call must be authenticated and authorized.

**Key pillars and Spring implementations:**

**1. mTLS for service-to-service communication:**
```java
// Each microservice gets a client certificate; RestTemplate/WebClient verifies peer certs
@Bean
public RestTemplate restTemplate(SSLContext sslContext) throws Exception {
    SSLConnectionSocketFactory socketFactory =
        new SSLConnectionSocketFactory(sslContext, new DefaultHostnameVerifier());
    CloseableHttpClient httpClient = HttpClients.custom()
        .setSSLSocketFactory(socketFactory)
        .build();
    return new RestTemplate(new HttpComponentsClientHttpRequestFactory(httpClient));
}
```

**2. Token propagation between services:**
```java
// Gateway propagates the user's JWT downstream; services re-validate it
@Bean
public WebClient webClient(OAuth2AuthorizedClientManager manager) {
    ServletOAuth2AuthorizedClientExchangeFilterFunction oauth2Client =
        new ServletOAuth2AuthorizedClientExchangeFilterFunction(manager);
    oauth2Client.setDefaultOAuth2AuthorizedClient(true);
    return WebClient.builder().apply(oauth2Client.oauth2Configuration()).build();
}
```

**3. Least-privilege via fine-grained scopes:**
```java
@PreAuthorize("hasAuthority('SCOPE_orders:write') and #order.tenantId == authentication.details.tenantId")
public Order createOrder(Order order) { ... }
```

**4. Centralized policy enforcement (OPA integration):**
```java
@Component
public class OpaAuthorizationManager implements AuthorizationManager<RequestAuthorizationContext> {

    private final WebClient opaClient;

    @Override
    public AuthorizationDecision check(Supplier<Authentication> auth,
                                       RequestAuthorizationContext context) {
        Map<String, Object> input = Map.of(
            "user", auth.get().getName(),
            "roles", auth.get().getAuthorities(),
            "method", context.getRequest().getMethod(),
            "path", context.getRequest().getRequestURI()
        );

        Boolean allowed = opaClient.post()
            .uri("/v1/data/authz/allow")
            .bodyValue(Map.of("input", input))
            .retrieve()
            .bodyToMono(OpaResponse.class)
            .map(OpaResponse::result)
            .block();

        return new AuthorizationDecision(Boolean.TRUE.equals(allowed));
    }
}

// Wire OPA as the global authorization manager:
http.authorizeHttpRequests(auth -> auth
    .anyRequest().access(opaAuthorizationManager)
);
```

**5. Audit logging filter:**
```java
@Component
public class SecurityAuditFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        chain.doFilter(req, res);
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        auditLog.record(AuditEvent.builder()
            .user(auth != null ? auth.getName() : "anonymous")
            .action(req.getMethod() + " " + req.getRequestURI())
            .status(res.getStatus())
            .timestamp(Instant.now())
            .build());
    }
}
```

---

### 30. How do you implement dynamic, database-driven authorization rules that can be changed at runtime without redeployment?

**A:** Replace static SpEL expressions with a dynamic policy engine backed by a database.

```java
// Domain model:
@Entity
public class PermissionRule {
    private String resource;         // e.g., "orders"
    private String action;           // e.g., "DELETE"
    private String roleRequired;     // e.g., "ROLE_MANAGER"
    private String tenantId;         // null = global rule
    private boolean active;
}

// Custom AuthorizationManager that queries DB:
@Component
public class DynamicAuthorizationManager
        implements AuthorizationManager<RequestAuthorizationContext> {

    private final PermissionRuleRepository ruleRepository;
    private final Cache<String, List<PermissionRule>> cache;  // Caffeine cache

    @Override
    public AuthorizationDecision check(Supplier<Authentication> authSupplier,
                                       RequestAuthorizationContext ctx) {
        Authentication auth = authSupplier.get();
        if (auth == null || !auth.isAuthenticated()) return new AuthorizationDecision(false);

        HttpServletRequest request = ctx.getRequest();
        String resource = extractResource(request.getRequestURI()); // e.g., "orders"
        String action = request.getMethod();                         // e.g., "DELETE"

        List<PermissionRule> rules = cache.get(resource + ":" + action,
            key -> ruleRepository.findByResourceAndAction(resource, action));

        Set<String> userAuthorities = auth.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.toSet());

        boolean permitted = rules.stream()
            .filter(PermissionRule::isActive)
            .anyMatch(rule -> userAuthorities.contains(rule.getRoleRequired()));

        return new AuthorizationDecision(permitted);
    }

    // Evict cache when rules change:
    @EventListener
    public void onPermissionRuleChanged(PermissionRuleChangedEvent event) {
        cache.invalidateAll();
    }
}

// Wire it:
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/public/**").permitAll()
    .anyRequest().access(dynamicAuthorizationManager)
);
```

**Cache invalidation strategy:**
```java
@Service
public class PermissionRuleService {

    @CacheEvict(value = "permissionRules", allEntries = true)
    @Transactional
    public PermissionRule updateRule(Long id, PermissionRuleDto dto) {
        PermissionRule rule = ruleRepository.findById(id).orElseThrow();
        // update rule...
        eventPublisher.publishEvent(new PermissionRuleChangedEvent(rule));
        return ruleRepository.save(rule);
    }
}
```

---

### 31. How do you handle security in a Spring reactive (WebFlux) application, and what are the key differences from Spring MVC security?

**A:** Reactive Spring Security uses `ReactorContextHolder` and `SecurityWebFilterChain` instead of the servlet-based equivalents.

**Key differences:**

| Aspect | Spring MVC (Servlet) | Spring WebFlux (Reactive) |
|---|---|---|
| Security context | `SecurityContextHolder` (ThreadLocal) | `ReactiveSecurityContextHolder` (Reactor Context) |
| Filter chain | `SecurityFilterChain` | `SecurityWebFilterChain` |
| Config class | `HttpSecurity` | `ServerHttpSecurity` |
| UserDetails | `UserDetailsService` | `ReactiveUserDetailsService` |
| Auth manager | `AuthenticationManager` | `ReactiveAuthenticationManager` |

```java
@Configuration
@EnableWebFluxSecurity
@EnableReactiveMethodSecurity
public class ReactiveSecurityConfig {

    @Bean
    public SecurityWebFilterChain springWebFilterChain(ServerHttpSecurity http) {
        return http
            .authorizeExchange(auth -> auth
                .pathMatchers("/public/**").permitAll()
                .pathMatchers("/admin/**").hasRole("ADMIN")
                .anyExchange().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.jwtAuthenticationConverter(reactiveJwtConverter()))
            )
            .csrf(ServerHttpSecurity.CsrfSpec::disable)
            .build();
    }

    @Bean
    public ReactiveUserDetailsService reactiveUserDetailsService(UserRepository repo) {
        return username -> repo.findByUsername(username)
            .map(user -> User.builder()
                .username(user.getUsername())
                .password(user.getPassword())
                .roles(user.getRole())
                .build()
            );
    }
}

// Reading security context in reactive pipeline:
@GetMapping("/profile")
public Mono<Profile> getProfile() {
    return ReactiveSecurityContextHolder.getContext()
        .map(SecurityContext::getAuthentication)
        .map(Authentication::getName)
        .flatMap(profileService::findByUsername);
}

// Custom reactive filter:
@Component
public class ReactiveJwtFilter implements WebFilter {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        String token = extractToken(exchange.getRequest());

        if (token == null) return chain.filter(exchange);

        return Mono.just(token)
            .map(jwtProvider::validateAndExtract)
            .flatMap(claims -> {
                Authentication auth = buildAuthentication(claims);
                return chain.filter(exchange)
                    .contextWrite(ReactiveSecurityContextHolder.withAuthentication(auth));
            })
            .onErrorResume(e -> chain.filter(exchange));
    }
}
```

---

### 32. How do you prevent and detect common security vulnerabilities in a Spring Security application?

**A:** A defense-in-depth checklist covering OWASP Top 10 in Spring Security context:

**A01 — Broken Access Control:**
```java
// Always use @PreAuthorize at service layer (not just controller):
@PreAuthorize("@securityService.canAccessOrder(#id, authentication)")
public Order getOrder(Long id) { ... }

// Custom security expression bean:
@Service("securityService")
public class SecurityExpressionService {
    public boolean canAccessOrder(Long orderId, Authentication auth) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        String tenantId = ((CustomPrincipal) auth.getPrincipal()).getTenantId();
        return order.getTenantId().equals(tenantId);
    }
}
```

**A02 — Cryptographic Failures:**
```java
// Use BCrypt with cost factor ≥ 12:
@Bean public PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(12); }

// Enforce TLS in production:
http.requiresChannel(c -> c.anyRequest().requiresSecure());
```

**A03 — Injection (SpEL injection):**
```java
// NEVER build SpEL expressions from user input:
// BAD:
String expression = "hasRole('" + userInputRole + "')"; // INJECTION RISK!
// GOOD: use fixed expressions, pass user data as method parameters
@PreAuthorize("hasRole('ADMIN') and #userId == authentication.name")
```

**A07 — Identification & Authentication Failures:**
```java
// Rate-limit login attempts:
@Component
public class LoginAttemptService {
    private final Cache<String, Integer> attemptsCache =
        CacheBuilder.newBuilder().expireAfterWrite(15, TimeUnit.MINUTES).build();

    public void loginFailed(String ip) {
        int attempts = attemptsCache.getOrDefault(ip, 0);
        attemptsCache.put(ip, attempts + 1);
    }

    public boolean isBlocked(String ip) {
        return attemptsCache.getOrDefault(ip, 0) >= 5;
    }
}
```

**A09 — Security Logging & Monitoring:**
```java
@Component
public class SecurityEventListener {

    @EventListener
    public void onAuthenticationSuccess(AuthenticationSuccessEvent event) {
        log.info("LOGIN_SUCCESS user={} ip={}", event.getAuthentication().getName(),
            getClientIp());
    }

    @EventListener
    public void onAuthenticationFailure(AbstractAuthenticationFailureEvent event) {
        log.warn("LOGIN_FAILURE user={} reason={}", event.getAuthentication().getName(),
            event.getException().getMessage());
        loginAttemptService.loginFailed(getClientIp());
    }
}
```

---

### 33. What are the security implications of using `@EnableGlobalMethodSecurity` vs `@EnableMethodSecurity` and how do you migrate?

**A:** `@EnableGlobalMethodSecurity` is deprecated since Spring Security 5.6. `@EnableMethodSecurity` is the replacement with several important differences:

| Feature | `@EnableGlobalMethodSecurity` | `@EnableMethodSecurity` |
|---|---|---|
| Status | Deprecated (removed in Spring Security 7) | Current standard |
| Default for `@PreAuthorize` | Requires `prePostEnabled=true` | ✅ Enabled by default |
| Authorization model | Old `AccessDecisionManager` | New `AuthorizationManager` |
| SpEL evaluation | `MethodSecurityExpressionHandler` | Same but cleaner |
| `@Secured` | Requires `securedEnabled=true` | `@EnableMethodSecurity(securedEnabled=true)` |
| JSR-250 (`@RolesAllowed`) | Requires `jsr250Enabled=true` | `@EnableMethodSecurity(jsr250Enabled=true)` |

**Migration:**
```java
// BEFORE (deprecated):
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true, securedEnabled = true)
public class OldMethodSecurityConfig extends GlobalMethodSecurityConfiguration {
    @Override
    protected MethodSecurityExpressionHandler createExpressionHandler() {
        // custom handler
    }
}

// AFTER (Spring Security 6+):
@Configuration
@EnableMethodSecurity(securedEnabled = true, jsr250Enabled = true)
public class MethodSecurityConfig {

    // Custom expression handler as a bean (auto-detected):
    @Bean
    public MethodSecurityExpressionHandler methodSecurityExpressionHandler(
            RoleHierarchy roleHierarchy) {
        DefaultMethodSecurityExpressionHandler handler =
            new DefaultMethodSecurityExpressionHandler();
        handler.setRoleHierarchy(roleHierarchy);
        return handler;
    }
}
```

**Role hierarchy (bonus — works with both):**
```java
@Bean
public RoleHierarchy roleHierarchy() {
    RoleHierarchyImpl hierarchy = new RoleHierarchyImpl();
    hierarchy.setHierarchy("""
        ROLE_SUPER_ADMIN > ROLE_ADMIN
        ROLE_ADMIN > ROLE_MANAGER
        ROLE_MANAGER > ROLE_USER
        """);
    return hierarchy;
}
// Now ROLE_ADMIN automatically has all ROLE_MANAGER and ROLE_USER permissions
```

---

### 34. How would you design a security architecture for a system that must support both browser clients (session/CSRF) and mobile/API clients (JWT) simultaneously?

**A:** Use multiple `SecurityFilterChain` beans with different `requestMatchers` and different authentication mechanisms. Spring Security 6 supports this natively.

```java
@Configuration
@EnableWebSecurity
public class MultiChainSecurityConfig {

    // Chain 1: REST API — stateless, JWT, no CSRF
    @Bean
    @Order(1)
    public SecurityFilterChain apiSecurityFilterChain(HttpSecurity http,
                                                       JwtAuthenticationFilter jwtFilter)
            throws Exception {
        http
            .securityMatcher("/api/**")           // applies only to /api/** paths
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.POST, "/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED))
                .accessDeniedHandler(new ApiAccessDeniedHandler())
            );
        return http.build();
    }

    // Chain 2: Browser app — session, CSRF enabled, form login
    @Bean
    @Order(2)
    public SecurityFilterChain browserSecurityFilterChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/**")               // catch-all for remaining paths
            .csrf(Customizer.withDefaults())
            .sessionManagement(s -> s
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(3)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login", "/register", "/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
            )
            .rememberMe(Customizer.withDefaults());
        return http.build();
    }
}
```

**Shared `AuthenticationManager`:**
```java
@Bean
public AuthenticationManager sharedAuthenticationManager(
        UserDetailsService userDetailsService,
        PasswordEncoder passwordEncoder) {
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(userDetailsService);
    provider.setPasswordEncoder(passwordEncoder);
    return new ProviderManager(provider);
}
```

This architecture cleanly separates concerns:
- Browser clients get CSRF protection, sessions, and cookie-based auth
- API/mobile clients get stateless JWT validation
- Both share the same user store and authorization rules

---

*File generated for the Java Learning repository. Spring Security version: 6.x (Spring Boot 3.x).*
