from setuptools import setup, find_packages

setup(
    name="invoke_api",
    version="0.1",
    author="karman",
    author_email="460312252@qq.com",
    description="use ak and sk invoke huawei cloud http api",
    packages=find_packages(),
    install_requires=['requests'],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

