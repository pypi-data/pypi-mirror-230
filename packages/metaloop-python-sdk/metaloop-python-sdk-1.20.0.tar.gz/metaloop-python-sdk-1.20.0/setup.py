from setuptools import find_packages, setup

requires = [
    'requests >= 2.4.2',
    'requests_toolbelt >= 0.3.0',
    'tqdm >= 4.14.0',
    'urllib3 >= 1.15',
    's3transfer >= 0.5.2',
    'boto3 >= 1.16.25',
    'botocore >= 1.24.40',
    'pyzipper >= 0.3.6',
]

setup(
    name='metaloop-python-sdk',
    version='1.20.0',
    packages=find_packages(exclude=['tests*']),
    url='http://data.deepglint.com/',
    license='Apache License 2.0',
    author='yuma',
    author_email='yuma@deepglint.com',
    description='Deepglint Metaloop Python SDK',
    long_description_content_type='text/markdown',
    long_description=open('README.md', encoding='utf-8').read(),
    python_requires=">= 3.5",
    install_requires=requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    project_urls={
        'Documentation': 'https://gitlab.deepglint.com/metaloop/metaloop-python-sdk',
        'Source': 'https://gitlab.deepglint.com/metaloop/metaloop-python-sdk',
    },
)
