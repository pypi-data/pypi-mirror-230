# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages
from django_apiview.version import VERSION

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x.strip() for x in fobj.readlines() if x.strip()]


setup(
    name="django-apiview",
    version="1.0.32",  # You have to change django_apiview.version too...
    description="A set of django tools to help you create JSON service..",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zhao JunXin",
    author_email="zhaojunxin@zencore.cn",
    maintainer="Zhao JunXin",
    maintainer_email="zhaojunxin@zencore.cn",
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
    keywords=["django-apiview"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=(
            "django_apiview_demo",
            "django_apiview_example",
            "django_apiview_example.migrations",
        ),
    ),
    zip_safe=False,
    include_package_data=True,
)
