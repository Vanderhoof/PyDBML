from setuptools import setup


SHORT_DESCRIPTION = 'DBML syntax parser for Python'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='pydbml',
    python_requires='>=3.5',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='0.4.1',
    author='Daniil Minukhin',
    author_email='ddddsa@gmail.com',
    url='https://github.com/Vanderhoof/PyDBML',
    packages=['pydbml', 'pydbml.definitions'],
    license='MIT',
    platforms='any',
    install_requires=[
        'pyparsing>=2.4.7',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ]
)
