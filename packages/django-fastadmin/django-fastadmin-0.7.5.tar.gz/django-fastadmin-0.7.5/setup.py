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
    name="django-fastadmin",
    version="0.7.5",
    description="django admin extensions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zhao GuangFan",
    author_email="zhaoguangfan@zencore.cn",
    maintainer="Zhao GuangFan",
    maintainer_email="zhaoguangfan@zencore.cn",
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
    keywords=["django admin extentions"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_fastadmin_example",
            "django_fastadmin_example.migrations",
            "django_fastadmin_demo",
        ],
    ),
    include_package_data=True,
    zip_safe=False,
)
