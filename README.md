# Jekyll Link Checker

A simple, fast link checker for Jekyll (and other static) sites. It scans your generated site for broken internal and external links.

## Features

- Checks internal links (relative and absolute within the site)
- Checks external links (HTTP/HTTPS)
- Ignores links to anchors on the same page (optional)
- Configurable timeout and user agent
- Outputs results in a clear, actionable format
- Can be used as a command-line tool or imported as a Python module

## Installation

```bash
pip install jekyll-link-checker
```

Or clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/jekyll-link-checker.git
cd jekyll-link-checker
pip install -e .
```

## Usage

### Command Line

After building your Jekyll site (usually in `_site`), run:

```bash
jekyll-link-checker _site
```

Options:

- `--ignore-anchors`: Ignore links that point to anchors on the same page (e.g., `#section`)
- `--timeout SECONDS`: Set timeout for external requests (default: 10)
- `--user-agent STRING`: Set custom user agent for external requests
- `--external`: Also check external links (enabled by default, use `--no-external` to skip)
- `--internal`: Also check internal links (enabled by default, use `--no-internal` to skip)
- `--verbose`: Show progress and details

### As a Library

```python
from jekyll_link_checker import LinkChecker

checker = LinkChecker(base_url="https://example.com")
broken = checker.check_site("_site")
if broken:
    print("Broken links found:")
    for link, error in broken.items():
        print(f"  {link}: {error}")
else:
    print("No broken links found!")
```

## Configuration

You can also configure the checker via a `.jekyll-link-checker` file in YAML format:

```yaml
timeout: 15
user_agent: "MySite LinkChecker/1.0"
ignore_anchors: true
check_external: true
check_internal: true
```

## Why This Tool?

- Jekyll sites can accumulate broken links over time, especially when linking to external resources.
- This tool is lightweight, has minimal dependencies, and focuses on doing one thing well.
- It integrates easily into your site's build process or CI pipeline.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need to maintain a personal Jekyll blog without broken links.
- Uses the excellent `requests` and `beautifulsoup4` libraries.