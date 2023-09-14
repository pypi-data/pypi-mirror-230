from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="alist_v3",
    version="0.1.1",
    description="Write for alist V3",
    author="Iamk77",
    author_email="chenyinfeng50@qq.com",
    url="https://github.com/IamK77/alist_v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
    ],
)