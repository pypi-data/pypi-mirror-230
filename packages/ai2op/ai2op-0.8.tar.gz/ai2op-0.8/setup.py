from setuptools import setup, find_packages

setup(
    name='ai2op',
    version='0.8',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    description='A package for fine-tuning and utilizing the ai2op model',
    author='Collin Lafayette',
    author_email='sscla-ops@outlook.com',
    url='https://github.com/sscla1/ai2op',
    py_modules=['interpret', 'summarize'],
    install_requires=[
        'torch',
        'transformers',
        'pandas',
        'nbformat',
        'chardet',
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

    keywords='machine-learning transformers fine-tuning ai market data stock option trading automation',
)