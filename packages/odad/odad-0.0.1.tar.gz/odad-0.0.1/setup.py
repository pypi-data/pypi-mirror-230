from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Anomaly detection for one-dimensional data'

setup(
    name="odad",
    version=VERSION,
    author="Zhilin Wang",
    author_email="wangzhil@iu.edu",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open('README.md',encoding="UTF8").read(),
    packages=find_packages(),
    install_requires=['numpy'],
    keywords=['python', 'anomaly detection', 'one-dimentional data'],
    license="MIT",
    url="https://github.com/wzljerry/xiezhi",
    #scripts=['cut_video/cut_video.py'],
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows"
    ]
)
