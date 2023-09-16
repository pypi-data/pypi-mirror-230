#!/usr/bin/env python3
import os
import sys

import codefast as cf

from .config import PIP_URL


def install_private(module_name: str) -> bool:
    url = cf.b64decode(PIP_URL)
    url = f'{url}/{module_name}.tgz'
    cf.shell(f'pip install {url}')


def install_public(module_name: str):
    cf.shell(f'pip install {module_name}')

def pip_install():
    module_name = sys.argv[1]
    try:
        install_private(module_name)
    except Exception as e:
        print(e)
        install_public(module_name)
    return True
