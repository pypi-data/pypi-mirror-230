# This file is part of the helm-sign Python package
#    https://gitlab.com/MatthiasLohr/helm-sign
#
# Copyright 2020 Matthias Lohr <mail@mlohr.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from setuptools import find_packages, setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="helm-sign",
    description="Gnupg based Signature Tool for Helm Charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Matthias Lohr",
    author_email="mail@mlohr.com",
    url="https://gitlab.com/MatthiasLohr/helm-sign",
    license="Apache License 2.0",
    install_requires=[
        "python-gnupg==0.5.*",
        "PyYAML==6.0.*",
    ],
    python_requires=">=3.7, <4",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"HelmSign": ["py.typed"]},
    include_package_data=True,
    entry_points={"console_scripts": ["helm-sign=HelmSign.main:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development",
        "Topic :: System :: Software Distribution",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": "https://gitlab.com/MatthiasLohr/helm-sign/-/blob/main/README.md",
        "Source": "https://gitlab.com/MatthiasLohr/helm-sign",
        "Tracker": "https://gitlab.com/MatthiasLohr/helm-sign/issues",
    },
)
