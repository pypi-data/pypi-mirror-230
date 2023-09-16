from bs4 import BeautifulSoup, Tag

def _remove_duplicate_tags(html, max_iterations=15, remove_tag_no_content=False):
    """
    Remplace les balises en double par une seule occurrence de la même balise, en préservant l'ordre et la hiérarchie des balises imbriquées.

    :param str html: Le code HTML à traiter.
    :param bool remove_tag_no_content: Supprimer les tags sans contenu, SAUF LES BR ! NON TESTE
    :param int max_iterations: Max iteration to remove duplicates (default: 15)
    :return: Le code HTML avec les balises en double remplacées.
    :rtype: str
    """
    def remove_duplicates(tag, tag_types_encountered):
        if isinstance(tag, Tag):
            # Check if the tag type has already been encountered in the current recursion
            if not tag.name in tag_types_encountered:
                # If it hasn't been encountered, mark it as encountered and continue
                tag_types_encountered.add(tag.name)
                if str(tag.name) == "b" and tag.b is not None:
                    tag.b.unwrap()
                elif str(tag.name) == "i" and tag.i is not None:
                    tag.i.unwrap()
                elif str(tag.name) == "u" and tag.u is not None:
                    tag.u.unwrap()
                elif str(tag.name) == "strong" and tag.strong is not None:
                    tag.strong.unwrap()
                #
            #

            # Recursively call the function on children
            for child in tag.contents:
                remove_duplicates(child, tag_types_encountered.copy())  # Use a copy of the set to avoid changing parent's set
            #
        #
    #

    soup = BeautifulSoup(html, 'html.parser')

    remove_duplicates(soup, set())
    u = soup
    v = None
    i = 0
    while u != v and i < max_iterations:
        v = u
        remove_duplicates(soup, set())
        u = soup
        i += 1
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

    return str(soup)




if __name__ =="__main__":
    s = '<b><i><b><i>Hello, <b>world!</b></i></b></i></b>'

    print(">START")
    print(">INPUT")
    print(s)
    print(">======================== 1")
    o = _remove_duplicate_tags(s)
    print(">======================== 2")
    print(">RESULT:")
    print(o)
    print(">END")
