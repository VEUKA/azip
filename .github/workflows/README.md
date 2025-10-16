# GitHub Actions Workflows

This project includes CI/CD workflows for testing and demonstrating usage:

## Testing Workflows

### 1. Unit Tests (`test-unit.yml`)

**Purpose:** Fast feedback on code changes with unit tests only (excludes E2E tests).

**Triggers:**
- ✅ Push to `main` branch
- ✅ Pull requests to `main` branch
- ✅ Manual dispatch (on-demand)

**What it does:**
- Runs all tests except E2E tests (`pytest -m "not e2e"`)
- Generates coverage report
- Runs mypy type checking

**Duration:** ~1-2 minutes

---

## 2. E2E Tests (`test-e2e.yml`)

**Purpose:** Run end-to-end tests that make real HTTP requests to Microsoft's servers.

**Triggers:**
- ✅ Manual dispatch only (on-demand)

**What it does:**
- Runs only E2E tests (`pytest -m e2e`)
- Uploads test artifacts on failure for debugging

**Duration:** ~30-60 seconds (network dependent)

**Note:** These tests make real HTTP requests and may be affected by external service availability.

---

## 3. Full Test Suite (`test-full.yml`)

**Purpose:** Comprehensive testing including all unit tests and E2E tests.

**Triggers:**
- ✅ Manual dispatch (on-demand)
- ✅ Scheduled: Every Monday at 9:00 AM UTC

**What it does:**
- Runs all tests including E2E
- Generates detailed coverage report (HTML)
- Runs mypy type checking
- Uploads coverage report artifact (retained for 30 days)

**Duration:** ~2-3 minutes

---

## Demo Workflow

### 4. Demo - Download Azure IPs (`demo-download.yml`)

**Purpose:** Demonstrates how easy it is to use `azip` in any CI/CD environment with `uvx`.

**Triggers:**
- ✅ Manual dispatch (on-demand)
- ✅ Scheduled: Daily at 2:00 AM UTC

**What it does:**
- Downloads Azure IP ranges using `uvx` (no installation!)
- Verifies the download
- Extracts statistics (change number, cloud, service count)
- Uploads the JSON file as an artifact

**Duration:** ~30 seconds

**Key command:**
```bash
uvx --from git+https://github.com/VEUKA/azip azip get --filename azure-ips.json
```

**Perfect for:** Showing how to integrate `azip` into any CI/CD pipeline without pre-installation.

---

## Running Workflows Manually

### From GitHub UI:
1. Go to **Actions** tab
2. Select the workflow you want to run
3. Click **Run workflow** button
4. Choose the branch
5. Click **Run workflow**

### From GitHub CLI:
```bash
# Run unit tests
gh workflow run test-unit.yml

# Run E2E tests
gh workflow run test-e2e.yml

# Run full test suite
gh workflow run test-full.yml
```

---

## Workflow Strategy

- **Fast feedback:** Unit tests run on every PR/push for quick validation
- **On-demand E2E:** E2E tests can be triggered manually before releases
- **Weekly comprehensive check:** Full suite runs weekly to catch integration issues

This approach balances speed (fast unit tests) with thoroughness (E2E tests when needed).
