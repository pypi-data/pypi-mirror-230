# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x.strip() for x in fobj.readlines() if x.strip()]


setup(
    name="django-safe-settings",
    version="0.1.4",
    description="Django application let you write your database password settings in an encrypted way.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zhao ShiXiao",
    author_email="zhaoshixiao@zencore.cn",
    maintainer="Zhao ShiXiao",
    maintainer_email="zhaoshixiao@zencore.cn",
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django-extensions"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_safe_settings_demo",
            "django_safe_settings_example",
            "django_safe_settings_example.migrations",
        ],
    ),
    zip_safe=False,
    include_package_data=True,
)
