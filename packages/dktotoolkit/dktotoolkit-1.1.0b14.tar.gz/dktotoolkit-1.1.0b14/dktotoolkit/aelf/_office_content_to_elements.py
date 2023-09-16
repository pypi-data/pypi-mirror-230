import logging

def aelf_officecontent_to_elements(office_content, hunfolding:list=[], skip_empty_items:bool=True):
    """
:param dict office_content: datas from AELF API, v1
:param list hunfolding: Hunfolding (usefull to repeat the "antienne" for exemple, optionnal)
:param bool skip_empty_item: skip empty items, or keep it inside the hunfolding ?
:return: hunfolding (or "hunfolding-like") with datas from AELF
:rtypes: list
    """

    datas = []

    if not hunfolding:
        for k,v in office_content.items():
            dico = {}
            dico["element_key"] = k
            if isinstance(v, dict):
                dico.update(v)
            elif isinstance(v, str):
                dico["texte"] = v
            elif v is None:
                logging.warning(f"office_content_to_element (NOT hunfolding : 1): {k} value is None here !")
                if skip_empty_items:
                    continue
                #
            elif not v:
                if skip_empty_items:
                    continue
                #
                logging.warning(f"office_content_to_element (NOT hunfolding : 2): {k} : v = {v} here and not 'default_element_key' or skip_empty_item!")
                dico["texte"] = None
            else:
                raise ValueError(f"Unexpected case here (0) for {k} : {type(v)} -- {v} !")
            # endIf
            datas += [dico,]
        # endFor

        return datas

    # endIf

    for element in hunfolding:

        if not "key_name" in element.keys():
            raise ValueError(f"Error in the database (1) : 'key_name' not found in {element}!")
        #

        d = office_content.get(element["key_name"], None)

        if (
                d is None and
                (element.get("default_element_key") or
                 (not skip_empty_items) ) ):

            element["texte"] = None

        elif (
                not d and
                (element.get("default_element_key") or
                (not skip_empty_items) ) ):
            # Par exemple, si on a d = [] (ca arrive de temps a autre aux complies...)
            logging.warning(f"office_content_to_element (hunfolding : 1): {element['key_name']} has no value. It type is {type(d)} and the value: {d} !")

            element["texte"] = None

        elif not d:

            logging.warning(f"office_content_to_element (hunfolding : 2): {element['key_name']} : d = {d} here and not 'default_element_key' or skip_empty_item!")
            continue

        elif isinstance(d, str):

            element["texte"] = d

        elif (
                isinstance(d, dict) and
                (not (d.get("texte") or d.get("text") or d.get("content"))) ):

            logging.warning(f"office_content_to_element (hunfolding : 3): {element['key_name']} value is None here and not 'default_element_key'  ! {d}.")

            if skip_empty_items:
                continue
                #pass
            else:
                element["texte"] = None
            #

        elif isinstance(d, dict):

            if d.get("text") :
                d["texte"] = d["text"]
            elif d.get("content"):
                d["texte"] = d["content"]
            #

            element.update({k:v for k, v in d.items() if k not in ["text", "content"]})

        else:

            raise ValueError(f"Unexpected case here (1) ! {element.get('default_element_key', None)} {element['key_name']} -- {type(d)}::: {d}")

        #
        datas += [element,]
    #

    return datas
#
