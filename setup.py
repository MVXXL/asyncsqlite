import re
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

version = ''
with open('asyncsqlite/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name='asyncsqlite',
    version=version,
    author='YourName',
    url='https://github.com/MVXXL/asyncsqlite',
    packages=find_packages(include=['asyncsqlite', 'asyncsqlite.*']),
    package_data={'asyncsqlite': ['py.typed']},
    license='MIT',
    description='An asynchronous SQLite wrapper for both small and large projects.',
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    python_requires='>=3.8.0',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Database :: Database Engines/Servers',
    ]
)
