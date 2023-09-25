from setuptools import setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name="vedro-replay",
    version="0.2.0",
    description="vedro-replay package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Konstantin Shefer",
    author_email="kostya.shefer.999@gmail.com",
    python_requires=">=3.9",
    url="https://github.com/kvs8/vedro-replay",
    license="Apache-2.0",
    packages=['vedro_replay'],
    install_requires=find_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "vedro-replay = vedro_replay:command",
        ],
    },
    include_package_data=True,
)
