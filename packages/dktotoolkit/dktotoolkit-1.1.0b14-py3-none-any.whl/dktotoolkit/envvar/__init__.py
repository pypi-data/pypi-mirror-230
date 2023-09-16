import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from ..list import castList
from ..str import str2digit

from ._load_dotenv import load_dotenv
from ._task_watch_dotenv import task_watch_dotenv_file

all = [
    "load_dotenv",
    "task_watch_dotenv_file"
]

def assign_envvar(var, envvar, defaultvar, useenv:bool=True):
    """Assigner une valeur à une variable ; les 3 sont obligatoires
:param var: Variable : sera assignee en priorite
:param envvar: Nom de la variable d'environnement : priorité 2
:param defaultvar: Valeur par défaut, si var=None et useenv : sera utilisé
"""

    if var is not None:
        return var
    elif useenv:
        return os.environ.get(envvar, defaultvar)
    else:
        return defaultvar
    #
#


def getEnvironVar(varname: str, digit: bool = False):
    """Get environ variable

:param str varname: Name of the variable
:param bool digit: Try to convert to digit  (default: False)
"""

    if varname is None:
        return None
    # endIf

    var = os.environ.get(varname)

    for char in [":", ";", ","]:  # separators
        if char in var:

            L = castList(var, char, digit=digit)
            if L is not None:
                return L
            # endIf
        # endIf
    # endFor

    if digit:
        return str2digit(var.strip())
    else:
        return str(var.strip())
    # endIf

# endDef


def getTimesReminder(
        dotenv_timevar: str = "REMINDER",
        outdico: bool = False
):
    """Recuperer une liste d'heures
REMINDER=hhmmss:hhmmss
"""
    # If no tzinfo is given then UTC is assumed.
    tzone = ZoneInfo(getEnvironVar("TZONE", "Europe/Paris"))

    tuples_dotenv = getEnvironVar(dotenv_timevar)
    dico_out = {}

    if tuples_dotenv is None:
        return []
    # endIf

    for office, time in tuples_dotenv:
        l_hourMinSec = ["", "", ""]
        i = 0
        for char in time:

            if char.isdigit():
                l_hourMinSec[i] = l_hourMinSec[i] + char
                justchange = False
            elif not justchange:
                i += 1
                justchange = True
            # endIf
        # endFor

        l_hourMinSec = [int(e) if e else 0 for e in l_hourMinSec]
        d_hourMinSec = {
            "hour": l_hourMinSec[0],
            "minute": l_hourMinSec[1],
            "second": l_hourMinSec[2]
        }

        dico_out[office] = d_hourMinSec
        dico_out[office]["time"] = datetime.time(**d_hourMinSec, tzinfo=tzone)

    # endFor

    if outdico:
        return dico_out
    else:
        return [v["time"] for k, v in dico_out.items()]
    # endIf

# endDef

