from setuptools import setup


# Setting up
setup(
    name="RaDinBase1",
    version="0.0.1",
    author="Abuzar",
    author_email="radinofficial15@gmail.com",
    description="It's a School's Database Modifier, That is written by Abuzar Alvi.",
    long_description_content_type="text/markdown",
    long_description="It's a School's Database Modifier, That is written by Abuzar Alvi. They can perform many tasks like insert, check, update, delete, add, sub or many more things.",
    packages=['radin'],
    install_requires=[''],
    keywords=['school', 'database', 'school database','arithmetic', 'mathematics', 'python', 'RaDin', 'RaDin database', 'database modifier'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

# sqlite3>=3.7.15', 'datetime>=5.2', 'calendar>=3.11.5'

# python setup.py sdist bdist_wheel
# python -m twine upload dist/*