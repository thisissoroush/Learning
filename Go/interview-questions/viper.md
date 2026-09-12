# 🌿 Viper — Configuration Management in Go — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is Viper and why is it used in Go?

**A:** Viper is the most popular configuration library for Go. It reads config from multiple sources with a clear priority order:

```
Priority (highest → lowest):
1. Explicit Set() calls
2. Flags (pflag)
3. Environment variables
4. Config file (YAML/JSON/TOML/HCL/INI)
5. Remote config (etcd/Consul)
6. Default values
```

**Why Viper over plain `os.Getenv`:**
- Unified API for all config sources
- Automatic type casting (`GetInt`, `GetDuration`, `GetStringSlice`)
- Nested key support (`database.host`)
- Hot reload (watch config file for changes)
- Works with 12-factor app and Kubernetes ConfigMaps

---

### 2. How do you set up a basic Viper configuration?

**A:**

```go
import "github.com/spf13/viper"

func LoadConfig() error {
    // Set defaults
    viper.SetDefault("server.port", 8080)
    viper.SetDefault("server.timeout", "30s")
    viper.SetDefault("database.max_connections", 25)
    viper.SetDefault("log.level", "info")

    // Config file
    viper.SetConfigName("config")        // config.yaml, config.json, etc.
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")            // current directory
    viper.AddConfigPath("$HOME/.myapp")
    viper.AddConfigPath("/etc/myapp/")

    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return fmt.Errorf("read config: %w", err)
        }
        // Config file not found — use defaults + env vars
    }

    // Env vars override config file
    viper.AutomaticEnv()
    viper.SetEnvPrefix("MYAPP") // MYAPP_SERVER_PORT → server.port
    viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_")) // server.port → SERVER_PORT

    return nil
}
```

---

### 3. How do you read config values from Viper?

**A:**

```go
// Typed getters
port := viper.GetInt("server.port")                  // 8080
timeout := viper.GetDuration("server.timeout")       // 30s
dsn := viper.GetString("database.dsn")
debug := viper.GetBool("app.debug")
tags := viper.GetStringSlice("app.tags")             // ["web", "api"]
limits := viper.GetStringMapString("rate.limits")    // map[string]string

// Check if set
if viper.IsSet("feature.new_checkout") {
    // ...
}

// All keys
keys := viper.AllKeys() // ["server.port", "database.dsn", ...]

// Sub-tree
dbViper := viper.Sub("database") // returns a Viper scoped to "database"
dbViper.GetString("host")        // equivalent to viper.GetString("database.host")
```

---

### 4. How do you bind config to a struct?

**A:**

```go
type Config struct {
    Server struct {
        Port    int           `mapstructure:"port"`
        Timeout time.Duration `mapstructure:"timeout"`
        Host    string        `mapstructure:"host"`
    } `mapstructure:"server"`
    Database struct {
        DSN            string `mapstructure:"dsn"`
        MaxConnections int    `mapstructure:"max_connections"`
        MaxIdleConns   int    `mapstructure:"max_idle_conns"`
    } `mapstructure:"database"`
    Log struct {
        Level  string `mapstructure:"level"`
        Format string `mapstructure:"format"`
    } `mapstructure:"log"`
}

func LoadConfig() (Config, error) {
    // ... viper setup ...

    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return Config{}, fmt.Errorf("unmarshal config: %w", err)
    }
    return cfg, nil
}

// Usage
cfg, err := LoadConfig()
db, _ := sql.Open("postgres", cfg.Database.DSN)
srv := &http.Server{Addr: fmt.Sprintf(":%d", cfg.Server.Port)}
```

---

### 5. How do you use a config YAML file with Viper?

**A:**

```yaml
# config.yaml
server:
  port: 8080
  host: "0.0.0.0"
  timeout: "30s"

database:
  dsn: "postgres://user:pass@localhost/mydb?sslmode=disable"
  max_connections: 25
  max_idle_conns: 10

log:
  level: "info"
  format: "json"

redis:
  url: "redis://localhost:6379"
  ttl: "5m"

feature:
  new_checkout: false
  max_items_per_cart: 100
```

```go
// Override specific values with environment variables
// MYAPP_SERVER_PORT=9090 MYAPP_LOG_LEVEL=debug ./myapp
```

---

## 🟡 Mid Level

---

### 6. How do you validate configuration after loading?

**A:**

