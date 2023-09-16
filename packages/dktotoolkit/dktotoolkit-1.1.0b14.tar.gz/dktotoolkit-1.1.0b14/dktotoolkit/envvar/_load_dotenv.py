import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from ..list import castList
from ..str import str2digit
from ..verbose import write_message

def load_dotenv(
        filename: str = "./.env",
        erase_variable: bool = False,
        verbose: bool = False
) -> None:
    """Load .env file

:param str filename: Path and name of the file (default: ./.env)
:param bool erase_variable: Erase variable if already exists (default: False)

:return: Only add the values (str) inside environment variables
:rtypes: None
"""
    write_message(
        F"Load environment file : {filename}",
        verbose=verbose,
        prefix_verbose=">"
    )

    with open(filename, 'r') as f:

        lines = f.readlines()

        for line in lines:

            linesplit = line.split("\n")[0].split("#")[0].split("=")

            if len(linesplit) > 1:

                var = linesplit[0].strip()
                val = linesplit[1].strip().replace(",", ":").replace(";", ":")

                if os.environ.get(var, False) and not erase_variable:
                    msg = F"{var} = {os.environ.get(var)} "
                    msg += "(already set, erase_variable)\n"
                    write_message(msg, verbose=verbose, prefix_verbose="load_env>")
                # endIf

                msg = F"load_env> {var} = {val} : "
                write_message(msg, verbose=verbose, prefix_verbose="load_env>", not_break=True)
                if "\"" in val:
                    msg = "warning : character \" "
                    msg += "in content (character removed)"
                    write_message(msg, verbose=verbose, level='warning')
                    val = val.replace("\"", "")
                else:
                     write_message("Done", verbose=verbose)
                # endIf

                if not os.environ.get(var, False) or not erase_variable:
                    # On ne peut avoir en var que des str
                    os.environ[var] = val
                # endIf

            # endIf
        # endFor
    # endWith

    sys.stdout.write("\n")

    # TODO : ajouter valeurs par defaut si pas presentes !

# endDef


