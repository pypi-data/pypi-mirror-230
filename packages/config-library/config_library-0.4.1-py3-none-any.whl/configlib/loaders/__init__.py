#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import os
from .baseloader import BaseLoader, extension_registry
from .conf_loader import ConfLoader
from .xml_loader import XmlLoader
from .json_loader import JsonLoader
from .jsonc_loader import JsoncLoader
try:
    from .json5_loader import Json5Loader
except NotImplementedError:
    Json5Loader = None
try:
    from .toml_loader import TomlLoader
except NotImplementedError:
    TomlLoader = None
try:
    from .yaml_loader import YamlLoader
except NotImplementedError:
    YamlLoader = None


def loadConfig(fp):
    fp = os.path.abspath(fp)
    extension = os.path.splitext(fp)[1]
    loader_class = extension_registry.get(extension, None)
    if loader_class is None:
        raise TypeError('unsupported filetype')
    loader = loader_class(fp)
    return loader.load()
