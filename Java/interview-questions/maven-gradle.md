# 🔨 Maven & Gradle — Interview Questions (Junior → Architect)

---

## 🟢 Junior Level

---

### 1. What is Maven and what problem does it solve?

**A:** Maven is a build automation and dependency management tool for Java. It provides:
- **Dependency management** — declare dependencies, Maven downloads from repositories
- **Standardized project structure** — `src/main/java`, `src/test/java`, `target/`
- **Build lifecycle** — ordered phases: compile → test → package → install → deploy
- **Plugin ecosystem** — compile, test, package, deploy plugins

```xml
<!-- pom.xml — Project Object Model -->
<project>
    <groupId>com.mycompany</groupId>
    <artifactId>order-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

---

### 2. What are Maven dependency scopes?

**A:**

| Scope | Compile | Test | Runtime | Packaged |
|-------|---------|------|---------|----------|
| `compile` (default) | ✅ | ✅ | ✅ | ✅ |
| `test` | ❌ | ✅ | ❌ | ❌ |
| `runtime` | ❌ | ✅ | ✅ | ✅ |
| `provided` | ✅ | ✅ | ❌ | ❌ |
| `system` | ✅ | ✅ | ❌ | ❌ |

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <!-- compile scope — default -->
    </dependency>

    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope> <!-- not needed at compile time -->
    </dependency>

    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope> <!-- only in tests -->
    </dependency>

    <dependency>
        <groupId>javax.servlet</groupId>
        <artifactId>javax.servlet-api</artifactId>
        <scope>provided</scope> <!-- provided by app server, not packaged -->
    </dependency>
</dependencies>
```

---

### 3. What is the Maven build lifecycle?

**A:** Three built-in lifecycles; the default lifecycle has these key phases:

```bash
mvn validate     # validate project structure
mvn compile      # compile src/main/java → target/classes
mvn test         # run unit tests (src/test/java)
mvn package      # create JAR/WAR in target/
mvn verify       # run integration tests + checks
mvn install      # install to local ~/.m2 repository
mvn deploy       # push to remote repository

# Each phase executes all prior phases
mvn package      # runs: validate, compile, test, package

# Skip tests
mvn package -DskipTests
mvn package -Dmaven.test.skip=true  # skip compile too
```

---

### 4. What is Gradle and how does it differ from Maven?

**A:**

| | Maven | Gradle |
|--|-------|--------|
| Language | XML (pom.xml) | Groovy/Kotlin DSL (build.gradle/build.gradle.kts) |
| Performance | Slower | Faster (incremental, build cache, daemon) |
| Flexibility | Convention over config | Highly customizable |
| Syntax | Verbose XML | Concise DSL |
| Incremental builds | Limited | First-class |
| Build cache | No | Yes (local + remote) |

```kotlin
// build.gradle.kts (Kotlin DSL — preferred in modern projects)
plugins {
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
    kotlin("jvm") version "1.9.20"
}

group = "com.mycompany"
version = "1.0.0-SNAPSHOT"

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
    maxParallelForks = Runtime.getRuntime().availableProcessors()
}
```

---

### 5. How do you manage versions in Maven with a BOM?

**A:** A Bill of Materials (BOM) manages compatible dependency versions:

```xml
<dependencyManagement>
    <dependencies>
        <!-- Import Spring Cloud BOM — manages all Spring Cloud versions -->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>2023.0.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <!-- No version needed — managed by BOM -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-openfeign</artifactId>
    </dependency>
</dependencies>
```

---

## 🟡 Mid Level

---

### 6. How does Gradle incremental build work?

**A:** Gradle tracks task inputs and outputs — skips tasks where nothing changed:

```kotlin
// Gradle compares:
// - Input files (source files, classpath)
// - Input properties (compiler flags, version)
// - Output files (class files, JARs)

// If unchanged → task is UP-TO-DATE → skipped

// Build cache — reuse outputs from previous builds (even on CI)
org.gradle.caching=true  // gradle.properties

// Parallel execution
org.gradle.parallel=true
org.gradle.workers.max=4

// Daemon — reuses JVM across builds
org.gradle.daemon=true
org.gradle.jvmargs=-Xmx2g -XX:+UseG1GC

// Force re-run
./gradlew build --rerun-tasks
```

---

### 7. How do you define custom Gradle tasks?

