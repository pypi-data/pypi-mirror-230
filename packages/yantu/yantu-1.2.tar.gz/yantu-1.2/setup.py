from setuptools import setup, find_packages

VERSION = '1.2'
DESCRIPTION = 'Yantu tools for python'

setup(
    name="yantu",
    version=VERSION,
    author="yantu-tech",
    author_email="wu466687121@qq.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding="UTF8").read(),
    packages=find_packages(),
    install_requires=['requests', 'setuptools'],
    keywords=["python", "yantu", "中文", "人工智能"],
    license="MIT",
    url="https://gitee.com/Sea-Depth/yantu-tools-test",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows"
    ]
)
