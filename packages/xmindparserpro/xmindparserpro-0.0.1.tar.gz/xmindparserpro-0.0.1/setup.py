from setuptools import setup

setup(
    name="xmindparserpro",
    version="0.0.1",
    python_requires=">=3.6.0",
    author="maiyajj",
    author_email="",
    url="https://github.com/maiyajj/xmindparserpro",
    description="xmindparser优化版",
    long_description=r"**基于xmindparser，在json和dict返回内增加了节点关系结构**",
    long_description_content_type="text/markdown",
    packages=["xmindparserpro"],
    entry_points={"console_scripts": ["main=main:main"]},
    install_requires=[],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
