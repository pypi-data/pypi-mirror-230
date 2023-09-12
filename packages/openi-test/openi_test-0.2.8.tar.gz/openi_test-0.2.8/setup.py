# python setup.py sdist bdist_wheel
# twine upload dist/*
# twine upload --repository testpypi dist/*
# pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple <your_package_in_testpypi>

from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='openi_test',
    version='0.2.8',
    description='A test packages for openi pypi',
    package_dir={'': 'src'},
    packages=['openi','openi.dataset','openi.path','openi.cloudbrain','openi.utils'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://openi.pcl.ac.cn/liuzx/openi-pypi-test',
    author='chenzh05,liuzx',
    author_email='chenzh.ds@outlook.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    install_requires=['emoji','requests','tqdm'],
    python_requires='>=3.6',
)