from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = []
with open("requirements/requirements.txt") as f:
    install_requires = f.read().splitlines()


setup(
    name="habitat-tools",
    use_scm_version={
        "version_scheme": "post-release",
        "write_to": "habitat_tools/_version.py",
    },
    author="Warren Snowden",
    author_email="warren.snowden@gmail.com",
    description="A habitat API utility package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    licence="proprietary",
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=["setuptools_scm"],
)
