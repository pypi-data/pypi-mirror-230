from setuptools import find_packages, setup as setup2
from .version import read_version


def setup(
    name,
    package_name=None,
    version=None,
    description=None,
    author=None,
    author_email=None,
    url=None,
    packages=None,
    package_data=None,
    install_requires=None,
    long_description=None,
    *args,
    **kwargs,
):
    version = version or read_version()
    return setup2(
        name=package_name or name,
        version=version,
        description=description or name,
        author=author or "bingtao",
        author_email=author_email or "1007530194@qq.com",
        url=url or f"https://github.com/farfarfun/{name}",
        packages=packages or find_packages(),
        package_data=package_data or {"": ["*.js", "*.*"]},
        install_requires=install_requires or [],
        long_description=long_description or open("README.md").read(),
        long_description_content_type="text/markdown",
        *args,
        **kwargs,
    )
