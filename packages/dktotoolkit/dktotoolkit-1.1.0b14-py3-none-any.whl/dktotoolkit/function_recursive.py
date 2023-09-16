import types
import sys

def recurs_function(
        function,
        data=None,
        recurs=False,
        convertEmptyNone: bool = False, #TODO : ameliorer le code ici
        convert_keys: bool = False, #TODO
        skip_values: list = [],  #TODO
        force_string: bool = False,
        **kwargs
):
    """
    Effectue une récursivité sur les données en utilisant la fonction spécifiée.

    :param function: La fonction à appliquer récursivement.
    :type function: callable
    :param data: Les données à traiter de manière récursive.
    :type data: str|int|float|list|tuple|dict|None
    :param recurs: Indique si la fonction est appelée récursivement. Ne pas spécifier directement lors de l'appel externe.
    :type recurs: bool
    :param kwargs: Arguments supplémentaires à transmettre à la fonction récursive.
    :param bool force_string: return a string for the datas if int,float,bool,None
    :returns: Les données traitées de manière récursive.
    :rtype: str|int|float|list|tuple|dict|None
    """

    if not isinstance(function, types.FunctionType) and not callable(function):
        raise ValueError(f"{function} is not a function ! {type(function)} : {isinstance(function, types.FunctionType)} : {callable(function)} - {type(data)}")
    #

    if isinstance(data, str):

        return function(data=data, **kwargs)

    elif isinstance(data, (int, float, bool)):

        if force_string:
            return function(data=str(data), **kwargs)
        else:
            return function(data=data, **kwargs)

    elif isinstance(data, list) or isinstance(data, tuple):

        l = [
            recurs_function(
                function,
                data=e, recurs=True, **kwargs)
            for e in data
        ]

        if l:
            return [l[i] if i not in skip_values else data[i] for i in range(len(l))]
        else:
            return None if convertEmptyNone else ""
        #endIf

    elif isinstance(data, dict):

        if convert_keys:
            return {
                recurs_function(function, data=k, recurs=True, **kwargs)
                if not k in skip_values else v
                :
                recurs_function(function,data=v, recurs=True, **kwargs)
                if not k in skip_values else v
                for k, v in data.items()
            }
        else:
            return {
                k
                :
                recurs_function(function,data=v, recurs=True, **kwargs)
                if not k in skip_values else v
            for k, v in data.items()
            }
        #endIf

    elif data is None:

        return None if convertEmptyNone else ""

    elif not data:

        return None if convertEmptyNone else ""

    else:

        sys.stderr.write(f"phr> datas : {type(data)} : {data}\n")

    #endIf

    return None if convertEmptyNone else ""

#endFunction
