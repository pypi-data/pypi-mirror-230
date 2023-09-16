import sys
import re
from datetime import date, timedelta, datetime
import traceback

from .exceptions import ParseError

def is_valid_date(date_str:str, date_format:str="yyyy-mm-dd", check_sep:bool=True):
    """Verifier qu'une date est au bon format
:param str date_str: Date a verifier
:param str date_format: Format de la date (default: yyyy-mm-dd)
:param bool check_sep: Reconnaissance du separateur egalement, ou non

:return: Vrai si la date est dans le bon format, Faux sinon
:rtypes: bool
"""

    # Vérification de la longueur de la date et du format
    if len(date_str) != len(date_format):
        return False

    # Vérification des séparateurs si nécessaire
    if check_sep:
        for i, char in enumerate(date_format):
            if char not in ("y", "m", "d") and date_str[i] != char:
                return False

    # Définition des correspondances entre les symboles du format et les parties de la date
    symbols = {"y": "year", "m": "month", "d": "day"}
    date_format = date_format.lower()

    if "yyyy" in date_format:
        year_digits = 4
    elif "yy" in date_format:
        year_digits = 2
    else:
        raise ValueError(f'date_format : {date_format} must have yy or yyyy')
    #

    # Extraction des parties de la date en fonction du format
    parts = {"year":"", "month":"", "day":""}

    for i, char in enumerate(date_format):
        if char in symbols:
            part = symbols[char]
            parts[part] += date_str[i]
        #
    #
    parts = {k:int(v) for k, v in parts.items()}

    # Vérification des chiffres dans les parties de la date
    try:
        datetime(**parts)
    except ValueError:
        return False

    return True

#

def _parse_month(month_in):
    """Convert month to the month number

:param str month_in: The month to parse
:return: The month number
:rtypes: str "01"-"12" for months between january-december
"""

    month = "00"  # Si on est en dehors des elements:

    all_months = {
        "01": ["janvier",   "janv", "january",  "jan",  "01", "1"],
        "02": ["fevrier",   "fev",  "february", "febr", "02", "2"],
        "03": ["mars",      "mar",  "march",            "03", "3"],
        "04": ["avril",     "avr",  "april",    "apr",  "04", "4"],
        "05": ["mai",               "may",              "05", "5"],
        "06": ["juin",              "june",             "06", "6"],
        "07": ["juillet",   "juil", "jully",    "jul",  "07", "7"],
        "08": ["aout",              "august",   "aug",  "08", "8"],
        "09": ["septembre", "sept", "september",        "09", "9"],
        "10": ["octobre",   "oct",  "october",          "10"],
        "11": ["novembre",  "nov",  "november",         "11"],
        "12": ["decembre",  "dec",  "december",         "12"]
    }

    for month_nb, values in all_months.items():
        if month_in in values:
            month = "{0:02d}".format(int(month_nb))
        # endIf
    # endFor

    return month
# endDef


def _relativeDate(date_string):
    """
    Parse a relative date (exemple "today")
"""

    if not isinstance(date_string, str):  # pragma: no cover
        raise ParseError
    # endIf

    lbeforey = ["avant-hier", "before-yesterday"]
    lyesterday = ["hier", "yesterday"]
    ltoday = ["aujourd'hui", "aujourd hui", "aujourdhui", "today"]
    ltomorrow = ["demain", "tomorrow"]
    laftert = [
        "apres demain", "après-demain", "apres-demain", "après-demain",
        "after-tomorrow", "aftertomorrow", "after tomorrow"
    ]

    today = date.today()

    if date_string.lower() in ltoday:
        the_date = today
    elif date_string.lower() in lyesterday:
        the_date = today - timedelta(days=1)
    elif date_string.lower() in lbeforey:
        the_date = today - timedelta(days=2)
    elif date_string.lower() in ltomorrow:
        the_date = today + timedelta(days=1)
    elif date_string.lower() in laftert:
        the_date = today + timedelta(days=2)
    else:
        t = traceback.format_list(traceback.extract_stack())
        msg = "".join(t)
        msg += f"toolkit.datestr : Cas non implemente : {date_string}\n"
        sys.stderr.write(msg)
        return "00-00-0000"
    # endIf

    return date2str(the_date)
# endDef


