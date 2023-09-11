import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "gammarer.aws-secure-flow-log-bucket",
    "version": "0.5.6",
    "description": "Specific AWS VPC FlowLog Bucket",
    "license": "Apache-2.0",
    "url": "https://github.com/yicr/aws-secure-flow-log-bucket.git",
    "long_description_content_type": "text/markdown",
    "author": "yicr<yicr@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/yicr/aws-secure-flow-log-bucket.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "gammarer.aws_secure_flow_log_bucket",
        "gammarer.aws_secure_flow_log_bucket._jsii"
    ],
    "package_data": {
        "gammarer.aws_secure_flow_log_bucket._jsii": [
            "aws-secure-flow-log-bucket@0.5.6.jsii.tgz"
        ],
        "gammarer.aws_secure_flow_log_bucket": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.80.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "gammarer.aws-secure-bucket>=0.12.4, <0.13.0",
        "gammarer.aws-secure-log-bucket>=0.12.6, <0.13.0",
        "jsii>=1.88.0, <2.0.0",
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
