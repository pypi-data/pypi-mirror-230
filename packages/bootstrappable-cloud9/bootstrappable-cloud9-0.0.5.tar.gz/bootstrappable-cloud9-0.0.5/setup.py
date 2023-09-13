import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "bootstrappable-cloud9",
    "version": "0.0.5",
    "description": "bootstrappable-cloud9",
    "license": "MIT",
    "url": "https://github.com/rafams/bootstrappable-cloud9.git",
    "long_description_content_type": "text/markdown",
    "author": "Rafael Mosca<rafams@amazon.es>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/rafams/bootstrappable-cloud9.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "bootstrappable_cloud9",
        "bootstrappable_cloud9._jsii"
    ],
    "package_data": {
        "bootstrappable_cloud9._jsii": [
            "bootstrappable-cloud9@0.0.5.jsii.tgz"
        ],
        "bootstrappable_cloud9": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.92.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.87.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