**A:**

```kotlin
// Simple task
tasks.register("hello") {
    group = "custom"
    description = "Prints hello"
    doLast {
        println("Hello from Gradle!")
    }
}

// Task with inputs/outputs (incremental)
tasks.register<Copy>("copyConfig") {
    from("src/main/resources")
    into("build/config")
    include("*.yml")
}

// Task depending on another
tasks.register("buildAndDeploy") {
    dependsOn("build", "dockerBuild")
    doLast {
        exec { commandLine("kubectl", "apply", "-f", "k8s/") }
    }
}

// Custom task class
abstract class GenerateCode : DefaultTask() {
    @get:InputFile abstract val schemaFile: RegularFileProperty
    @get:OutputDirectory abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        val schema = schemaFile.get().asFile.readText()
        // generate code...
        outputDir.get().asFile.mkdirs()
    }
}

tasks.register<GenerateCode>("generateFromSchema") {
    schemaFile.set(file("schema/api.yaml"))
    outputDir.set(layout.buildDirectory.dir("generated"))
}
```

---

### 8. How do you handle multi-module projects in Maven and Gradle?

**A:**

**Maven multi-module:**
```xml
<!-- parent/pom.xml -->
<packaging>pom</packaging>
<modules>
    <module>common</module>
    <module>order-service</module>
    <module>inventory-service</module>
</modules>

<dependencyManagement>
    <dependencies>
        <!-- Shared version management -->
    </dependencies>
</dependencyManagement>

<!-- order-service/pom.xml -->
<parent>
    <artifactId>parent</artifactId>
    <groupId>com.myapp</groupId>
    <version>1.0.0</version>
</parent>

<dependencies>
    <dependency>
        <groupId>com.myapp</groupId>
        <artifactId>common</artifactId>
        <version>${project.version}</version>
    </dependency>
</dependencies>
```

**Gradle multi-project:**
```kotlin
// settings.gradle.kts
rootProject.name = "my-app"
include("common", "order-service", "inventory-service")

// order-service/build.gradle.kts
dependencies {
    implementation(project(":common")) // cross-project dependency
}

// Build all
./gradlew build         # all modules
./gradlew :order-service:test  # specific module
```

---

### 9. How do you configure Maven for a CI/CD pipeline?

**A:**

```xml
<!-- Maven Wrapper — reproducible builds (no Maven install needed) -->
<!-- generates: mvnw, mvnw.cmd, .mvn/wrapper/ -->
mvn wrapper:wrapper -Dmaven=3.9.5

<!-- settings.xml — CI credentials (not in pom.xml) -->
<settings>
    <servers>
        <server>
            <id>nexus-releases</id>
            <username>${env.NEXUS_USER}</username>
            <password>${env.NEXUS_PASS}</password>
        </server>
    </servers>
    <mirrors>
        <mirror>
            <id>nexus</id>
            <url>https://nexus.company.com/repository/maven-public/</url>
            <mirrorOf>*</mirrorOf>
        </mirror>
    </mirrors>
</settings>
```

```yaml
# GitHub Actions
- name: Build with Maven
  run: ./mvnw verify -B -q --no-transfer-progress
  env:
    NEXUS_USER: ${{ secrets.NEXUS_USER }}
    NEXUS_PASS: ${{ secrets.NEXUS_PASS }}

- name: Publish Test Report
  uses: dorny/test-reporter@v1
  with:
    pattern: '**/target/surefire-reports/*.xml'
```

---

### 10. How do you configure Gradle for a CI/CD pipeline?

**A:**

```kotlin
// gradle/wrapper/gradle-wrapper.properties — pin version
distributionUrl=https://services.gradle.org/distributions/gradle-8.5-bin.zip

// CI optimizations
org.gradle.daemon=false          // disable daemon in CI (avoid stale state)
org.gradle.caching=true          // use build cache
org.gradle.parallel=true
org.gradle.configureondemand=true // configure only needed subprojects
```

```yaml
# GitHub Actions with Gradle caching
- uses: gradle/gradle-build-action@v2
  with:
    gradle-version: wrapper    # use wrapper version

- name: Build
  run: ./gradlew build --scan   # generate build scan for analysis
```

---

## 🔴 Senior Level

---

### 11. How do you optimize Maven build performance?

**A:**

