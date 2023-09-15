from setuptools import setup, find_packages

setup(
    name="operatorio",
    version="0.2.4",
    description="A Python SDK for the Operator Search API.",
    author="David Shi",
    author_email="david@operator.io",
    url="https://github.com/operatorlabs/sdk/python",
    packages=['operatorio'],  
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    test_suite="tests",
)

