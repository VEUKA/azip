# azip

Download Azure IP ranges JSON from Microsoft.

## Quick Start

### Using uvx (no installation)

```bash
uvx --from git+https://github.com/VEUKA/azip azip get
```

### Using uv (local install)

```bash
# Clone and install
git clone https://github.com/VEUKA/azip.git
cd azip
uv sync

# Run
uv run azip get

# Or with custom filename
uv run azip get -f azure-ips.json
```

## How It Works

The tool automatically finds the JSON download link by:

1. **Fetching the Microsoft download page** (`details.aspx?id=56519`)
2. **Parsing the HTML** with BeautifulSoup
3. **Searching for links** containing `.json` in the href attribute
4. **Preferring exact matches** (links ending with `.json`)
5. **Downloading the file** with a progress bar

No browser automation required—just lightweight HTTP requests and HTML parsing.

## Using in CI/CD

Perfect for automated workflows! No installation needed with `uvx`:

```yaml
# .github/workflows/your-workflow.yml
- name: Install uv
  uses: astral-sh/setup-uv@v5

- name: Download Azure IP ranges
  run: uvx --from git+https://github.com/VEUKA/azip azip get --filename azure-ips.json
```

**See it in action:** [`.github/workflows/demo-download.yml`](.github/workflows/demo-download.yml)

Works with any CI/CD platform (GitHub Actions, GitLab CI, Jenkins, etc.)!

## Output Example

```log
🌐 Opening download page...
   https://www.microsoft.com/en-us/download/details.aspx?id=56519
✓ Page loaded successfully
🔍 Searching for JSON download link...
✓ Found JSON file: ServiceTags_Public_20251013.json
   https://download.microsoft.com/download/...
📥 Downloading file...
   ServiceTags_Public_20251013.json ━━━━━━━━ 4.1/4.1 MB 14.9 MB/s 0:00:00
✓ Download complete: ServiceTags_Public_20251013.json
   File size: 4.1 MB
```
