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
    name="django-secure-password-input",
    version="0.1.5",
    description="A simple django application provides function to encrypt password value with rsa public key before form submit and decrypt at the backend.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Wu Tao",
    author_email="wutao@zencore.cn",
    maintainer="Wu Tao",
    maintainer_email="wutao@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django admin extentions", "django secure password input"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_secure_password_input_example",
            "django_secure_password_input_example.migrations",
            "django_secure_password_input_demo",
        ],
    ),
    zip_safe=False,
    include_package_data=True,
)
