# vimbuilder

Sphinx extension to create Vim help files.

Converting API documentation of programming languages to Vim help format just
got easier.

## Install

```sh
pip3 install vimbuilder
```

## Usage

Add the extension to your `conf.py` file:
```python
extensions = [
    ...,
    "vimbuilder",
    ...,
]
```

Build Vim help files with `sphinx-build` command

```sh
sphinx-build -M vimhelp ./docs ./build
```

## Configurations

You can add the following configurations to your `conf.py` file:

Option|Default|Description
------|-------|-----------
`vimhelp_tag_prefix`|`''`|String to prefix all tags. Useful for separating namespaces in case of multiple sources of documentation.
`vimhelp_tag_suffix`|`''`|String to suffix all tags. See above.
`vimhelp_tag_filename'|`True`|Whether to suffix filename to all tags in the file. Clarifies topic of help tag.
`vimhelp_tag_topic'|`False`|Same as above except without file extension.
`vimhelp_filename_extension'|`'txt'`|Generated filenames will have this extension.
`vimhelp_filename_suffix'|`''`|First tag in a help file is the filename itself. This adds a suffix to just that tag.

## Projects using Vimbuilder

- [Python documentation](https://github.com/girishji/pythondoc.vim) for Vim and Neovim
