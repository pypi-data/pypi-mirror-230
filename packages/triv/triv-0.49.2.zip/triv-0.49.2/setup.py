from distutils.core import setup

with open('README.md') as f:
  readme = f.read()

setup(name='triv',
    version='0.49.2',
    description='A syntax for the web and more...',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Triv Collective',
    author_email='maintainer@triv.co',
    url='https://www.triv.co/',
    license='bsd',
    python_requires='>=3.5.0',
    packages=['triv'],
    package_data={'triv': ['element_cases.txt']},
    entry_points={
        'console_scripts': [
            '3v=triv.triv:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Code Generators',
        'Topic :: File Formats',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: SGML',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)
