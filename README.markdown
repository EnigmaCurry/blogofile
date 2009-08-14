Blogofile is a simple blog engine that requires no database and no special hosting environment. You customize a set of templates with Mako, create posts in a markup language like Textile, or Markdown, (or even plain HTML) and Blogofile generates your entire blog as plain HTML, CSS, images, and Atom/RSS feeds which you can then upload to any old web server you like. No CGI or scripting environment is needed on the server.

See the [main blogofile website](http://www.blogofile.com) for usage instructions.

# Org Branch Changelog

- Org branch : support orgmode of emacs as markup language
  - Todo : latex fragment, image, syntax highligting
- set pygments default encoding 'utf-8' for processing unicode
- For the py25 compatibility, advanced string formatting is changed to the original version
- Fix a bug : article without yaml header is not properly generated
- post.format is generated base not on yaml header, but on filename suffix 
- config.permalink configuration is added, which is used for the article without permalink yaml header
- refine __except function
