from setuptools import setup, find_packages

setup(
        name='move_data',
    version='0.0.4',
    packages=find_packages(),
    install_requires=[
        # List any dependencies your package requires to run
        'snowflake-connector-python[pandas]',
        'python-dotenv',
        'pandas',
        'pygsheets',
    ],
)

