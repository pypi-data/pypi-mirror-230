# -*- coding: utf-8 -*-

from textwrap import wrap
import markdownify as md

if __name__=="__main__":
    import os, sys
    sys.path.insert(0, os.path.abspath('..'))
    from functions import compat_mode
    from str import split_content
else:
    from ..functions import compat_mode
    from ..str import split_content
#end

# https://github.com/matthewwithanm/python-markdownify/blob/develop/markdownify/__init__.py


RETURN = "return"
RETURN_BACKSLASH = "returnbackslash"

class DiscordMarkdownConverter(md.MarkdownConverter, object):
    """Overcharge markdownify.MarkdownConverter (https://github.com/matthewwithanm/python-markdownify)"""

    class DiscordDefaultOptions:

        # options de Markdownify
        bullets = '-+*'

        discordwrap = True
        discordwrap_width = 1012

        wrap = False  # J'utilise ensuite ma fonction str.split_content

        heading_style=md.ATX

        # options supplementaires
        newline_style=RETURN

        escape_gt=True
        escape_backslash=True

        keep_only_br=True

        bold_asterisks=True
        bold_plus=True
    #

    # Surcharge init
    def __init__(self, **options):

        if options.get("wrap", False):
            raise ValueError("Do not use here, but 'discordwrap' instead for 'str.split_content'")
        #

        super().__init__(**{**md._todict(self.DiscordDefaultOptions), **options})
    #

    # Reecriture fonctions
    def convert_hn(self, n, el, text, convert_as_inline):
        if convert_as_inline:
            return text
        #

        style = self.options['heading_style'].lower()
        text = text.rstrip()
        if style == md.UNDERLINED and n <= 2:
            line = '=' if n == 1 else '-'
            return self.underline(text, line)
        hashes = '#' * n
        if style == md.ATX_CLOSED:
            return '%s %s %s\n\n' % (hashes, text, hashes)
        #

        if n == 1:
            return '\n\n%s %s\n\n' % (hashes, text)
        #
        return '\n%s %s\n\n' % (hashes, text)
    #

    def convert_blockquote(self, el, text, convert_as_inline):

        if convert_as_inline:
            return text

        return '\n' + (md.line_beginning_re.sub('>>> ', text) + '\n\n') if text else ''
    #

    def convert_quote(self, el, text, convert_as_inline):

        if convert_as_inline:
            return text

        return '\n' + (md.line_beginning_re.sub('> ', text) + '\n\n') if text else ''
    #

    def convert_br(self, el, text, convert_as_inline):
        if convert_as_inline:
            return ""

        if self.options['newline_style'].lower() == md.BACKSLASH:
            return '\\\n'
        elif self.options['newline_style'].lower() == RETURN:
            return "\n"
        elif self.options['newline_style'].lower() == RETURN_BACKSLASH:
            return "\\n"
        else:
            return '  \n'
        #
    #
    def escape(self, text):
        if not text:
            return ''
        #
        if self.options['escape_backslash']:
            text = text.replace(r'\\', r'\\\\')
        #
        if self.options['escape_asterisks'] and self.options['bold_asterisks']:
            text = text.replace('*', r'**\***')
        elif self.options['escape_asterisks']:
            text = text.replace('*', r'\*')
        elif self.options['bold_asterisks']:
            text = text.replace('*', r'*****')
        #
        if self.options['escape_underscores']:
            text = text.replace('_', r'\_')
        #
        if self.options['escape_gt']:
            text = text.replace('>', r'\>')
        #
        if self.options['bold_plus']:
            text = text.replace('+', r'**+**')
        #
        return text
    #

    # Nouvelles fonctions
    convert_u = md.abstract_inline_conversion(lambda self: 2 * '_')

#


def discordify(
        html,
        keep_only_br=True,
        **options):
    """Convert to Markdown with particular options for Discord norm (wrapping until 1020 characters, espace symbols, ...)
:param str html: Input string (HTML)
:param bool keep_only_br: Delete "\n" in text if <br/>  (default: True)
:param bool options[discordwrap]: Wrap the content (default: False)
:param int options[discordwrap_width]: Number of characters when wrapping text (default: max_characters)
:param bool options[discordwrap_keeplines]: Split on new lines (default: False)
"""

    keep_only_br = not(options.get("discordwrap_keeplines", not keep_only_br))

    if keep_only_br and ("<br/>" in html or "<br>" in html or "<br />" in html):
        html = html.replace("\n", "")
    #
    out = DiscordMarkdownConverter(**options).convert(html)
    out = out.replace("\xa0", " ")

    if options.get('discordwrap', False):
        mylist = split_content(out, max_length=options.get("discordwrap_width", 0))
        return mylist
    #

    return out
#

def discordify_dict(data, key=None, **kwargs):
    """Discordify on a key or a full dictionnary
:param dict(|list|tuple|str|int|float|bool) data: Content to "discordify"
:param str key: key of the value be discordify ; if None, discordify all values of the dict. Default: None
"""
    if kwargs and key is None:
        key_proper, kwargs_proper = compat_mode("key", ["discord_key",], **kwargs)
        if key_proper:
            key, kwargs = key_proper, kwargs_proper
        #
    #

    if isinstance(data, (str, int, float, bool)) or data is None:
        return data
    elif isinstance(data, (list, tuple)):
        return [
            discordify_dict(data=e,
                            key=key,
                            **kwargs
                            )
            for e in data
        ]

    elif isinstance(data, dict) and key is not None and not data.get(key, False):
        return {
            k:discordify_dict(data=v,
                              key=key,
                              **kwargs
                              )
            for k,v in data.items()
        }

    elif isinstance(data, dict):
        return {
            k:
            discordify(v, **kwargs) if (k==key or key is None)
            else v
            for k,v in data.items()
        }
    else:
        raise ValueError(f"unknown type of datas {type(datas)}")
    #
