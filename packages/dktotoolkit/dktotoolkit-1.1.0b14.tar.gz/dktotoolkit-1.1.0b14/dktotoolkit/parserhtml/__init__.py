# -*- coding: utf-8 -*-
import sys

from ._decode_html_special_chars import _decode_html_special_chars
from ._clean_html import _clean_html
from ._keep_only_selected_tags import _keep_only_selected_tags
from ._remove_duplicate_tags import _remove_duplicate_tags
from ._replace_span_with_bold_and_italic import _replace_span_with_bold_and_italic

from ._html_2_markdown import _convert_html_to_markdown

class ParserHTML:
    def __init__(self,
                 data_input:str=None,
                 convertEmptyNone:bool=False,
                 convert_keys:bool=False,
                 skip_values:list=[]
                 ):
        """Parser un texte, une liste, un dictionnaire

:param str|int|float|list|tuple|dict data_input: Donnee a convertir (recursif)
:param bool convertEmptyNone: If True return None if field empty, if False return ''
:param bool convert_keys: If type(data_input) is dict : If True parse keys of dict  else not parse keys
:param list|str|int skip_values: Values to skip if data_input is list (int/list[int]) or dict (str/list[str]) ; UNIQUEMENT AVEC DICT ET CONVERT_KEY=FALSE POUR LE MOMENT
"""

        self.data = data_input
        self.convertEmptyNone = convertEmptyNone
        self.convert_keys = convert_keys
        self.skip_values = [skip_values,] if not isinstance(skip_values, list) else skip_values
        # https://www.journaldunet.com/solutions/dsi/1195751-accents-caracteres-speciaux-html/

    def get_data(self, **kwargs):
        """
        Retourner les donnees
:return: self.data
:rtypes: dict|list|str
        """
        if kwargs:
            sys.stderr.write("dktotoolkit.ParserHTML.get_data : unexpected kwargs !\n")
        #

        return self.data
    #

    def utf8_to_html(self, *args, **kwargs):
        sys.stderr.write("> parserHHTML compat-mode (utf8_to_html) ! ")

        if "displayMarkdown" in kwargs:
            sys.stderr.write("Delete displayMarkdown argument. ")
            kwargs = {key: value for key, value in kwargs.items() if key != 'displayMarkdown'}
        #
        if "cleanHTML" in kwargs:
            sys.stderr.write("Delete cleanHTML argument. ")
            kwargs = {key: value for key, value in kwargs.items() if key != 'cleanHTML'}
        #

        if "convertbreaklines" in kwargs:
            sys.stderr.write("Delete convertbreaklines argument. ")
            kwargs = {key: value for key, value in kwargs.items() if key != 'convertbreaklines'}
        #
        sys.stderr.write("\n")

        if "data" in kwargs and kwargs["data"]:
            data = kwargs["data"]
            kwargs = {key: value for key, value in kwargs.items() if key != 'data'}
            return self.clean_html(content=data, *args, **kwargs)
        #endIF

        return self.clean_html(*args, **kwargs)
    #

    def html_to_utf8(self, *args, **kwargs):
        sys.stderr.write("> parserHHTML compat-mode (html_to_utf8) ! ")
        return self.clean_html(*args, **kwargs)

    def html_to_markdown(self, *args, **kwargs):
        # def utf8_to_html(self, convertbreaklines:bool=False, data:str=None, cleanHTML:bool=False, recurs:bool=False, inplace:bool=False, **kwargs)->str:

        sys.stderr.write("> parserHHTML compat-mode !   kwargs="+str(kwargs)+" // args="+str(list(args)))

        if "displayMarkdown" in kwargs:
            sys.stderr.write("Delete displayMarkdown argument. ")
            kwargs = {key: value for key, value in kwargs.items() if key != 'displayMarkdown'}
        #

        sys.stderr.write("\n")

        if "data" in kwargs and kwargs["data"]:
            data = kwargs["data"]
            kwargs = {key: value for key, value in kwargs.items() if key != 'data'}
            return self.to_markdown(html_content=data, *args, **kwargs)
        #endIF

        return self.to_markdown(*args, **kwargs)
    #


    def to_markdown(self, html_content="", inplace=False, replace_tags={}, *args, **kwargs):
        """
        Convert to markdown

        :param str html_content: html content
        :param dict replace_tags: {"span:class_=verse_number":"i", "span:chapter_number":"b"}
        :param bool inplace: replace self.data
"""

        if not html_content:
            html_content = self.data
        #

        clean_content = self.clean_html(html_content, replace_tags=replace_tags)
        md_content = self.convert_html_to_markdown(html_content=clean_content, inplace=False, *args, **kwargs)
        out = self.decode_html_special_chars(md_content)

        if inplace:
            self.data = out
            return None
        else:
            return out
        #endIf
    # endDef


    def clean_html(self, content="", replace_tags={}, inplace=False):
        """
        Nettoie le code HTML en uniformisant les balises et en convertissant les caractères spéciaux en entités HTML.
        Assure l'uniformité des valeurs pour les attributs spécifiques tels que `class`, `id`, `href`, `src` et `alt`.

        :param str content: Le code HTML à nettoyer.
        :param dict replace_tags: {"span:class_=verse_number":"i", "span:chapter_number":"b"}
        :return: Le code HTML nettoyé.
        :rtype: str
        """
        if not content:
            content = self.data
        #

        out = _clean_html(data=content, replace_tags=replace_tags)

        if inplace:
            self.data = out
            return None
        else:
            return out
        #endIf
    #

    # Static methods
    @staticmethod
    def convert_html_to_markdown(html_content, inplace=False, *args, **kwargs):
        if kwargs.get("data", False):
            print("Debug mode : convert_html_to_markdown I must not have data")
            kwargs = {key: value for key, value in kwargs.items() if key != 'data'}
        elif "data" in kwargs:
            kwargs = {key: value for key, value in kwargs.items() if key != 'data'}
        #

        return _convert_html_to_markdown(data=html_content, *args, **kwargs)
    # endDef

    @staticmethod
    def decode_html_special_chars(content, encoding='utf-8'):
        """
        Convertit les caractères spéciaux HTML en caractères spéciaux lisibles en utilisant l'encodage spécifié.

        :param str content: Le contenu HTML contenant les caractères spéciaux à convertir.
        :param str encoding: L'encodage à utiliser pour décoder les caractères spéciaux. Par défaut, c'est UTF-8.
        :return: Le contenu HTML avec les caractères spéciaux convertis en caractères lisibles.
        :rtype: str
        """

        return _decode_html_special_chars(data=content, encoding=encoding)
    # endDef


    @staticmethod
    def keep_only_selected_tags(content, tags_to_keep=['b', 'span', 'br', 'i'], delete_attributes=False):
        """
        Conserve uniquement les tags spécifiés et les caractères spéciaux dans le contenu HTML, et supprime tous les autres tags.

        :param str content: Le code HTML à traiter.
        :param list tags_to_keep: La liste des tags à conserver.
        :param bool delete_attributes: Supprimer les attributs des tags.
        :return: Le code HTML avec uniquement les tags spécifiés et les caractères spéciaux.
        :rtype: str
        """
        return _keep_only_selected_tags(
            content=content,
            tags_to_keep=tags_to_keep,
            delete_attributes=delete_attributes
        )
    # endDef


    @staticmethod
    def remove_duplicate_tags(content):
        """
        Remplace les balises en double par une seule occurrence de la même balise, en préservant l'ordre et la hiérarchie des balises imbriquées.

        :param str content: Le code HTML à traiter.
        :return: Le code HTML avec les balises en double remplacées.
        :rtype: str
        """
        return _remove_duplicate_tags(content=content)
    # endDef


    @staticmethod
    def replace_span_with_bold_and_italic(
        content,
        tag_replacements = {
            'verse_number': 'i',
            'chapter_number': 'b'
        }):
        """
        Remplace les balises <span class="XXX"> par des balises <b> ou <i> en fonction de la classe.

        :param str content: Le code HTML à traiter.
        :param dict tag_replacements: Un dictionnaire spécifiant les classes de balises <span> à remplacer et les balises de remplacement correspondantes.
                                  Par exemple, {'chapter_number': 'b', 'verse_number': 'i'}.
        :return: Le code HTML avec les balises <span> remplacées par des balises <b> ou <i>.
        :rtype: str
        """
        return _replace_span_with_bold_and_italic(
            content=content,
            tag_replacements=tag_replacements
        )
    # endDef

    # Class methods



#endClass

