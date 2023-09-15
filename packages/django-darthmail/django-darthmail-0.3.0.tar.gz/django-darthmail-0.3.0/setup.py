import os
import re
from os.path import join, dirname
from setuptools import setup, find_namespace_packages


def get_version(*file_paths):
    """Retrieves the version from the given path"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(filename) as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def long_description():
    """Return long description from README.md if it's present
    because it doesn't get installed."""
    try:
        with open(join(dirname(__file__), "README.md")) as f:
            return f.read()
    except IOError:
        return ""


setup(
    name='django-darthmail',
    packages=[
        'django_darthmail',
    ],
    version=get_version("django_darthmail", "__init__.py"),
    description="""Client for the DarthMail project""",
    long_description=long_description(),
    long_description_content_type='text/markdown',
    author='RegioHelden GmbH',
    author_email='entwicklung@regiohelden.de',
    url='https://github.com/regiohelden/django-darthmail',

    include_package_data=True,
    install_requires=[
        "django>=4.2",
        "requests>=2.31.0",
    ],
    license="BSD-3-Clause",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Email',
    ],
)
