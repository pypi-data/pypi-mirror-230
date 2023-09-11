# Sparta Database ORM

The database migrations and ORM for Sparta has been developed as a python package module. The name of the package modeule is `spartaORM` (https://pypi.org/project/spartaORM/). The benefits of maintaining the database ORM for sparta are as follows:

- Reduce duplication of code in the sparta application.
- Proper overview of the database migrations.
- Defining the possible values for datatypes as ENUM in one place. 
- Additional functionality such as query, filter, update entries using relationships.
- Combined insights of race analysis.
- Ease of use.
- Can easily be used in other project just by adding the package module.

## How to use

- Open the `requirements.txt` of the project.
- Add a new line.
- Add `spartaORM` and for specific version to be used, add `spartaORM==0.0.1`

## How to publish
In oder to publish a new version of the package, follow the below steps:

1. Push all the necessary changes for the new version into the `master` branch.
2. Navigate to `Releases` (Deployments -> Releases) and click `New release`.
3. Enter proper version number and title for the new release and click `create release`.
4. Once the release is done, you will find the details of the new release in the `Releases` page.
5. Right click the `Source code (tar.gz)` and click `copy link address`.
6. Navigate to the `setup.py`, which can be found in the root folder of the project.
7. Replace `download_url` with the copied link address and save it.
8. Run `python setup.py sdist`
9. Then, run `twine upload dist/*` (If `twine` is not installed, please intall it `pip install twine`)

That it. The new version will be published and you can check it by navigating to https://pypi.org/project/spartaORM/

## Where to find schema diagram

The schema diagram are designed using the tool called https://dbdiagram.io/d/64f1a4bc02bd1c4a5ecb65f3