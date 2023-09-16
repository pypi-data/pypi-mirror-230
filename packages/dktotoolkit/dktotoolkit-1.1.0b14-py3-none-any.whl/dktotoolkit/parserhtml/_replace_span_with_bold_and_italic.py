from bs4 import BeautifulSoup

def _replace_span_with_bold_and_italic(
        content,
        tag_replacements={}):
    """
    Remplace les balises <span class="XXX"> par des balises <b> ou <i> en fonction de la classe.

    :param str content: Le code HTML à traiter.
    :param dict tag_replacements: Un dictionnaire spécifiant les classes de balises <span> à remplacer et les balises de remplacement correspondantes.
                                  Par exemple, {'chapter_number': 'b', 'verse_number': 'i'}.
    :return: Le code HTML avec les balises <span> remplacées par des balises <b> ou <i>.
    :rtype: str
    """
    if tag_replacements is None :
        return content
    #

    if content is None:
        return ""
    #

    soup = BeautifulSoup(content, 'html.parser')

    for span_tag in soup.find_all('span'):
        class_attr = span_tag.get('class')

        # Vérifier si la balise <span> a un attribut class
        if class_attr is not None:
            class_value = ' '.join(class_attr)

            # Vérifier si la classe est présente dans le dictionnaire de remplacements

            if class_value in tag_replacements:
                new_tag = tag_replacements[class_value]
                span_tag.name = new_tag
                del span_tag['class']
            #

    return str(soup)
