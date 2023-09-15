"""
fichier regroupant les fonctions "coeur" pour les calculs de tva de shopify
"""

# library
from typing import Tuple

from loguru import logger
import pandas as pd


# constantes
# liste des colonnes du fichier de sortie 'écriture comptable'
LIST_COLS_EC = ["JOURNAL", "DATE", "GENERAL", "AUXILIAIRE", "REFERENCE", "LIBELLE", "DEBIT", "PAYS"]


def log_pays_absent(df_key: pd.DataFrame, df_0: pd.DataFrame) -> None:
    """fonction pour identifier les pays absent du fichier 'tva_pays.xlsx'"""

    list_used = df_0["pays"].unique()
    list_key = df_key["pays"].unique()

    list_absent = [country for country in list_used if country not in list_key]

    if list_absent:
        logger.warning(f"Les pays suivants sont absents de 'tva_pays.xlsx' : {list_absent}")

    else:
        logger.info("Tous les pays dans le fichier à traiter sont définis dans 'tva_pays.xlsx'")


def find_pays_tva_seuil(df_0, seuil):
    """fonction pour identifier les pays ayant dépasser le seuil de tva"""

    # on somme par pays et on compare au seuil
    df_grouped = df_0.groupby(["pays"], as_index=False)["total_ht"].sum()
    df_seuil = df_grouped[df_grouped["total_ht"] >= seuil]

    return df_grouped, df_seuil["pays"].tolist()


def add_tva_colonne(df_key, df_0, list_pays_seuil_tva, quiet=False):
    """fonction pour ajouter la colonne TVA en fonction du seuil de vente"""

    df_1 = df_0.copy()
    list_pays_tva_definies = df_key["pays"].unique()

    # on crée la colonne et on applique la tva FR par défaut (car si pays < seuil alors tva fr)
    tva_fr = df_key.loc[df_key["pays"] == "France", "tva"].values[0]
    df_1.loc[:, "tva"] = tva_fr

    # pour chaque pays qui a dépassé le seuil de tva, on lui applique associe le bon taux
    for country in list_pays_seuil_tva:
        if country in list_pays_tva_definies:
            tva_country = df_key.loc[df_key["pays"] == country, "tva"].values[0]
            df_1.loc[df_1["pays"] == country, "tva"] = tva_country

        # si le pays a dépassé le seuil mais n'est pas dans la liste df_key, on log le pb
        elif (country not in list_pays_tva_definies) and (not quiet):
            logger.error(
                f"Le pays '{country}' est absent de 'tva_pays.xlsx' alors qu'il a dépassé le seuil de vente. La TVA française est appliquée par défaut."
            )

        # pour quand on rappelle la fonction avec df_bilan et éviter d'avoir 2 fois le msg loggé
        elif (country not in list_pays_tva_definies) and (quiet):
            pass

        else:
            logger.critical("ERREUR - impossible: on est sortie des if/elif :/")

    return df_1


def create_df_ecriture_comptable(df_0):
    """fonction pour créer le fichier d'écriture comptable - vectorisé"""

    # on crée le df vide avec les colonnes d'écriture comptable
    df_1 = pd.DataFrame(columns=LIST_COLS_EC)
    df_1_ht = pd.DataFrame(columns=LIST_COLS_EC)

    # pour HT
    df_1_ht.loc[:, "JOURNAL"] = df_0["type_transaction"]
    df_1_ht.loc[:, "DATE"] = df_0["date"]
    df_1_ht.loc[:, "GENERAL"] = 707200
    df_1_ht.loc[:, "AUXILIAIRE"] = ""
    df_1_ht.loc[:, "REFERENCE"] = df_0["id_vente"].astype("int64")
    df_1_ht.loc[:, "LIBELLE"] = (
        "HT - ref_command" + ": " + df_0["ref_command"].astype("int64").astype(str)
    )
    df_1_ht.loc[:, "DEBIT"] = df_0["total_ht"]
    df_1_ht.loc[:, "PAYS"] = df_0["pays"]

    # pour TVA
    df_1_tva = df_1_ht.copy()
    df_1_tva.loc[:, "GENERAL"] = 445712
    df_1_tva.loc[:, "LIBELLE"] = (
        "TVA - ref_command" + ": " + df_0["ref_command"].astype("int64").astype(str)
    )
    df_1_tva.loc[:, "DEBIT"] = df_0["total_ht"] * df_0["tva"]

    # pour TTC
    df_1_ttc = df_1_ht.copy()
    df_1_ttc.loc[:, "GENERAL"] = 411000
    df_1_ttc.loc[:, "LIBELLE"] = (
        "TTC - ref_command" + ": " + df_0["ref_command"].astype("int64").astype(str)
    )
    df_1_ttc.loc[:, "DEBIT"] = df_0["total_ht"] + df_0["total_ht"] * df_0["tva"]

    # on regroupe et trie
    df_1 = pd.concat([df_1_ht, df_1_tva, df_1_ttc], axis=0)
    df_1 = df_1.sort_values(["DATE", "REFERENCE", "LIBELLE"], ascending=[True, True, True])
    df_1 = df_1.reset_index(drop=True)

    return df_1


def create_dfs_ec_shopify(
    df_key: pd.DataFrame, df_0: pd.DataFrame, seuil: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """function to compose the core functions to compute the TVA and écritures comptables"""

    # vérification si tous les pays ont leur TVA définies dans le fichier de paramètres
    log_pays_absent(df_key, df_0)

    # on identifie les pays dont la somme des ventes > seuil_tva
    df_bilan, lst_pays = find_pays_tva_seuil(df_0, seuil)
    # on calcule la TVA pour chaque pays
    df_0 = add_tva_colonne(df_key, df_0, lst_pays)
    # on crée le df de sortie et on calcule la tva sur 3 lignes (TTC, HT, TVA)
    df_ec = create_df_ecriture_comptable(df_0)

    # idem pour bilan (pour avoir facilement le taux appliqué en résumé)
    df_bilan = add_tva_colonne(df_key, df_bilan, lst_pays, quiet=True)
    df_bilan = df_bilan.rename(columns={"tva": "tva_appliquée"})

    return df_ec, df_bilan


# end
