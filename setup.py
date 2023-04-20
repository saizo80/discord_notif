import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="discord_notif",
    version="0.2.0",
    author="saizo",
    author_email="saizo@simplemail.is",
    description="importable script to send messages to discord webhooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        "certifi==2022.12.7",
        "charset-normalizer==3.1.0",
        "discord-webhook==1.1.0",
        "idna==3.4",
        "sai_logging @ git+https://git.saizo.gay/saizo/sai_logging.git",
        "requests==2.28.2",
        "urllib3==1.26.15",
    ]
)