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
    name="django-data-import-management",
    version="0.2.1",
    description="Django data import management application.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Qian DingFeng",
    author_email="qiandingfeng@zencore.cn",
    maintainer="Qian DingFeng",
    maintainer_email="qiandingfeng@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django extentions"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_data_import_management_example",
            "django_data_import_management_example.migrations",
            "django_data_import_management_demo",
        ],
    ),
    zip_safe=False,
    include_package_data=True,
)
