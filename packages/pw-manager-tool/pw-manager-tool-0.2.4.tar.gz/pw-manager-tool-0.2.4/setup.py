from setuptools import setup, find_packages

setup(
    name='pw-manager-tool',
    version='0.2.4',
    description='Password Manager',
    author='scatterman99',
    author_email='db.brunetti4@gmail.com',
    packages=find_packages(),
    install_requires=[
        'cryptography>=41.0.0'
    ],
    entry_points={
        'console_scripts': [
            'pw-manager = manager.main:execute'
        ],
    },
)