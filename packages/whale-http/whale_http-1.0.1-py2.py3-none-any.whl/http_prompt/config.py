"""Functions that deal with the user configuration."""

import os
import shutil
from pathlib import Path

from http_prompt.utils import writeprojecttofile

from . import defaultconfig, xdg
from .constants import PROJECT_COLLECT_FILE, PROJECT_CONFIG, PROJECT_HOST_DEFAULT


def write_projectcollect_file(project_name: str, project_path: str):
    assert project_name
    assert project_path
    prjcolfile = get__projectcollect_file()
    with open(prjcolfile, "a", encoding="utf-8") as f:
        writeprojecttofile(f, project_name, project_path)


def newproject(prjname: str, prjpath: str, url: str):
    pname = prjname or "default"
    ppath = Path(prjpath).expanduser() if prjpath else Path.cwd().joinpath(pname)
    url = url or PROJECT_HOST_DEFAULT

    if not ppath.exists():
        ppath.mkdir(parents=True)

    conffile = ppath.joinpath(PROJECT_CONFIG)
    if not conffile.exists():
        conffile.touch()
        with open(conffile, "a", encoding="utf-8") as f:
            f.write(f"host: {url}")
    write_projectcollect_file(pname, str(ppath))


def get__projectcollect_file():
    configfile = Path(xdg.get_config_dir()).joinpath(PROJECT_COLLECT_FILE)
    if not configfile.exists():
        configfile.touch()
        pname = "default"
        ppath = Path.cwd().joinpath(pname)
        newproject(pname, str(ppath), "")

    return configfile


def get_user_config_path():
    """Get the path to the user config file."""
    return os.path.join(xdg.get_config_dir(), "config.py")


def initialize():
    """Initialize a default config file if it doesn't exist yet.

    Returns:
        tuple: A tuple of (copied, dst_path). `copied` is a bool indicating if
            this function created the default config file. `dst_path` is the
            path of the user config file.
    """
    dst_path = get_user_config_path()
    copied = False
    if not os.path.exists(dst_path):
        src_path = os.path.join(os.path.dirname(__file__), "defaultconfig.py")
        shutil.copyfile(src_path, dst_path)
        copied = True
    return copied, dst_path


def _module_to_dict(module):
    attrs = {}
    attr_names = filter(lambda n: not n.startswith("_"), dir(module))
    for name in attr_names:
        value = getattr(module, name)
        attrs[name] = value
    return attrs


def load_default():
    """Return default config as a dict."""
    return _module_to_dict(defaultconfig)


def load_user():
    """Read user config file and return it as a dict."""
    config_path = get_user_config_path()
    config = {}

    # TODO: This may be overkill and too slow just for reading a config file
    with open(config_path, encoding="utf-8") as f:
        code = compile(f.read(), config_path, "exec")
    exec(code, config)

    keys = list(config.keys())
    for k in keys:
        if k.startswith("_"):
            del config[k]

    return config


def load():
    """Read default and user config files and return them as a dict."""
    config = load_default()
    config.update(load_user())
    return config
