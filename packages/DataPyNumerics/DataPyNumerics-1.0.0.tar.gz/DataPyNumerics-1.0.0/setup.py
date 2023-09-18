from setuptools import setup, find_packages

setup(
    name='DataPyNumerics',
    version='1.0.0',
    description='A package for data storage and manipulation',
    author='chanakya ram sai illa',
    author_email='chanakyaramsai@gmail.com',
    packages=find_packages(),
    install_requires=[
        'dill',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
