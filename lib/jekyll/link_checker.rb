require "addressable/uri"
require "public_suffix"
require "fileutils"

module Jekyll
  module LinkChecker
    class BrokenLinkChecker < Jekyll::Generator
      safe true
      priority :low

      def generate(site)
        return unless site.config["link_checker"] && site.config["link_checker"]["enabled"]

        puts "LinkChecker: Checking for broken links..."
        broken_links = []

        site.pages.each do |page|
          next unless page.output_ext == ".html"
          next unless File.exist?(File.join(site.dest, page.url.sub(/^\//, "")))

          html = File.read(File.join(site.dest, page.url.sub(/^\//, "")))
          links = extract_links(html)

          links.each do |link|
            next if skip_link?(link)
            absolute_url = resolve_url(link, page.url, site)
            if broken?(absolute_url, site)
              broken_links << { page: page.url, link: link, resolved: absolute_url }
            end
          end
        end

        site.documents.each do |doc|
          next unless doc.output_ext == ".html"
          next unless File.exist?(File.join(site.dest, doc.url.sub(/^\//, "")))

          html = File.read(File.join(site.dest, doc.url.sub(/^\//, "")))
          links = extract_links(html)

          links.each do |link|
            next if skip_link?(link)
            absolute_url = resolve_url(link, doc.url, site)
            if broken?(absolute_url, site)
              broken_links << { page: doc.url, link: link, resolved: absolute_url }
            end
          end
        end

        unless broken_links.empty?
          puts "LinkChecker: Found #{broken_links.size} broken link#{broken_links.size == 1 ? "" : "s"}:"
          broken_links.each do |bl|
            puts "  - Page: #{bl[:page]}"
            puts "    Link: #{bl[:link]}"
            puts "    Resolved: #{bl[:resolved]}"
          end
        else
          puts "LinkChecker: No broken links found."
        end
      end

      private

      def extract_links(html)
        html.scan(/<a[^>]*href=["']([^"']*)["']/i).flatten
      end

      def skip_link?(link)
        link.nil? ||
          link.empty? ||
          link.start_with?("#") ||
          link.start_with?("mailto:") ||
          link.start_with?("javascript:") ||
          link.match?(/^data:/i)
      end

      def resolve_url(link, page_url, site)
        # If link is already absolute, return as is
        return link if link.match?(/^https?:\/\//i)

        # Get the directory of the page
        page_dir = File.dirname(page_url)
        page_dir = "." if page_dir == ""

        # Resolve relative to page directory
        resolved = File.join(page_dir, link)
        resolved = File.expand_path(resolved)

        # Make it relative to site root (removing any leading ./ or ../ that are now absolute)
        resolved = Pathname.new(resolved).relative_path_from(Pathname.new(site.source)).to_s

        # Prepend baseurl if configured
        baseurl = site.config["baseurl"] || ""
        baseurl = "" if baseurl == "/"
        File.join(baseurl, resolved)
      end

      def broken?(url, site)
        begin
          uri = Addressable::URI.parse(url)
          return true unless uri && uri.scheme && uri.host

          # Check if scheme is http or https
          return true unless %w(http https).include?(uri.scheme.downcase)

          # Validate domain using PublicSuffix
          domain = uri.host
          return true unless PublicSuffix.valid?(domain)

          # For relative links (those without scheme), we already handled in resolve_url
          # But if we get here, it's an absolute http/https link with valid domain.
          # We do not check reachability to avoid network calls.
          false
        rescue
          true
        end
      end
    end
  end
end