import setuptools
from nonebot_plugin_uvdiviner import __version__

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name = "nonebot_plugin_uvdiviner",
    version = __version__,
    author = "Night Resurgent <fu050409@163.com>",
    author_email = "fu050409@163.com",
    description = "基于周易蓍草算法的 QQ 占卜师.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://gitee.com/unvisitor/nonebot-plugin-uvdiviner",
    project_urls = {
        "Bug Tracker": "https://gitee.com/unvisitor/nonebot-plugin-uvdiviner/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license = "Apache-2.0",
    packages = setuptools.find_packages(),
    install_requires = [
        'nonebot2',
        'uvdiviner',
        'nonebot-plugin-apscheduler'
    ],
    python_requires=">=3",
)