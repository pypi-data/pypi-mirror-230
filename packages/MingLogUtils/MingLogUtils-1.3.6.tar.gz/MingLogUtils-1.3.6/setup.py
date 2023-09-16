from setuptools import setup, find_packages

setup(
    name="MingLogUtils",
    version="1.3.6",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'pillow',
        'opencv-python',
        'aiofiles',
        'scipy',
        'pandas',
        'requests'
    ],
    package_data={'CVUtils': ['files\*',], 'SpiderUtils': ['files\*']},
    author="MingLog",
    author_email="736704198@qq.com",
    description="自定义相关工具库",
    long_description=open("README.md", encoding='UTF-8').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://minglog.hzbmmc.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)