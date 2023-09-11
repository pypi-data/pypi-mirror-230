from setuptools import find_packages, setup

install_requires = open("requirements.txt").read().strip().split("\n")

setup(
    name="freeq",
    version="0.0.11",
    description="Zero-setup queue with e2e encryption for free in 1 line of code",
    author="Viktor Hronec",
    author_email="zamr666@gmail.com",
    platforms=["linux"],
    license="Apache 2.0",
    url="https://github.com/hronecviktor/freeq",
    python_requires=">=3.7",
    install_requires=install_requires,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    #
    project_urls={
        "Source": "https://github.com/hronecviktor/freeq",
        "Tracker": "https://github.com/hronecviktor/freeq/issues",
    },
    # Package setup
    packages=find_packages(),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
)
