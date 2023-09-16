from .str import str2digit


def replace_with_mask(arr, mask, replacement, inplace=False):
    """
    Remplace les valeurs dans un tableau selon un masque.

    :param list arr: Le tableau d'origine.
    :param list mask: Le masque indiquant les valeurs a remplacer.
    :param replacement: La valeur de remplacement.
    :param bool inplace: Indique si la modification doit etre effectuee sur place
                        (par defaut: False).
    :return: Le tableau modifie.
    :rtype: list

    """

    if len(arr) != len(mask):  # pragma: no cover
        raise ValueError("Les tableaux doivent avoir la meme longueur")
    # endIf

    if inplace:
        for i in range(len(arr)):
            if mask[i]:
                arr[i] = replacement
            # endIf
        # endFor
    else:
        new_arr = []
        for i in range(len(arr)):
            if mask[i]:
                new_arr.append(replacement)
            else:
                new_arr.append(arr[i])
        return new_arr
    # endIf

    return None
# endDef


def castList(
        var: str,
        sep: str = None,
        digit: bool = False
):
    """
    Caster une liste, a partir d'une string

    :param str var: une liste en entree
    :param str sep: le separateur de la liste
    :param bool digit: Retourner des chiffres
    :returns: A list of values

    """

    list_seps = ["::", ":", ";", ",", "|", "/", "?", "£", "$", "+"]

    if sep is None or sep not in var:
        i = 0
        while i < len(list_seps):
            if list_seps[i] in var:
                sep = list_seps[i]
                i = len(list_seps)
            # endIf
            i += 1
        # endWhile
    # endIf

    if "(" in var and ")" in var:
        sublist = [""]
        for e in var:
            if e == "(":
                sublist += ["",]
            elif e == ")":
                sublist += ["",]
            else:
                sublist[-1] += str(e)
            # endIf
        # endFor

        tr_sb_list = []
        for e in sublist:
            if not e or e in ["", sep]:
                continue
            # endIf
            tr_sb_list += [castList(e, sep=sep, digit=digit),]
        # endFor

        return [e for e in tr_sb_list if e]
    # endIf

    try:

        if isinstance(var, list) or isinstance(var, tuple):
            return var
        else:
            L = [
                str2digit(e.strip())
                if digit
                else str(e.strip())
                for e in var.split(sep)
                if str(e.strip())
            ]
            return L
        # endIf

    except ValueError:  # pragma: no cover
        L = [str(e.strip()) for e in var.split(sep) if str(e.strip())]
        return L
    except Exception as e:  # pragma: no cover
        print(e)
        raise Exception
    # endTry

    return None
# endDef



def aplatir_liste(lst, doubles:bool=False):
    resultat = []
    for element in lst:
        if isinstance(element, list):
            resultat.extend(aplatir_liste(element))
        elif element is not None and element != '':
            if doubles or element not in resultat:
                resultat.append(element)
            #
        #
    return resultat
