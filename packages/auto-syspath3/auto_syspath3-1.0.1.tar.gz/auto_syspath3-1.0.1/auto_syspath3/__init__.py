'''
拒绝`Flake8`提示检测: module level import not at top of file Flake8(E402)
原因: 为了让这个文件可以单独运行, 所以把`import`放到了函数里面

编写这个包的原因:
我使用`VSCode`编写`python`代码的,但是`VSCode`导入是正确提示,但是`Flake8`提示错误
可能使用PyCharm不会有这个问题,但是他需要设置为`source root`,我不喜欢这样

这个函数原本的样子,每次引用,都得复制一遍
其实这个文件主要是放在`site-packages`目录,打包后发给别人使用会缺少这个文件
我在`pypi`上有找到类似的包,但是未能达到我的预期,所以自己写了一个
重要的是,使用这个包后,自定义的包在任何一个终端都可以使用,不需要设置`source root`

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
'''

import inspect
import logging as log
import os
import re
import sys
from configparser import ConfigParser
from typing import TypeVar

__version__ = '1.0.1'
__author__ = 'Alan3344'

PatternString = TypeVar("PatternString", str, re.Pattern)


def getenv(key: str, default: str = "") -> str:
    """get env value, if not exists, return default"""
    return os.environ.get(key, default)


def add_env_dir_names() -> list[str]:
    pwd = os.getcwd()
    ret = []
    for dir in os.listdir(pwd):
        if os.path.isdir(dir):
            child_dir = os.path.join(pwd, dir, 'bin')
            if os.path.exists(child_dir) and os.path.join(child_dir, 'activate'):
                ret.append(dir)
    return ret


class SysPath:
    # path
    root_dir = os.getcwd()
    root_name = os.path.basename(root_dir)

    debug = 0

    # var
    exclude = [
        '.git',
        '__pycache__',
        '.vscode',
        '.idea',
        '.mypy_cache',
        '.pytest_cache',
        'venv',
        '.venv',
    ]
    depth = getenv('syspath_depth') and int(getenv('syspath_depth')) or 0
    regex: PatternString = getenv('syspath_regex', '')

    # No matter how many levels are specified, the end point is relative to the cwd directory
    depth_limit: bool = getenv('syspath_depth_limit', True)
    log_level = (
        getenv('syspath_log_level', '').upper() or 'DEBUG' if debug else 'CRITICAL'
    )


log.basicConfig(
    level=log.getLevelName(SysPath.log_level),
    format="%(asctime)s - %(name)s - \033[1;32m%(levelname)s\033[0m - %(message)s",
)


def __():
    se = getenv('syspath_exclude')
    if se:
        SysPath.exclude = list(filter(lambda x: x, se.split(',')))
    sd = getenv('syspath_depth')
    if sd:
        try:
            SysPath.depth = int(sd)
        except Exception as e:
            log.error(f"syspath_depth: {e}")

    if getenv('syspath_depth_limit'):
        dl = getenv('syspath_depth_limit')
        if dl.lower() == 'false' or dl.lower() == '0':
            SysPath.depth_limit = False
        elif dl.lower() == 'true' or dl.lower() == '1':
            SysPath.depth_limit = True
        else:
            SysPath.depth_limit = bool(dl)

    log.info(f"os.cwd(): {SysPath.root_dir}")
    cfg_path = os.path.join(os.getcwd(), 'setup.cfg')

    # if setup.cfg exists, use setup.cfg configuration
    if os.path.exists('setup.cfg'):
        log.debug(f'setup.cfg exists: use {cfg_path} configration')
        configReader = ConfigParser()
        configReader.read(cfg_path, encoding='utf-8')

        def func(type_):
            return {
                'int': configReader.getint,
                'bool': configReader.getboolean,
                'str': configReader.get,
            }[type_]

        def get_config(key, type_, default=None):
            try:
                return func(type_)('syspath', key)
            except Exception:
                return default

        if 'syspath' in configReader.sections():
            # if exclude := get_config('syspath', 'exclude', 'str', ''):
            #     SysPath.exclude = list(filter(lambda x: x, exclude.split(',')))

            exclude = get_config('exclude', 'str', '')
            if exclude:
                SysPath.exclude = list(filter(lambda x: x, exclude.split(',')))

            depth = get_config('depth', 'int', None)
            if depth is not None:
                SysPath.depth = depth

            regex = get_config('regex', 'str', '')
            if regex:
                SysPath.regex = regex

            depth_limit = get_config('depth_limit', 'bool', None)
            if depth_limit is not None:
                SysPath.depth_limit = depth_limit

    envdir = add_env_dir_names()
    if envdir:
        SysPath.exclude.extend(envdir)
    log.debug(f"exclude: {SysPath.exclude}")


