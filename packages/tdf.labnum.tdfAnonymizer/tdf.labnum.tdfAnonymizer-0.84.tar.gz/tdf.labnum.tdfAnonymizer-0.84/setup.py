from setuptools import setup, find_packages

setup(
    name='tdf.labnum.tdfAnonymizer',
    version='0.84',
    packages=find_packages(),
    install_requires=[
        'nltk',
        'pydantic',
        'faker',
        'pandas',
        'gender_guesser',
    ],
    package_data={'tdf.labnum.tdfAnonymizer': ["resources/*"]}
)
