# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = requires = [x.strip() for x in fobj.readlines() if x.strip()]

setup(
    name="django-horizontal-list-filter",
    version="0.2.9",
    description="Move list filter to  above of the changelist in django admin site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zheng JiaHui",
    author_email="zhengjiahui@zencore.cn",
    maintainer="Zheng JiaHui",
    maintainer_email="zhengjiahui@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django admin extentions", "django horizontal list filter"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_horizontal_list_filter_example",
            "django_horizontal_list_filter_example.migrations",
            "django_horizontal_list_filter_demo",
        ],
    ),
    zip_safe=False,
    include_package_data=True,
)
