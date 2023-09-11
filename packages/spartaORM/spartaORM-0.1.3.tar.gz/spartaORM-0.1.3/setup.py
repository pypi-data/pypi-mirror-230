from setuptools import setup, find_packages

setup(
    name="spartaORM",
    py_modules=["spartaORM"],
    version="0.1.3",
    license="MIT",
    description="Simple ORM for Sparta",
    author="Arun Kumar",
    author_email="arun.kumar@swimming.org.au",
    url="https://gitlab.com/arun-ak/sparta-database-orm",
    packages=find_packages(),
    install_requires=["alembic", "sqlalchemy", "psycopg2"],
    classifiers=["Topic :: Software Development :: Build Tools",],
)
