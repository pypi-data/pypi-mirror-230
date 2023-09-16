def dict2obj(d=None, obj=None):
    """Convert nested Python dictionnary to object

:author: geeksforgeeks.org

:param dict d: input dictionnary
:param obj: a class (could be empty)
    """

    if isinstance(d, list):  # si d est une liste
        d = [dict2obj(x) for x in d]
    # endIf

    if not isinstance(d, dict):  # si d est un dico
        return d
    # endIf

    if obj is None:
        class C:
            pass
        # endClass

        obj = C()
    # endIf

    for k in d:
        obj.__dict__[k] = dict2obj(d[k])
    # endFor

    return obj

# endDef


def invert_dict(dictionary):
    """
    Inverse les clés et les valeurs d'un dictionnaire.

    Args:
        dictionary (dict): Le dictionnaire à inverser.

    Returns:
        dict: Un nouveau dictionnaire avec les clés et les valeurs inversées.
    """

    # Vérifier que le paramètre est bien un dictionnaire
    if not isinstance(dictionary, dict):
        raise TypeError("Le paramètre 'dictionary' doit être un dictionnaire.")
    # endIF

    # Vérifier que les valeurs du dictionnaire sont uniques
    if len(set(dictionary.values())) != len(dictionary):
        raise ValueError("Les valeurs du dictionnaire ne sont pas uniques.")
    #endIf

    return {value: key for key, value in dictionary.items()}
#

def unprefix_keys(dico:dict,
                  prefix:str="prefix_",
                  keep_only_prefixed:bool=True,
                  keep_prefix:bool=False,
                  revert:bool=False,
                  ):
    """
unprefix_keys
-------------

Remove prefix of a dict (for exemple :  >

:param dict dico: Input dictionnary
:param str prefix: Prefix (with an underscore if needed !)
:param bool keep_only_prefixed: Keep only prefixed var
:param bool keep_prefix: keep the prefix, or not ?

Usage Example
~~~~~~~~~~~~~

Here's an example of how to use the `compatMode` function:

.. code-block:: python

    from dktotoolkit import unprefix_keys

    dico = {"d_aa":1, "d_bb":2, "cc":4}

    unprefix_keys(dico, "d", keep_only_prefixed=True, keep_prefix=False)   # returns {'aa': 1, 'bb': 2}
    unprefix_keys(dico, "d", keep_only_prefixed=False, keep_prefix=False)  # returns {'aa': 1, 'bb': 2, 'cc': 4}
    unprefix_keys(dico, "d", keep_only_prefixed=True, keep_prefix=True)    # returns {'d_aa': 1, 'd_bb': 2}
    unprefix_keys(dico, "d", keep_only_prefixed=True, keep_prefix=False)   # returns {'cc': 4}

"""

    if revert:
        raise ValueError("dict.unprefix_keys: 'revert' argument is not implemented yet !")
    #

    if keep_only_prefixed and keep_prefix:
        return {k:v for k,v in dico.items() if k[:len(prefix)]==prefix }
    elif keep_only_prefixed:
        return {k[len(prefix):]:v for k,v in dico.items() if k[:len(prefix)]==prefix}
    elif keep_prefix and not revert:
        return dico
    elif keep_prefix and revert:
        return {}
    else:
        return {k[len(prefix):] if bool( (not revert) and k[:len(prefix)] )==prefix else k:v  for k,v in dico.items() }
