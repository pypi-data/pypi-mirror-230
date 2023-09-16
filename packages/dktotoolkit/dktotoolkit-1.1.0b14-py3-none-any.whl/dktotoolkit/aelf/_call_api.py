# -*- coding: utf-8 -*-
"""
@author: Pierre
"""

import sys
import re
import requests, json

if __name__=="__main__":
    import os
    sys.path.insert(0, os.path.abspath('../..'))
#end

from dktotoolkit.datestr import is_valid_date
from dktotoolkit.html import request_html_page

def _modify_datas(datas, requested_url):
    if 'informations' in datas:
        datas['informations']['url'] = requested_url
    #

    return datas


def call_api_aelf(
        office_name,
        date,
        zone=None,
        return_alldatas=True # retourner toutes les donnees ou juste la priere
):
    """
    Recuperer le dictionnaire de donnees d'aelf (vient de ProphetiS)

:param str office_name: nom de l'office
:param str date: jour
:param str zone: calendrier utilise
:param bool return alldatas: Retourner toutes les donnees (informations + priere) ou juste la priere
    """

    if not is_valid_date(date):
        err = "Error : needs "
        err += f"date (= {date}) in format YYYY-MM-DD"
        raise ValueError(err)
    # endIf

    if not office_name or not date or not zone:
        err = "Error : needs "
        err += f"office_name (= {office_name}), "
        err += f"date (= {date}) and zone (={zone})"
        raise ValueError(err)
    #endIf

    requested_url="https://api.aelf.org/v1/{0}/{1}/{2}".format(
        office_name,
        date,
        zone
    )

    try:
        datas = request_html_page(requested_url, format_output="json")
    except Exception as e:
        print(f"dktotoolkit.office.call_api (1) : {e} \n\n url = {requested_url}")
        raise e
    #

    if "<title>AELF — 404</title>" in datas:
        message="A parameter is wrong : page not found.\n"
        message+=f"office_name: {office_name}"+"\n"
        message+=f"date: {date}"+"\n"
        message+=f"zone: {zone}"+"\n"
        message+="\n\n"
        raise ValueError(message)
    #

    datas_from_aelf = _modify_datas(datas, requested_url)

    if return_alldatas:
        return datas_from_aelf
    else:
        return datas_from_aelf[office_name]
    #endIf

    return 1

#endDef



if __name__=="__main__":
    print(api_aelf("informations", date="2023-05-21"))
    print()
    #print(api_aelf("informations",the_day="3 juin"))
    print()
    #print(api_aelf("informations",the_day="hier"))
    print()
    #print(api_aelf("informations",the_day="avant-hier"))
    print()