__()

if __name__ == '__main__':
    SysPath.depth = 0  # try > 0 ?


if SysPath.regex and isinstance(SysPath.regex, str):
    SysPath.regex = re.compile(SysPath.regex)


def get_file_position():
    """
    ```python
    import inspect

    for stack in inspect.stack():
        print(stack.filename, stack.lineno, stack.function)
    ```
    /opt/homebrew/lib/python3.11/site-packages/autosyspath/__init__.py 26 add_path
    /opt/homebrew/lib/python3.11/site-packages/autosyspath/__init__.py 46 <module>
    <frozen importlib._bootstrap> 241 _call_with_frames_removed
    <frozen importlib._bootstrap_external> 940 exec_module
    <frozen importlib._bootstrap> 690 _load_unlocked
    <frozen importlib._bootstrap> 1147 _find_and_load_unlocked
    <frozen importlib._bootstrap> 1176 _find_and_load
    /Users/----/--/---/-----/--/----/test2/test.py 5 <module>
    """
    return [stack.filename for stack in inspect.stack()]


def add_to_syspath(
    path: str = SysPath.root_dir,
    depth: int = SysPath.depth,
    exclude_list: list[str] = SysPath.exclude,
    exclude_regex: PatternString = SysPath.regex,
):
    """Add a path to the sys.path if it is not already there."""
    # TODO: Determine whether the current working path is in the file path
    # args0 = sys.argv[0]
    # if SysPath.root_dir not in args0:
    #     # os.chdir(os.path.dirname(args0)
    #     # SysPath.root_dir = os.path.dirname(args0)
    #     # SysPath.root_name = os.path.basename(SysPath.root_dir)
    #     log.debug(f"chdir: {SysPath.root_dir}")
    #     # path = args0
    # else:
    path = path or get_file_position()[-1]
    paths = []
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return print(f"path: {path} not exists")
    dirname = path
    if os.path.isfile(path):
        dirname = os.path.dirname(path)
    for i in range(depth):
        dirname = os.path.dirname(dirname)

    # limit the depth
    if SysPath.depth_limit:
        if dirname != os.path.dirname(SysPath.root_dir):
            log.warning(
                'depth_limit: Exceeding the safe depth, '
                + 'it has been automatically set the cwd path'
            )
            dirname = SysPath.root_dir

    log.debug(f"dirname: {dirname}")

    for fp, _, _ in os.walk(dirname):
        # add deep limit:
        # if depth_limit is True, then only add the path under the cwd
        # so depth is useless, default is 0 is ok
        if SysPath.depth_limit:
            if not fp.startswith(SysPath.root_dir):
                continue
        for ex in exclude_list:
            if ex in fp:
                break
        else:
            # check if it is a regex object
            if exclude_regex:
                if isinstance(exclude_regex, str):
                    exclude_regex = re.compile(exclude_regex)
                if exclude_regex.search(fp):
                    continue

            if re.search(r'\..+$', os.path.basename(fp)):
                continue

            if fp not in sys.path:
                paths.append(fp)
                sys.path.insert(0, fp)
                log.debug(f"add_path: {fp}")

    return paths


add_to_syspath()