```go
// Using go-playground/validator
type Config struct {
    Server struct {
        Port int    `mapstructure:"port" validate:"required,min=1,max=65535"`
        Host string `mapstructure:"host" validate:"required"`
    } `mapstructure:"server"`
    Database struct {
        DSN            string `mapstructure:"dsn"            validate:"required"`
        MaxConnections int    `mapstructure:"max_connections" validate:"min=1,max=1000"`
    } `mapstructure:"database"`
    JWTSecret string `mapstructure:"jwt_secret" validate:"required,min=32"`
}

func LoadConfig() (Config, error) {
    // ... viper setup ...

    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return Config{}, err
    }

    validate := validator.New()
    if err := validate.Struct(cfg); err != nil {
        return Config{}, fmt.Errorf("invalid config: %w", err)
    }

    return cfg, nil
}
```

---

### 7. How do you implement hot reload with Viper?

**A:**

```go
import "github.com/fsnotify/fsnotify"

func SetupConfigWatcher(onReload func(cfg Config)) {
    viper.WatchConfig()
    viper.OnConfigChange(func(e fsnotify.Event) {
        log.Printf("Config file changed: %s", e.Name)

        var newCfg Config
        if err := viper.Unmarshal(&newCfg); err != nil {
            log.Printf("Failed to reload config: %v", err)
            return
        }

        onReload(newCfg)
    })
}

// In main
var (
    cfg   Config
    cfgMu sync.RWMutex
)

cfg, _ = LoadConfig()

SetupConfigWatcher(func(newCfg Config) {
    cfgMu.Lock()
    cfg = newCfg
    cfgMu.Unlock()
    log.Println("Config reloaded")
})

// Access config safely
func getLogLevel() string {
    cfgMu.RLock()
    defer cfgMu.RUnlock()
    return cfg.Log.Level
}
```

---

### 8. How do you handle multiple environments (dev/staging/prod)?

**A:**

```go
// Environment-specific config files
func LoadConfig(env string) error {
    viper.SetDefault("app.env", "development")

    // Base config
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath("./config")
    viper.ReadInConfig()

    // Override with environment-specific config
    viper.SetConfigName("config." + env)
    viper.MergeInConfig() // merge, not replace

    // Environment variables always win
    viper.AutomaticEnv()
    viper.SetEnvPrefix("APP")

    return nil
}

// config/
// ├── config.yaml         # base (committed)
// ├── config.development.yaml
// ├── config.staging.yaml
// └── config.production.yaml  # no secrets — only structure

// config/config.production.yaml (no secrets here)
// database:
//   max_connections: 100  # production pool size
// log:
//   level: "warn"         # less verbose in prod
// feature:
//   new_checkout: true

// Secrets come from environment variables, not files:
// APP_DATABASE_DSN=postgres://... APP_JWT_SECRET=... ./myapp
```

---

### 9. How do you use Viper with Cobra CLI flags?

**A:**

```go
import (
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
    Use: "myapp",
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := LoadConfig()
        return run(cfg)
    },
}

func init() {
    // Define flags
    rootCmd.PersistentFlags().String("config", "", "config file path")
    rootCmd.PersistentFlags().Int("port", 8080, "server port")
    rootCmd.PersistentFlags().String("log-level", "info", "log level")

    // Bind flags to Viper — flags override config file
    viper.BindPFlag("server.port", rootCmd.PersistentFlags().Lookup("port"))
    viper.BindPFlag("log.level", rootCmd.PersistentFlags().Lookup("log-level"))

    // Config file flag
    cobra.OnInitialize(func() {
        cfgFile, _ := rootCmd.PersistentFlags().GetString("config")
        if cfgFile != "" {
            viper.SetConfigFile(cfgFile)
        }
        viper.ReadInConfig()
    })
}

// Run: ./myapp --port=9090 --log-level=debug
// or:  PORT=9090 ./myapp
// or:  config.yaml with server.port: 9090
```

---

### 10. How do you load remote configuration from etcd or Consul?

**A:**

```go
import (
    "github.com/spf13/viper"
    _ "github.com/spf13/viper/remote"
    _ "github.com/go-etcd/etcd/v3" // register etcd provider
)

func LoadRemoteConfig() error {
    // etcd
    viper.AddRemoteProvider("etcd3", "http://127.0.0.1:2379", "/config/myapp")
    viper.SetConfigType("yaml")

    if err := viper.ReadRemoteConfig(); err != nil {
        return err
    }

    // Watch for changes
    go func() {
        for {
            time.Sleep(5 * time.Second)
            if err := viper.WatchRemoteConfig(); err != nil {
                log.Printf("remote config watch error: %v", err)
            }
        }
    }()

    return nil
}

// Consul
viper.AddRemoteProvider("consul", "localhost:8500", "MY_FEATURE_FLAGS")
```

---

## 🔴 Senior Level

