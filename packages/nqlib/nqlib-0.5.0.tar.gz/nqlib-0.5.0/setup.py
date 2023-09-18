from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name='nqlib',
    version='0.5.0',  # '0.0.1-pre.1' or '0.0.1'
    packages=find_packages(
        exclude=[
            'tests',
            'conda-release',
            'nqlib_dev',
            'article',
            'online-documentation',
        ],
    ),

    # install_requires=[
    #     'numpy',
    #     'scipy',
    #     'slycot',
    #     'control',
    #     'cvxpy',
    # ],
    # extras_require={
    #     'minreal':  ["slycot"],
    # },

    # author
    author='kenta tanaka',
    author_email='kenta.tanaka@eom.mech.eng.osaka-u.ac.jp',

    url='https://github.com/knttnk/NQLib',
    description='NQLib: Library to design noise shaping quantizer for discrete-valued input control.',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=(
        'discrete-valued input control, '
        'control theory, '
        'quantizer, '
        'control system design, '
        'quantization, '
        'simulation, '
    ),

    python_requires='>=3.8',

    # License, Python version, OS
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        # 'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
)
