# library
import json
from pathlib import Path


# for compatibility with python 3.8, 3.9 and 3.10 (from https://github.com/hukkin/tomli)
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def get_pypt_version(path_pypt: Path) -> str:
    """fonction pour récupérer la version du pyproject.toml, définie ici et uniquement ici"""
    with open(path_pypt, "rb") as f:
        return tomllib.load(f)["tool"]["poetry"]["version"]


def get_config_jsonc(path_json: Path) -> dict:
    """pour charger un json avec commentaires"""
    with open(path_json, "r", encoding="utf-8") as f:
        # json as list of str
        full_json_list = f.readlines()
        # remove the comments: '//' in json
        clean_json_list = [line for line in full_json_list if not line.strip().startswith("//")]
        # join to make it 'json.loads' read
        clean_json_str = "\n".join(clean_json_list)

        return json.loads(clean_json_str)


def get_config_json(path_json: Path) -> dict:
    """pour charger un json classique"""
    with open(path_json, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


# end
