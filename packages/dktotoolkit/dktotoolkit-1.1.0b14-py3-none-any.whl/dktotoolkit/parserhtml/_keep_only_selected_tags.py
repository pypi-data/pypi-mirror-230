from bs4 import BeautifulSoup, Tag, NavigableString

def _keep_only_selected_tags(content, tags_to_keep, delete_attributes=False, keep_newlines=True, encadre_avec_span=False, remove_inside=False, remove_tag_no_content=False):
    """
    Conserve uniquement les tags spécifiés et les caractères spéciaux dans le contenu HTML, et supprime tous les autres tags.

    :param str content: Le code HTML à traiter.
    :param list tags_to_keep: La liste des tags à conserver.
    :param bool delete_attributes: Supprimer les attributs des tags.
    :param bool keep_newlines: Garder les balises <p> et <br/>.
    :param bool remove_inside: Supprimer l'interieur des tags supprimés (utilise tag.decompose)
    :param bool encadre_avec_span: Encadrer avec span
    :param bool remove_tag_no_content: Supprimer les tags sans contenu, SAUF LES BR !
    :return: Le code HTML avec uniquement les tags spécifiés et les caractères spéciaux.
    :rtype: str
    """
        
    # Parse le code HTML
    soup = BeautifulSoup(content, 'html.parser')

    if keep_newlines:
        tags_to_keep.append("p")
        tags_to_keep.append("br")
        tags_to_keep.append("br/")
    #
    
    # Liste des balises à supprimer
    tags_to_remove = []

    # Liste des balises parents à conserver avec le contenu interne à supprimer
    tags_to_remove_with_content = []

    for tag in soup.find_all():
        if delete_attributes:
            tag.attrs = {}
            
        if tag.name not in tags_to_keep:
            if remove_inside:
                tag.decompose()
            else:
                tag.unwrap()
            #
        #
    #

    if remove_tag_no_content:
        # Supprime les balises sans contenu
        for tag in soup.find_all():
            if not tag.contents and tag not in tags_to_remove_with_content and tag.name != "br":
                tags_to_remove.append(tag)
            #
        #
        
        # Supprime les balises de la liste tags_to_remove
        for tag in tags_to_remove:
            tag.decompose()
        #
    #

        
    # Si encadre_avec_span est True et qu'il n'y a pas de balises autour du texte, on entoure avec span
    if encadre_avec_span and len(soup.contents) > 1:
        soup = BeautifulSoup(f'<span>{str(soup)}</span>', 'html.parser')
        
    # Récupère le code HTML nettoyé
    cleaned_html = str(soup)

    return cleaned_html


# Exemple d'utilisation
if __name__=="__main__":
    html_content = '<div><p>Hello, <b>world!</b></p><span class="special">Some <i>text</i></span></div>'
    tags_to_keep = ['b', 'span', 'br', 'i']
    cleaned_html = _keep_only_selected_tags(html_content, tags_to_keep)
    print(f"-{html_content}")
    print(f"+{cleaned_html}")
