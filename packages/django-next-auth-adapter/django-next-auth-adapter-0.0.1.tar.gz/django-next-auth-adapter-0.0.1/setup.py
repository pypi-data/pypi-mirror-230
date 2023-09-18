#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

# with open("HISTORY.md") as history_file:
#     history = history_file.read()

requirements = [
    "Django>=3.0.0",
    "djangorestframework>=3.0",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Abdullah Adeel",
    author_email="contact.abdadeel@gamil.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
    ],
    description="A Django app to to handle server side requirests of next-auth-http-adapter",
    entry_points={},
    install_requires=requirements,
    license="MIT license",
    # long_description=readme + "\n\n" + history,
    long_description=readme,
    include_package_data=True,
    keywords=[
        "django_next_auth_adapter",
        "django",
        "next-auth",
        "auth",
        "rest",
        "restframework",
    ],
    name="django-next-auth-adapter",
    packages=find_packages(
        include=["django_next_auth_adapter", "django_next_auth_adapter.*"]
    ),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/mabdullahadeel/django-next-auth-adapter",
    version="0.0.1",
    zip_safe=False,
)
