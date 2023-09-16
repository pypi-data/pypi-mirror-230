import sys
import json
import re

if __name__=="__main__":
    import os
    sys.path.insert(0, os.path.abspath('../..'))
#end

from dktotoolkit import compat_mode

from ._insert_doxo import insert_doxologie
from ._call_api import call_api_aelf
from ._office_content_to_elements import aelf_officecontent_to_elements

def get_aelf_office(office, date, zone="", hunfolding=[], **kwargs):
    """
:param str office: name of the office
:param str date: date, format YYYY-MM-DD
:param str zone: Zone (france, romain, ...)
:param list hunfolding: Hunfolding (usefull to repeat the "antienne" for exemple)
:return: hunfolding with datas from AELF
:rtypes: list
    """

    if kwargs and not zone:
        zone_proper, kwargs_proper = compatMode("zone", ["calendrier", "calendar"], **kwargs)
        if zone_proper:
            zone, kwargs = zone_proper, kwargs_proper
        # endIf
    # endIf

    # Get datas from AELF API
    try:
        datas_api = call_api_aelf(office_name=office, date=date, zone=zone)
    except Exception as e:
        sys.stderr.write(f"Error dktotoolkit.Office.get_office (1) : {e}"+"\n")
        raise e
    #

    # Merge datas of office from API inside hunfolding
    try:
        datas_api[office] = aelf_officecontent_to_elements(datas_api[office], hunfolding=hunfolding)
    except:
        sys.stderr.write("UNEXPECTED get_aelf_office !\n")
        raise
    #

    if not "informations" in datas_api or not datas_api["informations"]:
        raise ValueError(f"Unexpected empy 'datas_api['informations']' : please check {zone}, {date}, {office}:  {datas_api['informations']}")
    elif not office in datas_api or not datas_api[office]:
        raise ValueError(f"Unexpected empy 'datas_api[office]' : please check {zone}, {date}, {office}:  {datas_api[office]}")
    #

    if isinstance(datas_api["informations"], list) or isinstance(datas_api["informations"], tuple) and len(datas_api["informations"]) == 1:
        datas_api["informations"] = datas_api["informations"][0]
    elif isinstance(datas_api["informations"], list) or isinstance(datas_api["informations"], tuple):
        raise ValueError(f"Unexpected empy 'datas_api['informations']' (len = {len(infos)}) : please check {zone}, {date}, {office} :  {datas_api['informations']}")
    #endIf

    if hunfolding:
        datas_api[office] = insert_doxologie(datas_api[office])
    #

    return datas_api
#
