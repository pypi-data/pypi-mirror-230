"""
fonctions pour vérifier la validité du fichier d'entrée avant de charger
"""

from pathlib import Path
from typing import Optional

# library
from loguru import logger
import pandas as pd


# constantes
# dictionnaire de colonnes à utiliser pour le fichier shopify + leur renommage
DICT_COLS_SHOPIFY = {
    "Référence de commande": "ref_command",
    "Identifiant de vente": "id_vente",
    "Date": "date",
    "Type de transaction": "type_transaction",
    "Pays de facturation": "pays",
    "Quantité nette": "quantite_nette",
    "Ventes brutes": "ventes_ht",
    # "Réductions": "reductions",
    # "Retours": "retours",
    # "Ventes nettes": "ventes_nettes",
    "Expédition": "expedition_ht"
    # "Taxes": "taxes",
    # "Ventes totales": "ventes_totales"
}


def try_load_xlsx(name_f, path_xlsx):
    """fonction pour charger le fichier et en même temps vérifier la validité avec try/except"""

    # on se sert des checks de read_excel() pour optimiser check & load
    try:
        df_0 = pd.read_excel(
            io=path_xlsx, header=1, usecols=DICT_COLS_SHOPIFY.keys(), parse_dates=["Date"]
        )
        # on check aussi si le df est vide car, contrairement à read_csv, read_excel ne remonte pas
        # d'erreur 'pd.errors.EmptyDataError'...
        if not df_0.empty:
            return df_0
        else:
            logger.critical(f"ERREUR : le fichier '{name_f}' est vide")
            return None

    except FileNotFoundError:
        logger.critical(f"FileNotFoundError : le fichier '{name_f}' n'existe pas")
        return None
    except ValueError:
        logger.critical(f"ValueError: le fichier '{name_f}' n'est pas conforme au format attendu")
        return None


def clean_df(name_f, df_0):
    """clean df avant son utilisation"""

    # si le test précédent 'try_load_xlsx()' précédent a échoué, on revoie None.
    if df_0 is None:
        return None

    # on essaye de cleaner le fichier
    try:
        df_1 = df_0.copy()
        df_1 = df_1.rename(columns=DICT_COLS_SHOPIFY)
        df_1 = df_1.dropna(axis=0, how="all")
        df_1["date"] = df_1["date"].dt.date
        # on divise par 1000 pour avoir des euros
        df_1[["ventes_ht", "expedition_ht"]] = df_1[["ventes_ht", "expedition_ht"]] / 1000
        # on somme les ventes pour expeditions pour avoir la somme totales HT par pays
        df_1["total_ht"] = df_1["ventes_ht"] + df_1["expedition_ht"]

        return df_1

    # si ça ne fonctionne pas, c'est que le format a un souci
    except KeyError:
        logger.critical(f"KeyError: le fichier '{name_f}' n'est pas conforme au format attendu")
        return None


# Optional and not "|" for python 3.8/3.9 compatibility
def try_load_and_clean(path_xlsx: Path) -> Optional[pd.DataFrame]:
    """function to compose the try, load and clean functions"""

    name_file_in = path_xlsx.name
    df_1 = try_load_xlsx(name_file_in, path_xlsx)
    df_2 = clean_df(name_file_in, df_1)

    return df_2


# end
