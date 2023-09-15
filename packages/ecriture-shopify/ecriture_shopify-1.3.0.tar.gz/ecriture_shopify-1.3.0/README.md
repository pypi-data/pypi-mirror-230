# ecriture-shopify

[![Test CI](https://github.com/michelpado/ecriture-shopify/actions/workflows/test_source_code.yml/badge.svg)](https://github.com/michelpado/ecriture-shopify/actions/workflows/test_source_code.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/ecriture-shopify?label=Latest%20release&color=41B3FF)](https://pypi.org/project/ecriture-shopify/)
[![PyPI - License](https://img.shields.io/pypi/l/ecriture-shopify?color=EEEEEE)](https://github.com/michelpado/ecriture-shopify/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ecriture-shopify?color=F67280)](https://pypi.org/project/ecriture-shopify/)


Génère une écriture comptable à partir d'un extrait mensuel de Shopify.<br>Avec notamment le calcul de la TVA en fonction des ventes dans les différents pays en UE.

Le coeur du traitement est en Pandas & XlsxWriter, avec l'aide de Loguru pour la partie log.


## Fonctionnement
La fonction principale du package est `shopify_to_ec`. Cette fonction encapsule le pipeline complet pour créer une écriture comptable à partir du fichier xlsx mensuel de Shopify. Le pipeline est composé de 3 étapes majeures:
* chargement, vérification et nettoyage du fichier d'entrée
* application de la TVA et génération de l'écriture comptable
* création du fichier de sortie xlsx avec une mise en forme propre

**Explication de la fonction**<br>
`shopify_to_ec` prend en argument le path du fichier d'entrée, et le path du (futur) fichier de sortie. La fonction génère et enregistre le fichier d'écriture comptable dans ce dernier et émet un booléen pour indiquer si la génération à fonctionner.

**Code:**<br>
```python
from ecriture_shopify import shopify_to_ec
status = shopify_to_ec(input_file_path, output_file_path)
```

**Définition des arguments**:
* `input_file_path`: str, path du fichier d'entrée
* `output_file_path`: str, path du fichier de sortie
* `status`: bool, _True_ si génération ok, _False_ sinon
<br><br>


## A propos
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Le projet est mené, entres autres, avec Poetry, Black, isort, Pytest et pre-commit.<br> Voir "pyproject.toml" pour la liste comptète.


## Auteur:
michel padovani


## Licence
License "GNU General Public License v3.0 only".<br>
Voir [LICENSE](https://github.com/michelpado/ecriture-shopify/blob/master/LICENSE)
