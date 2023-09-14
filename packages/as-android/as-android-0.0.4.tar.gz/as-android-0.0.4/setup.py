from setuptools import setup, find_packages

VERSION = '0.0.4'
DESCRIPTION = 'airscript 类型提示语言包'

setup(
    name="as-android",
    version=VERSION,
    author="aojoy",
    author_email="aojoytec@163.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding="UTF8").read(),
    packages=find_packages(),
    keywords=['python', "airscript"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/itisl2220/airscript",
)
