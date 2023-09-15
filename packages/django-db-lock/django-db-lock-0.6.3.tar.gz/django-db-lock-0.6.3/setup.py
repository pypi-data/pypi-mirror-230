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
    name="django-db-lock",
    version="0.6.3",
    description="Lock something and keep status in database. A simple distributed lock system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chao WeiZhi",
    author_email="chaoweizhi@zencore.cn",
    maintainer="Chao WeiZhi",
    maintainer_email="chaoweizhi@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django extentions", "django db lock"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_db_lock_demo",
            "django_db_lock_example",
            "django_db_lock_example.migrations",
        ],
    ),
    py_modules=["django_db_lock"],
    zip_safe=False,
    include_package_data=True,
)
