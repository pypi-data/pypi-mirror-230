import versioneer
from setuptools import setup

setup(
    test_suite='tests',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    project_urls={
        'Documentation': 'https://drb-python.gitlab.io/impl/tar',
        'Source': 'https://gitlab.com/drb-python/impl/tar',
    }
)
