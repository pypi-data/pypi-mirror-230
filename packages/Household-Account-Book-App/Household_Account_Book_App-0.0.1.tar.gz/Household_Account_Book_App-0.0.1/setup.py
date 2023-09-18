from setuptools import setup, find_packages

setup(
    name='Household_Account_Book_App',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'pydantic',
        'sqlalchemy',
        'uvicorn'
    ],
    entry_points={
        'console_scripts': [
            'Household_Account_Book_App = Household_Account_Book_App.main:run'
        ],
    }
)
