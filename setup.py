from setuptools import setup

setup(name='ssht',
    version='0.7a1',
    description='SSH client wrapper for easily connecting to hosts',
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Shells',
        'Topic :: Utilities',
    ],
    url='http://github.com/hkraal/ssht',
    author='Henk Kraal',
    author_email='hkraal@users.noreply.github.com',
    license='MIT',
    packages=['ssht'],
    package_dir={'ssht':
                 'ssht'},
    install_requires=[
        'mysql-connector',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points = {
      'console_scripts': ['ssht=ssht.ssht:main'],
    },
    setup_requires = ['pytest-runner'],
    tests_require=['pytest'],
)
