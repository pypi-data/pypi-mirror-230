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
    name="django-command-server",
    version="0.1.2",
    description="Django management.command is running a long live task, we make it a linux daemon server, so that you can start, stop, restart the task.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jiang Li",
    author_email="jiangli@zencore.cn",
    maintainer="Jiang Li",
    maintainer_email="jiangli@zencore.cn",
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
            "django_command_server_example",
            "django_command_server_example.migrations",
            "django_command_server_example.management",
            "django_command_server_example.management.commands",
            "django_command_server_demo",
        ],
    ),
    py_modules=["django_command_server"],
    zip_safe=False,
    include_package_data=True,
)
