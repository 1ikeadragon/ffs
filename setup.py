from setuptools import setup, find_packages

setup(
    name='ffs',
    version='0.1.0',
    author='1ikeadragon',
    description='fix the last command without ChatGPT API key',
    packages=find_packages(where='src'),  
    package_dir={'': 'src'},  
    install_requires=[
        'requests',
        'pybase64',
        'distro'
    ],

    entry_points={
        'console_scripts': [
            'ffs = ffs.ffs:main',
        ]
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
