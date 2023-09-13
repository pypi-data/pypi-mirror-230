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
    name="django-admin-global-sidebar",
    version="0.2.2",
    description="Provides a configurable left navigation bar for Django's admin site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Li HaoRan",
    author_email="lihaoran@zencore.cn",
    maintainer="Li HaoRan",
    maintainer_email="lihaoran@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django admin extentions", "django admin global admin"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_admin_global_sidebar_demo",
            "django_admin_global_sidebar_example",
            "django_admin_global_sidebar_example.migrations",
        ],
    ),
    zip_safe=False,
    include_package_data=True,
)
