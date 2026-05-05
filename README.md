# Jekyll Link Checker

A Jekyll plugin to check for broken links in your site.

## Installation

Add this line to your Jekyll site's `Gemfile`:

```ruby
gem "jekyll-link-checker"
```

And then execute:

    $ bundle

Or install it yourself as:

    $ gem install jekyll-link-checker

## Usage

Enable the plugin in your Jekyll site's `_config.yml`:

```yaml
plugins:
  - jekyll-link-checker

link_checker:
  enabled: true
```

The plugin will run after each Jekyll build and report any broken links found in the generated HTML files.

## Configuration

You can disable the link checker by setting `enabled` to `false` in the `link_checker` section of `_config.yml`.

## How it works

The plugin scans all generated HTML files (pages and posts) for anchor tags (`<a>`) and extracts the `href` attribute.
It then checks each link for:
- Validity (not empty, not a fragment, not a mailto:, not javascript:, not a data URI)
- Whether the URL is absolute and uses http or https scheme
- Whether the host has a valid domain suffix (using the PublicSuffix list)

Note: This plugin does not perform actual HTTP requests to check if the link is reachable. It only validates the URL format and domain.

## Development

After checking out the repo, run `bin/setup` to install dependencies. You can also run `rake spec` to run the tests.

To install this gem onto your local machine, run `bundle exec rake install`.

To release a new version, update the version number in `version.rb`, and then run `bundle exec rake release`, which will create a git tag for the version, push git commits and tags, and push the `.gem` file to [rubygems.org](https://rubygems.org).

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/brucestudios/jekyll-link-checker.

## License

The gem is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).