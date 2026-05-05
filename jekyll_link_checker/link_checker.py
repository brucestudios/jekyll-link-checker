import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class LinkChecker:
    def __init__(self, base_url="", timeout=10, user_agent=None, 
                 check_external=True, check_internal=True, ignore_anchors=False):
        """
        Initialize the link checker.

        :param base_url: The base URL of the site (for resolving relative links)
        :param timeout: Timeout for external requests in seconds
        :param user_agent: User agent string for external requests
        :param check_external: Whether to check external links
        :param check_internal: Whether to check internal links
        :param ignore_anchors: Whether to ignore links that point to anchors on the same page
        """
        self.base_url = base_url
        self.timeout = timeout
        self.user_agent = user_agent or "JekyllLinkChecker/0.1"
        self.check_external = check_external
        self.check_internal = check_internal
        self.ignore_anchors = ignore_anchors
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def _is_external(self, url):
        """Check if a URL is external (has a different domain than base_url)."""
        if not self.base_url:
            return False
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        return bool(url_domain and url_domain != base_domain)

    def _normalize_url(self, url, page_url):
        """Normalize a URL relative to a page URL."""
        if not url:
            return None
        # Handle anchor links
        if url.startswith('#'):
            if self.ignore_anchors:
                return None
            return urljoin(page_url, url)
        # Handle relative URLs
        if not urlparse(url).netloc:
            return urljoin(page_url, url)
        return url

    def check_link(self, url, page_url):
        """
        Check a single link.

        :param url: The link URL as found in the HTML
        :param page_url: The URL of the page containing the link
        :return: None if the link is okay, or an error string if broken
        """
        normalized_url = self._normalize_url(url, page_url)
        if normalized_url is None:
            return None  # Ignored (e.g., anchor)

        # Skip if we are not checking this type of link
        if self._is_external(normalized_url):
            if not self.check_external:
                return None
        else:
            if not self.check_internal:
                return None

        try:
            # For internal links, we check the file system if base_url is not set or is a file path?
            # Since we are checking a generated site, we assume the site is built and we can check via HTTP
            # But if the site is built locally, we might want to check file existence.
            # However, for simplicity, we'll check via HTTP for both internal and external.
            # If the site is served locally, we can set base_url to the local URL (e.g., http://localhost:4000)
            response = self.session.get(normalized_url, timeout=self.timeout, allow_redirects=True)
            if response.status_code >= 400:
                return f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return str(e)
        return None

    def check_page(self, page_path):
        """
        Check all links in a single HTML file.

        :param page_path: Path to the HTML file
        :return: Dictionary of broken links (link -> error) for this page
        """
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
        except Exception as e:
            return {f"Error reading file {page_path}": str(e)}

        # Get the directory of the page to resolve relative links
        page_dir = os.path.dirname(os.path.abspath(page_path))
        # We'll assume the page can be accessed via base_url + relative path from site root
        # For simplicity, we'll use the file path to construct a URL if base_url is set.
        # Alternatively, we can require the user to set base_url to the site's URL.
        # We'll compute the page URL relative to the site root if base_url is provided.
        page_url = None
        if self.base_url:
            # Try to get the relative path from the site root (assuming the site is built in _site)
            # This is a simplification; in reality, you might need to configure the site root.
            # We'll assume the page_path is relative to the current directory and the site root is the current directory.
            # So the page URL is base_url + the relative path from the current directory to the page.
            rel_path = os.path.relpath(page_path, start=os.getcwd())
            page_url = urljoin(self.base_url, rel_path.replace(os.sep, '/'))

        broken = {}
        for tag in soup.find_all(['a', 'link', 'img', 'script']):
            # Extract the URL from the appropriate attribute
            if tag.name == 'a' or tag.name == 'link':
                url = tag.get('href')
            elif tag.name == 'img' or tag.name == 'script':
                url = tag.get('src')
            else:
                continue

            if url is None:
                continue

            error = self.check_link(url, page_url or page_path)
            if error:
                broken[url] = error

        return broken

    def check_site(self, site_dir):
        """
        Check all HTML files in a directory (recursively).

        :param site_dir: Path to the generated site directory (e.g., _site)
        :return: Dictionary of broken links (link -> error) for the entire site
        """
        broken_links = {}
        for root, dirs, files in os.walk(site_dir):
            for file in files:
                if file.endswith('.html') or file.endswith('.htm'):
                    page_path = os.path.join(root, file)
                    broken = self.check_page(page_path)
                    for link, error in broken.items():
                        # Use the page path and link as key to avoid overwriting same link on different pages
                        key = f"{page_path}:{link}"
                        broken_links[key] = error
        return broken_links

def main():
    parser = argparse.ArgumentParser(description='Check links in a Jekyll (static) site.')
    parser.add_argument('site_dir', help='Path to the generated site directory (e.g., _site)')
    parser.add_argument('--base-url', help='Base URL of the site (for resolving relative links)', default='')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout for external requests in seconds')
    parser.add_argument('--user-agent', help='User agent string for external requests')
    parser.add_argument('--no-external', dest='check_external', action='store_false', 
                        help='Skip checking external links')
    parser.add_argument('--no-internal', dest='check_internal', action='store_false', 
                        help='Skip checking internal links')
    parser.add_argument('--ignore-anchors', action='store_true', 
                        help='Ignore links that point to anchors on the same page')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    checker = LinkChecker(
        base_url=args.base_url,
        timeout=args.timeout,
        user_agent=args.user_agent,
        check_external=args.check_external,
        check_internal=args.check_internal,
        ignore_anchors=args.ignore_anchors
    )

    if args.verbose:
        print(f"Checking site in {args.site_dir}")
        print(f"Base URL: {args.base_url or '(not set)'}")
        print(f"Timeout: {args.timeout}s")
        print(f"User Agent: {checker.user_agent}")
        print(f"Check external: {args.check_external}")
        print(f"Check internal: {args.check_internal}")
        print(f"Ignore anchors: {args.ignore_anchors}")
        print("-" * 50)

    broken = checker.check_site(args.site_dir)

    if broken:
        print(f"Found {len(broken)} broken link(s):")
        for link, error in broken.items():
            print(f"  {link}: {error}")
        sys.exit(1)
    else:
        print("No broken links found!")
        sys.exit(0)

if __name__ == '__main__':
    main()