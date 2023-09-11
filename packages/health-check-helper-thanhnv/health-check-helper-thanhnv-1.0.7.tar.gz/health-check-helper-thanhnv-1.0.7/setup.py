import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="health-check-helper-thanhnv",
    version="1.0.7",
    author="LinLin",
    author_email="nguyenthanh2303@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="",
    url="https://github.com/thanhnv2303/QueryStateLib",
    project_urls={
        "Bug Tracker": "https://github.com/thanhnv2303/QueryStateLib",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "health-check-helper"},
    packages=setuptools.find_packages(where="health-check-helper"),
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "sortedcontainers",
        "pyspnego==0.9.2",
        "requests-kerberos==0.14.0",
        "xmltodict",
    ]
)
