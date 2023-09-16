import os
import sys
import traceback
from typing import Union

def compatMode(
        original_name: str,
        compatibility_list: Union[str, list, tuple] = [],
        verbose: bool=True,
        errors_are_critical: bool=False,
        replace_in_kwargs: bool=False,
        **kwargs):
    """
    Legacy ! Please use :func:`compat_mode` instead.
"""
    if kwargs and not compatibility_list:
        a_proper, kwargs_proper = compat_mode("compatibility_list", ["list_var",], **kwargs)
        if a_proper:
            compatibility_list, kwargs = a_proper, kwargs_proper
        # endIf
    # endIf

    sys.stderr.write("Legacy ! Please use dktotoolkit.compat_mode instead.\n")

    return compat_mode(
        original_name = original_name,
        compatibility_list = compatibility_list,
        verbose = verbose,
        errors_are_critical = errors_are_critical,
        replace_in_kwargs = replace_in_kwargs,
        **kwargs)


def compat_mode(
        original_name: str,
        compatibility_list: Union[str, list, tuple],
        verbose: bool=True,
        errors_are_critical: bool=False,
        replace_in_kwargs: bool=False,
        **kwargs
):
    """
compat_mode Function
--------------------

    Add a compatibility mode.

    :param str original_name: Name of the original variable.
    :param list compatibility_list: Names detecting compatibility.
    :param bool verbose: Verbose (default: True).
    :param bool errors_are_critical: Raise an error if True (default: False);
                                    look at the environment variable ERRORS_ARE_CRITICAL.
    :param bool replace_in_kwargs: Return the original name in kwargs instead of return
                                  (default: False)
    :param dict kwargs: All passing arguments.

    :return: value for the original variable, kwargs (compatibility deleted)
            if not replace_in_kwargs
            else kwargs (compatibility deleted but original name instead)
    :rtype: tuple (2 elements).

Usage Example
~~~~~~~~~~~~~

Here's an example of how to use the `compatMode` function:

.. code-block:: python

    from dktotoolkit import compatMode

    def main(a, **kwargs):

        if kwargs and not a:
            a_proper, kwargs_proper = compatMode("a", ["b", "c", "d"], **kwargs)      # a_proper = 1, kwargs_proper = {e:2}
            if a_proper:
                a, kwargs = a_proper, kwargs_proper
            # endIf
         # endIf

         ...

    # endDef
    main(b=1, e=2)
    """

    if (kwargs.get("debug") or kwargs.get("stop_mode")) and not errors_are_critical:
        a_proper, kwargs_proper = compat_mode("errors_are_critical", ["debug","stop_mode"], **kwargs)
        if a_proper:
            errors_are_critical, kwargs = a_proper, kwargs_proper
        # endIf
    # endIf

    out = None

    if not kwargs and replace_in_kwargs:
        return {}
    elif not kwargs:
        return None, {}
    #

    errors_are_critical = bool(errors_are_critical or os.environ.get("ERRORS_ARE_CRITICAL", False))

    if isinstance(compatibility_list, str):
        compatibility_list = [compatibility_list]
    elif not isinstance(compatibility_list, (list, tuple)):
        raise ValueError(f"compat_mode: compatibility_list={compatibility_list} must be a list, a tuple or a string !\n")
    #

    for compatibility in compatibility_list:
        if compatibility in kwargs:
            t = traceback.format_list(traceback.extract_stack())
            message = f"{''.join(t)}> Compatibility mode:\n"
            message += f"> Please correct the file {t[-4]}\n"
            message += f"> Prefer '{original_name}' than '{compatibility}' in the call\n"
            sys.stderr.write(message)

            if out:
                message = "> Not the first time...\n"
                message += "I'll change, but please check your input parameters\n"
                sys.stderr.write(message)
            #
            out = kwargs[compatibility]
            del kwargs[compatibility]

    if errors_are_critical:
        raise ValueError("compat_mode: errors are critical! Please make the corrections\n")
    #

    if replace_in_kwargs and out:
        kwargs[original_name] = out
        return {k:v for k,v in kwargs.items() if k not in compatibility_list}
    elif replace_in_kwargs:
        return kwargs
    else:
        return out, kwargs
    #
