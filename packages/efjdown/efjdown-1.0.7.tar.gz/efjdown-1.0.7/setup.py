from setuptools import setup, find_packages
with open('README.md', 'r',encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='efjdown',
    version='1.0.7',
    packages=['efjdown'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests',
        'tqdm',
        'loguru',
    ],
    entry_points={
        'console_scripts': [
            'efjdown = efjdown.efjdown:main',
        ],
    },
)
