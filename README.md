# 🔍 EnvLens

**Full-stack environment variable contract scanner** — catch missing, ghost, and drifted env vars before deployment blows up.

EnvLens scans your source code and every layer of deployment config (`.env`, Docker Compose, Kubernetes, GitHub Actions) to find inconsistencies.

## 🚀 Quick Start

```bash
pip install -r requirements.txt

# Scan current project
python envlens.py .

# JSON output for scripting
python envlens.py . --format json

# Fail CI if missing vars detected
python envlens.py . --fail-on-missing
```

### Example Output
```
EnvLens Report | Source: 5 | Config: 4
✅ Matched: 3  ❌ Missing: 2  👻 Ghost: 1

❌ MISSING (in code, not in config):
  STRIPE_KEY  ← src/billing.py
  REDIS_URL   ← src/cache.ts

👻 GHOST (in config, not in code):
  OLD_API_KEY  ← .env.production

✅ MATCHED: DATABASE_URL, PORT, SECRET_KEY
```

## 🔧 Supported Sources & Configs

| Source Languages | Config Formats |
|-----------------|----------------|
| Python (`os.getenv`) | `.env` / `.env.*` files |
| Node.js (`process.env`) | `docker-compose.yml` |
| Go (`os.Getenv`) | Kubernetes manifests |
| Java (`System.getenv`) | GitHub Actions workflows |
| Ruby, PHP, Rust, Shell | Any YAML with `environment:` |

## 📊 Why Pay for EnvLens?

**The average env var misconfiguration causes 2-4 hours of debugging** and costs $500+ in developer time. Teams with 50+ env vars across staging/production see config drift weekly.

EnvLens catches these issues in seconds, in CI, before they hit production.

## 💰 Pricing

| Feature | Free | Pro $19/mo | Enterprise $99/mo |
|---------|:----:|:----------:|:-----------------:|
| Source code scanning (6 langs) | ✅ | ✅ | ✅ |
| `.env` file scanning | ✅ | ✅ | ✅ |
| Docker/K8s YAML scanning | ✅ | ✅ | ✅ |
| Table & JSON output | ✅ | ✅ | ✅ |
| SARIF output (GitHub Security) | ❌ | ✅ | ✅ |
| `--fail-on-missing` CI gate | ❌ | ✅ | ✅ |
| Terraform `.tf` scanning | ❌ | ✅ | ✅ |
| Monorepo multi-root scan | ❌ | ✅ | ✅ |
| Slack/webhook notifications | ❌ | ❌ | ✅ |
| Custom naming rules | ❌ | ❌ | ✅ |
| Priority support & SLA | ❌ | ❌ | ✅ |

## 🏗️ CI Integration

```yaml
# .github/workflows/envlens.yml
- name: EnvLens Check
  run: python envlens.py . --fail-on-missing --format json
```

## License

BSL 1.1 — Free for teams ≤5. Commercial license required for larger teams.
