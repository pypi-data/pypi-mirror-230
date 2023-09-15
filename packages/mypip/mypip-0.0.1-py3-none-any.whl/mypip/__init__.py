#!/usr/bin/env python3
import os
import sys

import codefast as cf

from .config import PIP_URL


def install_private(module_name: str) -> bool:
    url = cf.b64decode(PIP_URL)
    url = f'{url}/{module_name}.tgz'
    ret = os.system(f'pip install {url}')
    if ret != 0:
        return False
    return True


def install_public(module_name: str):
    ret = os.system(f'pip install {module_name}')
    return ret == 0


def pip_install():
    module_name = sys.argv[1]
    ret = install_private(module_name)
    if ret:
        return True
    return install_public(module_name)
