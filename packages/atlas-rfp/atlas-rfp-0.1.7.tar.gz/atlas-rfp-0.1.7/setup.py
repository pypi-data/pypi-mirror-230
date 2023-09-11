import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='atlas-rfp',
    version='0.1.7',
    author='Christopher Johnstone',
    author_email='meson800@gmail.com',
    description='Programmatically access the Atlas RFP interface',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/meson800/atlas-rfp',
    project_urls={
        'Bug Tracker': 'https://github.com/meson800/atlas-rfp/issues',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Session'
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires=">=3.7",
    install_requires=[
        'beautifulsoup4',
        'touchstone-auth>=0.5.1',
        'pydantic',
        'py-moneyed'
    ]
)
