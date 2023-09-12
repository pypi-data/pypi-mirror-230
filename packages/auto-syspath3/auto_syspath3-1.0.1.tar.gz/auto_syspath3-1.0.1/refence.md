# About Upload Error

### 1. InvalidDistribution: Unknown distribution format: ''

https://stackoverflow.com/questions/65369612/unknown-distribution-format-when-uploading-to-pypi-via-twine

### 2. Response from https://upload.pypi.org/legacy/: 400 The description failed to render in the default format of reStructuredText. See https://pypi.org/help/#description-content-type for more information.

https://github.com/pypi/warehouse/issues/5890

### 3. https://github.com/pypa/gh-action-pypi-publish

correct keywork is `packages-dir`

`packages`, `package-dir` is wrong

```yaml
- name: Publish package to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: custom-dir/
```
