# Copyright: (c) 2023, Michel Padovani <michel.padovani@outlook.com>
# GNU General Public License v3.0 only (see LICENSE or <https://www.gnu.org/licenses/gpl-3.0.txt>)
"""
code pour générer une écriture comptable à partir d'un extrait mensuel de Shopify.
le code calcule notamment la TVA internationale en fonction des ventes dans l'UE.

auteur: michel padovani
"""

# library
from pathlib import Path

from loguru import logger
import pandas as pd

# modules
from ecriture_shopify.core_ecriture_tva import create_dfs_ec_shopify
from ecriture_shopify.create_xlsx import xlsx_generate_file
from ecriture_shopify.load_and_clean import try_load_and_clean
from ecriture_shopify.tools.read_config import get_config_json


# configuration lib
pd.options.mode.copy_on_write = True


# config
ROOT_PATH = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(ROOT_PATH, "ecriture_shopify", "config")
CONFIG_XLSX_PATH = Path(CONFIG_PATH, "config_tva_par_pays.xlsx")
CONFIG_JSON_PATH = Path(CONFIG_PATH, "config_seuil_tva.json")

# liste des pays avec leur TVA associée
DF_TVA_PARAM = pd.read_excel(CONFIG_XLSX_PATH)
# constante clé - le seuil principal pour déterminer quelle TVA appliquer (€)
SEUIL_TVA = get_config_json(CONFIG_JSON_PATH)["SEUIL_TVA"]


# fonction coeur
def shopify_to_ec(file_input_path: Path, file_output_path: Path) -> bool:
    """Fonction principale de 'ecriture_shopify' qui encapsule le pipeline complet"""

    # start log
    logger.info("Une nouvelle génération est lancée")

    # load & clean xlsx if ok. else return None
    df_ventes = try_load_and_clean(file_input_path)

    if df_ventes is not None:
        # si fichier au bon format shopify, on le traite
        df_ecriture, df_pays_bilan = create_dfs_ec_shopify(DF_TVA_PARAM, df_ventes, SEUIL_TVA)

        # on enregistre le fichier de sortie xlsx et on sort le statut
        xlsx_generate_file(df_ecriture, df_pays_bilan, file_output_path)
        logger.success("Fin de la génération")

        return True

    else:
        # on ne log pas d'erreur car c'est déjà fait dans les sub-fonctions
        return False


# for standalone run
if __name__ == "__main__":
    # path
    path_file_input = Path("data", "input", "VENTES AVRIL SHOPIFY 04.xlsx")
    path_file_output = Path("data", "output", f"{path_file_input.stem}_généré.xlsx")

    # log
    logger.add(sink="data/local_log/local_file_{time:DD-MMM-YYYY}.log", rotation="100 MB")

    # execution
    _ = shopify_to_ec(path_file_input, path_file_output)


# end
