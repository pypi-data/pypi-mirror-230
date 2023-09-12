<a href=https://github.com/Alan3344/auto_syspath3/blob/main/README.zh-CN.md alt=https://github.com/Alan3344/auto_syspath3/blob/main/README.zh-CN.md>切换为中文</a>

### 1. Instructions:

1. Installation (the syntax does not use the latest `Python` version, so it should be compatible with most `Python3` versions above)

- Currently released to PyPI, install directly using `pip install auto_syspath3`

```bash
git clone https://github.com/Alan3344/auto_syspath3.git
cd auto_syspath3
Python setup.py install
```

Or

```bash
pip install git+https://github.com/Alan3344/auto_syspath3.git
```

2. Use

No need to add these two lines at the beginning of each document, because this will attract the annoying `Flake8` squiggly line 〰️ prompt `Flake8(E402)`

- People with OCD say they are less willing to accept

```python
import sys
sys.path.extend(['./', '../'])

from utils import login
from config import env
```

Now you only need to add this line directly in front of the custom package. If you don’t like the `Flake8` prompt unused, you can add `# noqa` after it

Just reference it in front of the custom module

- According to the characteristics of `Python` imported modules, this `__init__.py` file will be executed automatically, so there is no need to write `add_path()` function

```python
import os
import auto_syspath3 # noqa
from utils import quit
from config import env
```

### 2. Refused `Flake8` prompt detection: module level import not at top of file Flake8(E402)

- Reason: In order to make this file run independently, put `import` into the function

### 3. Reasons for writing this module:

I use `VSCode` to write `Python` code, but `VSCode` import is correctly prompted, but `Flake8` prompts an error
Maybe using `PyCharm` will not have this problem, but he needs to be set to `source root`, I don't like this

1. The original appearance of this function has to be copied every time it is referenced
2. Secondly, this file is mainly placed in the `site-packages` directory. After packaging and sending it to others for use, this file will be missing
3. I found a similar package on `pypi`, but it failed to meet my expectations, so I wrote one myself
4. The important thing is that after using this package, the customized package can be used in any terminal, no need to set `source root`

```python
def add_path(path=__file__, deep=0):
    """Add a path to the sys.path if it is not already there."""
    paths = []
    path = os.path.abspath(path)
    dirname = os.path.dirname(path)
    for i in range(deep):
        dirname = os.path.dirname(dirname)
    d(f'dirname: {dirname}')
    for p in os.walk(dirname):
        p0 = p[0].replace(dirname, '')
        if p0.startswith('/.') or '__pycache__' in p0:
            continue
        elif not p[0] in sys.path:
            paths.append(p[0])
            sys.path.insert(0, p[0])
            d(f'add path: {p[0]}')
    return paths
```

### Screenshot during use

- Solve the error when the subpackage `py` file imports the top-level module method: `ModuleNotFoundError: No module named 'package name'`

- Normally, our `pwd` paths are all in the top-level directory. At this time, we can directly run the `main.py` file. Of course, there is no problem if I run `python test_project/main.py` directly.

1. If your project structure is like this, the `main.py` file is the entry file, `child_package` is the custom package, and `child_package/child_package` is the subpackage of the custom package, they all have specific ` py` file
   ![](./screenshot/Snipaste_2023-08-13_14-23-52.png)

2. Run directly in the entry file in the `main.py` file like this
   ![](./screenshot/Snipaste_2023-08-13_14-24-57.png)

3. This is how it works in the `child_package/call_user.py` file. The first time the error is reported because the line `import auto_syspath3 # noqa F401` has been commented out
   ![](./screenshot/Snipaste_2023-08-13_14-28-35.png)

4. This is how it works in the `child_package/child_package/call_user.py` file. The first time the error is reported because the line `import auto_syspath3 # noqa F401` is commented out
   ![](./screenshot/Snipaste_2023-08-13_14-28-57.png)
