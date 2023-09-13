from setuptools import find_packages, setup


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

install_requires = [
    'fake_useragent>=1.2.1',
    'lxml>=4.9.3',
    'Requests>=2.31.0',
    'setuptools>=68.1.2'
]

setup(
    name="ChenUtils",
    version="0.0.9",  # 包版本号，便于维护版本
    author="CodexploRe",  # 作者，可以写自己的姓名
    author_email="1259864733@qq.com",  # 作者联系方式，可写自己的邮箱地址
    url="https://gitee.com/CodexploRe",  # 自己项目地址，比如github的项目地址
    description="A package used to store various modules written by individuals.",
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license='MIT License',
    python_requires='>=3.8',  # 对python的最低版本要求
    zip_safe=False
)
