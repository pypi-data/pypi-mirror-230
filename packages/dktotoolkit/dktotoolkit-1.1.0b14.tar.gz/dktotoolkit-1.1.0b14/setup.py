from setuptools import setup
import os
import sys
import glob

# Variables ##########################################
package_name = "dktotoolkit"

url_page = "https://discord-catho.frama.io"
url_git = "https://framagit.org"

# Components of the package
packages = [package_name,
            f"{package_name}.parserhtml",
            f"{package_name}.discordify",
            f"{package_name}.aelf",
            f"{package_name}.str",
            f"{package_name}.verbose",
            f"{package_name}.envvar",
            ]
# To import, fe, libraries to package must acceded, but not be called
package_dir = []
# Additionnal datas, not sources
package_data = {}
# #####################################################
#
# THEN : DO NOT MODIFY
# --------------------
# #####################################################

def parse_version(path:str='./modulename/__version__.py'):
    about = {}
    with open(path, "r") as f:
        exec(f.read(), about)
    #endWith
    return about
#endDef


def parse_requirements(path:str='./requirements.txt'):
    """
    Parser le fichier requirements.txt

- Nommer les categories de modules pour separer l'indispensable au package de ceux pour le deploiement et la doc
- Les tags qui ne sont pas indiques ici seront consideres comme principaux
> # tag
> package == X.Y.Z

- Pour creer une nouvelle categorie :
-- ajouter "CATEGORIE_TAG" (1)
-- ajouter un indicateur "CAT" (4) et init le dico "extra_requires" avec cet indicateur
-- Ajouter dans (5) :
--- "elif line.lower() in CATEGORIE_tags: ..."
--- "elif add_to == _CAT: ..."

:param str path: Chemin/fichier.txt a parser
:return: packages, extras_require
:rtypes: (list, dict)
    """

    # (1) Categories
    doc_tags = [
        '# doc', '# document', '# documentation',
        '#doc', '#document', '#documentation',
    ]

    test_tags = [
        '# cover', '# coverage', '# test', '# tests', '# unit test', '# unit-test', '# unit tests', '# unit-tests',
        '#cover', '#coverage', '#test', '#tests', '#unit test', '#unit-test', '#unit tests', '#unit-tests',
    ]

    pypi_tags = [
        '# twine', '# pypi',
        '#twine', '#pypi',
    ]
    ## (2) Lire le contenu du fichier requirements.txt
    if not os.path.exists(path):
        return [], {}
    #
    with open(path, 'r') as file:
        lines = file.readlines()
    #endWith

    ## (3) Variables pour stocker les lignes dans les sections appropriées
    packages_lines = []
    doc_lines = []
    extras_pkg = {}

    ## (4) Indicateur pour déterminer si les lignes doivent être ajoutées à la section "packages" ou "doc"
    _packages = "packages"
    _doc = "doc"
    _test = "test"
    _pypi = "upload"

    extras_pkg[_doc] = []
    extras_pkg[_test] = []
    extras_pkg[_pypi] = []

    add_to = _packages # Valeur par defaut

    ## (5) Parcourir les lignes du fichier requirements.txt
    for line in lines:

        line = line.strip()

        if line.lower() in doc_tags:

            add_to = _doc

        elif line.lower() in test_tags:

            add_to = _test

        elif line.lower() in pypi_tags:

            add_to = _pypi

        elif line.startswith('#'):

            add_to = _packages

        elif add_to == _packages:

            packages_lines.append(line.split("#")[0].strip())

        elif add_to == _doc:

            extras_pkg[_doc].append(line.split("#")[0].strip())

        elif add_to == _test:

            extras_pkg[_test].append(line.split("#")[0].strip())

        elif add_to == _pypi:

            extras_pkg[_pypi].append(line.split("#")[0].strip())

        else:

            raise ValueError(f"{add_to} not in [{_packages}, {_doc}]")

        #endIf
    #endFor

    ## Convertir les lignes en arguments de setup()
    packages = [line.split(' ')[0] for line in packages_lines]
    extras_require = {k:[e for e in v if e] for k,v in extras_pkg.items() if k}

    return packages, extras_require
#endDef


def find_scripts(script_dir="./scripts"):

    if os.path.exists(script_dir):
        return [e for e in glob.glob(os.path.join(script_dir, "*.py"))] # .replace(".py", "")
    #endIf

    return []
#


def prepareSetup():
    try:
        import sphinx
    except ImportError:
        sphinxInstalled=False
    else:
        sphinxInstalled=True
    #endTry

    if not sphinxInstalled:
        sys.stderr.write(f"> Warning, Sphinx is not installed ; I'll try it.\n")
    #endIf

    # Chemin du repertoire ...........................................
    here = os.path.abspath(os.path.dirname(__file__))

    # Lecture du requirements.txt ....................................
    packages_requirements, extras_require = parse_requirements(path=os.path.join(here, 'requirements.txt'))

    # Lecture du __version__.py ......................................
    path_about = os.path.join(here, package_name, "__version__.py")
    if os.path.exists(path_about):
        about = parse_version(path=path_about)
    else:
        raise ValueError(f"Path not exists: {path_about}")
    #

    ## Creation de variables
    url = f'{url_page}/{about["__git_name__"]}'
    project_urls = {
        'Source Code': f'{url_git}/{about["__git_group__"]}/{about["__git_name__"]}',
    }

    # Setup ..........................................................
    setupkw = {}

    # Metadata
    setupkw["name"] = str(about["__pkg_name__"])
    setupkw["version"] = str(about["__version__"])
    setupkw["license"] = str(about["__license__"])
    setupkw["copyright"] = str(about["__copyright__"])
    setupkw["url"] = url
    setupkw["project_url"] = project_urls
    setupkw["author"] = str(about["__author__"])
    setupkw["author_email"] = str(about["__author_email__"])
    setupkw["description"] = str(about["__description__"])
    setupkw["keywords"]=str(about["__keywords__"])

    # Content
    setupkw["packages"]=packages #*package_dir]
    try:
        setupkw["packages_dir"]=package_dir
    except NameError:
        setupkw["packages_dir"]=[]
        print(">>> NO PKG DIR")
    #
    try:
        setupkw["package_data"]=package_data
    except NameError:
        setupkw["package_data"]=[]
        print(">>> NO PKG DATA")
    #
    try:
        setupkw["scripts"]=find_scripts()
        #find_scripts()  # generate env/bin/scriptname.py
    except NameError:
        setupkw["scripts"]=[]
        print(">>> NO SCRIPT")
    #

    # Requirements :
    setupkw["python_requires"]=str(about["__python_requires__"])
    setupkw["install_requires"]=packages_requirements
    setupkw["extras_require"]=extras_require

    # Classifiers: cf https://pypi.org/classifiers/
    setupkw["classifiers"]=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: French",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ]

    # No entry point, use scripts

    return setupkw

#endIf


if __name__ == '__main__':
    setupkw = prepareSetup()
    setup(**setupkw)
