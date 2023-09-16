from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'FlashLearners core package'
LONG_DESCRIPTION = 'Package that holds all models and core functions/classes of FlashLearners project'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="flashlearners_core",
    version=VERSION,
    author="Folayemi Bello",
    author_email="<bello.folayemi.az@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={'': ['app/templates/flashlearners_core/*']},
    include_package_data=True,
    install_requires=["django", "python-dotenv", "django-elasticsearch-dsl",
                      'django-environ', "onesignal-sdk", 'daphne',
                      'psycopg2-binary', "uvicorn", "django-storages",
                      "boto3", 'pymysql', 'django-ckeditor-5'],
    # add any
    # additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'FlashLearners'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

    ]
)
