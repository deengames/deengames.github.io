# Build a Naive Ruby to Python Converter

TLDR: How can I quickly, *without writing a parser*, convert from simple Ruby to Python code?

Background: both languages are mostly similar in terms of functionality and performance. The Python community seems ~3x bigger (eg. there's WebRuby for Ruby, for Python we have Brython, PyJs, Skulpt, etc.). So, all other things being equal, being able to convert Ruby to Python makes sense. 

No flame wars, please. I spent years writing Ruby code, and I personally find the language easier to understand and use (eg. private methods, better reflection capability to determine what methods are available at runtime, etc.)

The goal is not a 100%-automated process that produces terrible (or beautiful) code; the point is to automate 80% of the work, and come out with something that looks almost like a human wrote it (eg. good coding style).

# Rough Order of Steps

- Replace `require` calls for gems to `import` calls for pip packages. We can do something here to help auto-map (eg. `kramdown` => `markdown`)
- Replace `def (a-zA-Z0-9_-)*` with `def \1:`. Ditto for `class`. Even though the colon is optional.
- Figure out if we're in a class (`class ...` near the top of the file). If so, apply class-specific rules.
- Replace nil with None. Replace `x.None?` with `if x == None`
- Replace true with True and false with false
- `Blah.each do |n|` with `for n in Blah:`. UNLESS there's a bracket between the pipes. 
- Delete lines that are just `end` with whitespace.
- `raise "..."` with `raise(Exception("..."))` 
- :x => "x"

## Standard Library mappings
- String: `x.gsub` => `x.replace`
- Files: `File.exist?` with `os.path.isfile(...)`, `Dir.exist?` with `os.path.isdir(...)`


## Class-Specific Rules
- Replace any `def` after `private` with `def __`.
- For any `def`, add a first argument of `self`.
- Replace `@<alphanumeric>` with `self.\1`