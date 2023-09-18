import setuptools
import sys

from pathlib import Path

sys.path.append(str(Path("dicergirl").resolve()))

import coc

setuptools.setup(
    name='dicergirl-plugin-coc',
    version=coc.__version__,
    author = "Night Resurgent <fu050409@163.com>",
    author_email = "fu050409@163.com",
    description="Dicergirl COC 模式插件",
    url='https://gitee.com/unvisitor/dicer-plugins/',
    project_urls = {
        "Bug Tracker": "https://gitee.com/unvisitor/dicer-plugins/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license = "Apache-2.0",
    packages = ['dicergirl.coc'],
    install_requires=[
        'dicergirl',
    ],
    python_requires=">=3",
)