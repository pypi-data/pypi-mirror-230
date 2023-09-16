# -*- coding: utf-8 -*-
import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x for x in fobj.readlines() if x]
requires = [x.strip() for x in requires if x.strip()]

setup(
    name="django-visit-on-site-in-new-window",
    version="0.1.1",
    description="Turn VISIT-ON-SITE button to open in the new window on Django's admin site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Suo Jiang",
    author_email="suojiang@zencore.cn",
    maintainer="Suo Jiang",
    maintainer_email="suojiang@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django admin extentions", "django visit on site in new window"],
    install_requires=requires,
    packages=find_packages(
        ".",
        exclude=[
            "django_visit_on_site_in_new_window_example",
            "django_visit_on_site_in_new_window_example.migrations",
            "django_visit_on_site_in_new_window_demo",
        ],
    ),
    py_modules=["django_visit_on_site_in_new_window_example"],
    zip_safe=False,
    include_package_data=True,
)
