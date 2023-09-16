import sys

# Vérifier la version de Python
if sys.version_info >= (3, 4):
    import html
else:
    import html.parser
#

if __name__=="__main__":
    import os
    sys.path.insert(0, os.path.abspath('..'))
    from function_recursive import recurs_function
else:
    from ..function_recursive import recurs_function
#end

def _decode_html_special_chars(data, encoding='utf-8', **kwargs):
    """
    Convertit les caractères spéciaux HTML en caractères spéciaux lisibles en utilisant l'encodage spécifié.

    :param str data: Le contenu HTML contenant les caractères spéciaux à convertir.
    :param str encoding: L'encodage à utiliser pour décoder les caractères spéciaux. Par défaut, c'est UTF-8.
    :return: Le contenu HTML avec les caractères spéciaux convertis en caractères lisibles.
    :rtype: str
    """

    if data is None or isinstance(data, (int, float, bool)):
        if kwargs.get("force_string", False):
            return str(data)
        else:
            return data
        # endIf
    # endIf

    if not isinstance(data,str):

        recurs_datas = recurs_function(
            _decode_html_special_chars,
            data=data,
            recurs=True,
            **kwargs
        )

        return recurs_datas

    #endIf
    # Vérifier si l'encodage est valide
    try:
        ''.encode(encoding)
    except LookupError:
        raise ValueError(f"Invalid encoding: {encoding}")

    # Utiliser le module approprié en fonction de la version de Python
    if sys.version_info >= (3, 4):
        decoded_content = html.unescape(data)
    else:
        parser = html.parser.HTMLParser()
        decoded_content = parser.unescape(data)

    # Si un encodage est spécifié, on décode le contenu avec cet encodage
    if encoding:
        decoded_content = decoded_content.encode(encoding).decode(encoding)

    return decoded_content
#

if __name__=="__main__":
    html_content = '&eacute; &agrave; &ccedil;'
    encoding = 'utf-888'
    decoded_html = _decode_html_special_chars(html_content, encoding=encoding)

    print(f"-{html_content}")
    print(f"+{decoded_html}")
