from setuptools import setup, find_packages

setup(
    name='routing_engine',
    version='0.1.10',
    packages=find_packages(),
    install_requires=[
        'jsonpath-ng>=1.5.3',
        'jsonschema>=3.2.0',
        'streamlit>=1.25.0',
        'streamlit_modal>=0.1.0',
        'psycopg2>=2.9.3',
        'asyncpg>=0.28.0',
        'waitress==2.1.2',
        'connexion[swagger-ui] >= 2.6.0',
    ],
    include_package_data=True,
    author='Annecto',
    author_email='info@annecto.com',
    description='A routing engine for Python',
    url='https://gitlab.internal.ate.lc/numbers-lookup/routing-engine',
)