def _digitDate(
        date_string: str,
        splitDate_in: list,
        format_us: bool = False,
        verbose: bool = True
):
    """
Parse the date using a digital format, input is a list
"""

    if (isinstance(splitDate_in, list)) or (isinstance(splitDate_in, list)):
        pass
    else:  # pragma: no cover
        raise ParseError
    # endIf

    # Recuperer l'annee
    # De base, l'annee est en 3eme position, mais on va le verifier
    pos_yr_in = 2

    if len(splitDate_in) >= 2:

        # Formattage US ou francais ?
        if format_us is None:
            format_us = (len(splitDate_in[0]) == 4)
        # endIf

        if format_us:
            pos_yr_in = 0
        else:
            if len(splitDate_in) == 2:
                splitDate_in.append(str(date.today().year))
            # endIf
            pos_yr_in = 2
        # endIf

        if len(splitDate_in[pos_yr_in]) < 4:
            year = "20{0:02d}".format(int(splitDate_in[pos_yr_in]))
        else:
            year = splitDate_in[pos_yr_in]
        # endIf

    else:  # pragma: no cover
        sys.stderr.write("datestr has not days implemented yet\n")
        raise ParseError
    # endIf

    # Recuperer le jour
    if (pos_yr_in == 2) or (len(splitDate_in) < 3):
        pos_day_in = 0
    else:
        pos_day_in = 2
    # endIf

    # Recuperer le mois
    month = _parse_month(splitDate_in[1])

    if int(month) == 0:  # si on a une inversion mois/jour (car mois > 12)
        if verbose:
            msg = "pd> Warning : unknown month "
            msg += "or inversion of month and days in "
            msg += f"{date_string} : {splitDate_in} ! "
            msg += "I'll change month and day positions\n"
            sys.stderr.write(msg)
        # endIf

        pos_month_in = pos_day_in
        pos_day_in = 1

        month = _parse_month(splitDate_in[pos_month_in])

        if int(month) == 0:
            if verbose:
                msg = "pd> Warning : "
                msg += "After one more test, "
                msg += f"unknown month in {date_string} : "
                msg += f"{splitDate_in} ! Delete month value\n"
                sys.stderr.write(msg)
            # endIf

            pos_day_in = pos_month_in
        # endIf

    # endIf

    day = "{0:02d}".format(int(splitDate_in[pos_day_in]))

    return "{0:04d}-{1:02d}-{2:02d}".format(
        int(year),
        int(month),
        int(day)
    )


def parser_date(
        date_string: str = None,
        format_us: bool = None,
        verbose: bool = True
):
    """Convert an input date to a formated date  YYYY-MM-DD

:param str date_string: The date (default: None -> today)
:param bool format_us: Set input format as YYYY MM DD
:param bool verbose: Verbose (default: True)

:return: date as format YYYY-MM-DD
:rtypes: str
"""

    if date_string is None:

        date_string = date2str(date.today())

    elif isinstance(date_string, date):

        return date2str(date_string)

    elif isinstance(date_string, str):

        date_string = date_string.lower()

    else:   # pragma: no cover

        raise ParseError

    # endIf

    splitDate_in = [e for e in re.split("-|/|_| |:|\xa0", date_string) if e]

    if (
            len(splitDate_in) > 1
            and not
            ("hier" in date_string.lower())
            and not
            ("demain" in date_string.lower())
            and not
            ("avant" in date_string.lower())
            and not
            ("before" in date_string.lower())
            and not
            ("apres" in date_string.lower())
            and not
            ("après" in date_string.lower())
            and not
            ("after" in date_string.lower())
    ):

        return _digitDate(
            date_string=date_string,
            splitDate_in=splitDate_in,
            format_us=format_us,
            verbose=verbose
        )

    else:

        return _relativeDate(date_string=date_string)

    # endIf

    sys.stderr.write("Warning : unexpected case : I return a wrong date !\n")
    return "00-00-0000"
# endDef


def date2str(date):
    """Return a datetime.date in the good format

:param datetime.date adate: A date
:return: YYYY-MM-DD
:rtypes: str
"""

    return "{0:04d}-{1:02d}-{2:02d}".format(
        int(date.year),
        int(date.month),
        int(date.day)
    )
# endDef
