from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

pkg_req = [
    'requests>=2.25.0'
]
test_req = pkg_req + [
    'pytest>=3.0.6'
]

setup(
    name="bnipython",
    version="0.6.7",
    author="BNI API",
    author_email="",
    license='MIT',
    description="Official  BNI API SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bni-api/bni-python/",
    packages=['bnipython','bnipython.lib','bnipython.lib.api','bnipython.lib.net','bnipython.lib.util'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.5',
    install_requires=pkg_req,
)