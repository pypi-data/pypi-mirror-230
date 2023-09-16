from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="django-venv",
    version="1.0.0",
    author="Gianluca Iavicoli",
    author_email="gianluca.iavicoli04@gmail.com",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/GianlucaIavicoli/Django-Setup",
    install_requires=["django", "mysqlclient", "colorlog", "sqlparse",
                      "asgiref", "tomli", "yapf", "zipp", "platformdirs",
                      "importlib-metadata", "ast-comments"],
    scripts=["src/django-venv", "src/database",
             "src/script.py", "src/logger.py", "src/const.py"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    license="Apache License 2.0",
    keywords="django django-environment mysql postgres cassandra scylla docker",
    project_urls={
        "Source Code": "https://github.com/GianlucaIavicoli/Django-Venv",
    },
    python_requires=">=3.8",
    zip_safe=False,
)
