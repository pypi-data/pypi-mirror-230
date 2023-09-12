import setuptools

with open("README.md", "r",encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name='GG_Bond',
    version="0.0.1",
    author="GG_Bond",
    author_email="m17803141235@163.com",
    long_description=long_description,
    url="https://gitee.com/king8080/flask_news",
    packages=setuptools.find_packages()

)