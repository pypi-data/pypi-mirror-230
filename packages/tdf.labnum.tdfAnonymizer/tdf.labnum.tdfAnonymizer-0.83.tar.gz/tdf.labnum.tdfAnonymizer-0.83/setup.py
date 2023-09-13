from setuptools import setup, find_packages

setup(
    name='tdf.labnum.tdfAnonymizer',
    version='0.83',
    packages=find_packages(),
    install_requires=[
        'nltk',
        'pydantic',
        'faker',
        'pandas',
        'gender_guesser',
        'pkg_resources'
    ],
    package_data={'tdf.labnum.tdfAnonymizer': ["resources/*"]}
)
