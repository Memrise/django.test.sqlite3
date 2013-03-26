from setuptools import setup, find_packages

version = '0.1'

setup(
    name='django_test_sqlite3',
    version=version,
    description="Django testing with sqlite3 for replica databases",
    long_description="""\
""",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Memrise fork from github disdanes',
    author_email='tech@memrise.com',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django >= 1.4'
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