---

### 11. How do you design a robust config package for a large Go service?

**A:**

```go
// config/config.go — single source of truth
package config

type Config struct {
    App      AppConfig
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
    Kafka    KafkaConfig
    Auth     AuthConfig
    Observability ObservabilityConfig
}

type ServerConfig struct {
    Port            int           `mapstructure:"port"`
    ReadTimeout     time.Duration `mapstructure:"read_timeout"`
    WriteTimeout    time.Duration `mapstructure:"write_timeout"`
    ShutdownTimeout time.Duration `mapstructure:"shutdown_timeout"`
}

// Load is the single entry point
func Load() (Config, error) {
    v := viper.New()
    setDefaults(v)
    bindEnvVars(v)
    if err := readConfigFile(v); err != nil {
        return Config{}, err
    }

    var cfg Config
    if err := v.Unmarshal(&cfg, viper.DecodeHook(
        mapstructure.ComposeDecodeHookFunc(
            mapstructure.StringToTimeDurationHookFunc(),
            mapstructure.StringToSliceHookFunc(","),
        ),
    )); err != nil {
        return Config{}, fmt.Errorf("unmarshal: %w", err)
    }

    if err := cfg.Validate(); err != nil {
        return Config{}, fmt.Errorf("invalid config: %w", err)
    }

    return cfg, nil
}

func (c Config) Validate() error {
    // Fail fast with a clear error message
    if c.Auth.JWTSecret == "" || len(c.Auth.JWTSecret) < 32 {
        return errors.New("auth.jwt_secret must be at least 32 characters")
    }
    if c.Database.DSN == "" {
        return errors.New("database.dsn is required")
    }
    return nil
}
```

---

### 12. How do you manage secrets with Viper in production?

**A:** Never store secrets in config files committed to source control. Instead:

```go
// Secrets strategy:
// 1. Kubernetes Secrets → mounted as env vars or files
// 2. HashiCorp Vault → fetched at startup
// 3. AWS Secrets Manager / Azure Key Vault → SDK at startup
// 4. Docker secrets → files at known paths

// Example: Vault integration
func loadSecretsFromVault(cfg *Config) error {
    client, err := api.NewClient(api.DefaultConfig())
    if err != nil { return err }
    client.SetToken(os.Getenv("VAULT_TOKEN"))

    secret, err := client.Logical().Read("secret/myapp/production")
    if err != nil { return err }

    cfg.Database.DSN = secret.Data["database_dsn"].(string)
    cfg.Auth.JWTSecret = secret.Data["jwt_secret"].(string)
    return nil
}

// Example: AWS Secrets Manager
func loadSecretsFromAWS(cfg *Config) error {
    svc := secretsmanager.New(session.Must(session.NewSession()))
    result, err := svc.GetSecretValue(&secretsmanager.GetSecretValueInput{
        SecretId: aws.String("myapp/production"),
    })
    if err != nil { return err }

    var secrets map[string]string
    json.Unmarshal([]byte(*result.SecretString), &secrets)
    cfg.Database.DSN = secrets["DATABASE_DSN"]
    return nil
}
```

**Config file (committed):** Structure, non-sensitive defaults.
**Environment variables:** Per-deployment settings (port, log level).
**Secrets manager:** Credentials, API keys, signing secrets.

---

## 🏛️ Architect Level

---

### 13. How do you design a feature flag system on top of Viper?

**A:**

```go
type FeatureFlags struct {
    NewCheckout       bool    `mapstructure:"new_checkout"`
    MaxCartItems      int     `mapstructure:"max_cart_items"`
    CheckoutV2Rollout float64 `mapstructure:"checkout_v2_rollout"` // 0.0-1.0
}

type Config struct {
    Features FeatureFlags `mapstructure:"features"`
    // ...
}

// Reload on config file change (Kubernetes ConfigMap watch)
type FeatureService struct {
    mu       sync.RWMutex
    features FeatureFlags
}

func (s *FeatureService) IsNewCheckoutEnabled() bool {
    s.mu.RLock()
    defer s.mu.RUnlock()
    return s.features.NewCheckout
}

func (s *FeatureService) IsRolledOut(feature string, userID string) bool {
    s.mu.RLock()
    defer s.mu.RUnlock()
    // Deterministic hash of userID → consistent experience per user
    h := fnv.New32a()
    h.Write([]byte(feature + userID))
    pct := float64(h.Sum32()%100) / 100.0
    return pct < s.features.CheckoutV2Rollout
}

// Kubernetes ConfigMap → mounted as file → Viper watches → hot reload
// No redeploy needed to change feature flags
```
