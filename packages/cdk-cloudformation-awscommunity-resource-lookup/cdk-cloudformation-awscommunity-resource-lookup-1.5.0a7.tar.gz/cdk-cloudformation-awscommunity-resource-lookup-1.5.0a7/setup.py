import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-cloudformation-awscommunity-resource-lookup",
    "version": "1.5.0.a7",
    "description": "This resource uses AWS Cloud Control API to perform a lookup of a resource of a given type (such as, `AWS::EC2::VPC`) in your AWS account and current region, based on a query you specify.  If only one match is found, this resource returns the primary ID of the resource (in the `AWS::EC2::VPC` example, the VPC ID) and the resource properties, that you can then reference in your template with the `Fn::GetAtt` intrinsic function.  Specify resource type search targets that are supported by Cloud Control API.",
    "license": "Apache-2.0",
    "url": "https://github.com/aws-cloudformation/community-registry-extensions/blob/main/resources/Resource_Lookup/README.md",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-cloudformation.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_cloudformation_awscommunity_resource_lookup",
        "cdk_cloudformation_awscommunity_resource_lookup._jsii"
    ],
    "package_data": {
        "cdk_cloudformation_awscommunity_resource_lookup._jsii": [
            "awscommunity-resource-lookup@1.5.0-alpha.7.jsii.tgz"
        ],
        "cdk_cloudformation_awscommunity_resource_lookup": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.96.2, <3.0.0",
        "constructs>=10.2.70, <11.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