```bash
# Parallel builds (safe for most projects)
mvn -T 4 install              # 4 threads
mvn -T 1C install             # 1 thread per CPU core

# Offline mode after initial download
mvn -o package                # fail if dependency missing locally

# Profile-based builds
mvn verify -Pintegration-tests # enable integration test profile

# Skip expensive plugins
mvn package -DskipTests -Dcheckstyle.skip -Dspotbugs.skip

# Incremental compilation (compiler plugin)
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <useIncrementalCompilation>true</useIncrementalCompilation>
    </configuration>
</plugin>

# Maven Build Cache Extension (Maven 3.9+)
# .mvn/maven-build-cache-config.xml — cache task outputs
```

---

### 12. How do you create a custom Maven plugin?

**A:**

```java
@Mojo(name = "validate-schema", defaultPhase = LifecyclePhase.VALIDATE,
      requiresDependencyResolution = ResolutionScope.NONE)
public class SchemaValidationMojo extends AbstractMojo {

    @Parameter(defaultValue = "${project.basedir}/src/main/resources/schema", required = true)
    private File schemaDirectory;

    @Parameter(defaultValue = "false")
    private boolean failOnWarning;

    @Parameter(defaultValue = "${project}", readonly = true, required = true)
    private MavenProject project;

    @Override
    public void execute() throws MojoExecutionException {
        getLog().info("Validating schemas in: " + schemaDirectory);
        if (!schemaDirectory.exists()) {
            throw new MojoExecutionException("Schema directory not found: " + schemaDirectory);
        }
        // validation logic...
        getLog().info("Schema validation passed");
    }
}

// Usage in pom.xml:
// <plugin>
//     <groupId>com.mycompany</groupId>
//     <artifactId>schema-validation-plugin</artifactId>
//     <executions>
//         <execution>
//             <goals><goal>validate-schema</goal></goals>
//         </execution>
//     </executions>
// </plugin>
```

---

## 🏛️ Architect Level

---

### 13. How do you design a dependency management strategy for a large Java monorepo?

**A:**

```
mycompany/                         # monorepo root
├── platform/
│   ├── bom/pom.xml               # company-wide BOM — all version decisions
│   ├── parent/pom.xml            # build config: plugins, compiler, reports
│   └── common/pom.xml            # shared utilities
├── services/
│   ├── order-service/
│   ├── inventory-service/
│   └── payment-service/
└── libs/
    ├── domain-model/
    └── event-contracts/           # shared Kafka event schemas
```

```xml
<!-- platform/bom/pom.xml — single source of truth for versions -->
<dependencyManagement>
    <dependencies>
        <!-- All internal artifacts -->
        <dependency>
            <groupId>com.mycompany</groupId>
            <artifactId>common</artifactId>
            <version>${revision}</version>
        </dependency>
        <!-- All external versions pinned here -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.16.0</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

**Governance rules:**
- Only the BOM team updates external dependency versions
- All services import the company BOM — no version overrides without review
- OWASP dependency check in CI: `mvn org.owasp:dependency-check-maven:check`
- Renovate Bot / Dependabot for automated PR-based updates
- Semantic versioning + CHANGELOG for internal libraries

---

### 14. How do you manage secrets and environment-specific config in Maven/Gradle builds?

**A:**

```bash
# Maven — never commit credentials in pom.xml
# Settings.xml (per developer / CI environment)
# ~/.m2/settings.xml or /home/ci/.m2/settings.xml

# Environment variable injection
<server>
    <id>nexus</id>
    <username>${env.NEXUS_USER}</username>
    <password>${env.NEXUS_PASS}</password>
</server>

# Gradle — use gradle.properties (gitignored) for local secrets
# ~/.gradle/gradle.properties
nexusUser=developer1
nexusPass=secret123

# In build.gradle.kts
val nexusUser: String by project
val nexusPass: String by project

publishing {
    repositories {
        maven {
            credentials {
                username = System.getenv("NEXUS_USER") ?: nexusUser
                password = System.getenv("NEXUS_PASS") ?: nexusPass
            }
        }
    }
}
```

**Security:**
- GitGuardian / gitleaks in CI to catch secrets committed accidentally
- Vault integration for dynamic credentials: `vault read secret/nexus`
- Separate build-time secrets (repo credentials) from runtime secrets (DB passwords)
