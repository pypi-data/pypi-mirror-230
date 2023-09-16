import sys
import json
import re

if __name__=="__main__":
    import os
    sys.path.insert(0, os.path.abspath('../..'))
#end

from dktotoolkit import ParserHTML, clean_json
from dktotoolkit.dict import unprefix_keys

SKIP_PARSER_INFOS=["date", "date_requete", "id_office"]
SKIP_PARSER_ELTS=["cle_element", "element_defaut", "reference", "id_office", "nom_office"]

def insert_doxologie(lst, doxo_key_name="gloria_patri"):
    """
    Insère un élément spécifique après chaque élément ayant "b" à True dans une liste de dictionnaires.

    Args:
        lst (list): La liste de dictionnaires.
    (ex: "ajouter_doxologie")
    Returns:
        list: La liste modifiée avec l'insertion de l'élément supplémentaire.
    """
    result = []
    next_id = 0
    i = 0
    for item in lst:

        item["id_deroule"] = next_id
        result.append(item)
        next_id += 1

        if doxo_key_name in item.keys() and item[doxo_key_name]:

            new_item = {"id_deroule": next_id,
                        "key_name":f"doxologie",
                        "texte": "INSERER ICI",
                        "same_page":1,
                        }
            result.append(new_item)
            next_id += 1
            i += 1

        #endIf

    #endFor

    return result
#endDef

if __name__=="__main__":
    # Exemple d'utilisation
    data = [
        {"id_deroule": 1, "ajouter_doxologie": True, "t": "coucou"},
        {"id_deroule": 2, "ajouter_doxologie": None, "t": "Bonjour"},
        {"id_deroule": 3, "ajouter_doxologie": False, "t": "Hello"},
        {"id_deroule": 4, "ajouter_doxologie": True, "t": "Bye"},
        {"id_deroule": 5, "ajouter_doxologie": False, "t": "Haa", "p": "papa"},
    ]

    modified_data = insert_doxologie(data)
    print(modified_data)
#endIf
