from setuptools import setup, find_packages

setup(
        name='move_data',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        # List any dependencies your package requires to run
        'snowflake-connector-python[pandas]',
        'python-dotenv',
        'pandas',
        'pygsheets',
        'google-cloud-storage',
    ],
)

