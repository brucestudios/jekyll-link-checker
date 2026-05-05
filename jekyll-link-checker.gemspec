Gem::Specification.new do |spec|
  spec.name          = "jekyll-link-checker"
  spec.version       = "0.1.0"
  spec.authors       = ["Bruce Fang"]
  spec.email         = ["henshao.fang@outlook.com"]

  spec.summary       = "A Jekyll plugin to check for broken links in your site."
  spec.description   = "This plugin scans generated HTML files for broken internal and external links, providing a report after each Jekyll build."
  spec.homepage      = "https://github.com/brucestudios/jekyll-link-checker"
  spec.license       = "MIT"

  spec.files         = Dir.chdir(File.expand_path('..', __dir__)) do
    `git ls-files -z`.split("\x0").reject { |f| f.match(%r{^(test|spec|features)/}) }
  end
  spec.bindir        = "exe"
  spec.executables   = spec.files.grep(%r{^exe/}) { |f| File.basename(f) }
  spec.require_paths = ["lib"]

  spec.add_dependency "jekyll", ">= 3.0", "< 5.0"
  spec.add_dependency "addressable", "~> 2.8"
  spec.add_dependency "public_suffix", "~> 5.0"
  spec.add_development_dependency "bundler", "~> 2.0"
  spec.add_development_dependency "rake", "~> 13.0"
end