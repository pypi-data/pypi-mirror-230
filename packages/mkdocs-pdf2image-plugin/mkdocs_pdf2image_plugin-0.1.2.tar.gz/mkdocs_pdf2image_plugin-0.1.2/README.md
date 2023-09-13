# mkdocs-pdf2image-plugin

This plugin generates images from the first page of PDF files. It is particularly useful when you want
to include PDF presentations in your documentation.

## Installation

Install the package with pip:

```bash
pip install mkdocs-pdf2image-plugin
```

Note that this plugin uses Edouard Belval's [pdf2image](https://github.com/Belval/pdf2image) package, which requires
[Poppler](https://poppler.freedesktop.org/) to be installed on your system. Read the [installation instructions](https://github.com/Belval/pdf2image/blob/master/README.md) on the pdf2image repository for more information.

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - search
  - pdf2image:
        src:
            - path/to/*.pdf
            - other/**/file.pdf
        dpi: 300
        format: png
```

## Configuration

The plugin supports the following configuration options:

| Option      | Description                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------------|
| `src`       | A **list** of path names to convert (see [documentation](https://docs.python.org/3/library/glob.html) for details). |
| `dpi`       | Image quality in DPI (default 200).                                                                                 |
| `fmt`       | Output image format. Valid options are `jpg` and `png`. Defaults to `jpg`.                                          |
| `size`      | Size of the generated image, defaults to `(None, None)` or `!!python/tuple [NULL, NULL]` in _YAML_.                 |
| `extension` | Output file extension, defaults to `fmt` option.                                                                    |
| `force`     | Force image creation, defaults to `false`. It `true`, the generation is done even if the image already exist.       |
