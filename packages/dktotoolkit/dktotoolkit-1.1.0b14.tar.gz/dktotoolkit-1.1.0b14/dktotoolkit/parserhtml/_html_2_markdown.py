import traceback
from bs4 import BeautifulSoup
import sys
#try:
#    from dktotoolkit import discordify
#except:

if __name__=="__main__":
    import os
    sys.path.insert(0, os.path.abspath('..'))
    from function_recursive import recurs_function
    from discordify import discordify
else:
    from ..function_recursive import recurs_function
    from ..discordify import discordify, discordify_dict
#end
#

def _convert_html_to_markdown(
        data,
        recurs:bool=False,
        verbose:bool=False,
        debug:bool=False,
        discord:bool=False,
        **kwargs)->str:
    """Convert HTML (string) to Markdown (string)

    :param str|list|dict data: Input datas
    :param bool recurs: Use recursivity (if list, dict)
    :param bool inplace: (False) Replace self.data and return None
    :param bool debug: raise errors
    :param bool kwargs[DiscordMarkdownConverter]: see DiscordMarkdownConverter.DiscordDefaultOptions and MarkdownConverter.DefaultOptions
    """

    # Nettoyage kwargs
    discord_key=kwargs.get("discord_key", None)

    if kwargs :
        kwargs={k:v for k,v in kwargs.items() if k != "discord_key"}

        discord_format_keys = ['discordwrap','discordwrap_width', "discordwrap_keeplines", "discord_key"]
        additionnal_kwargs=set(kwargs.keys())-set(discord_format_keys)
        if additionnal_kwargs and (verbose or debug):
            t = traceback.format_list(traceback.extract_stack())
            sys.stderr.write("> WARNING Unexpected kwargs"+str(additionnal_kwargs)+", but not critical\n")
            sys.stderr.write("".join(t))
            if debug :
                raise
            #
        #
    #endIf

    if discord:
        return discordify_dict(data, key=discord_key,**kwargs)
    #

    if isinstance(data,(int, float, bool)) or data is None:
        return data
    #

    if not isinstance(data,str):

        recurs_datas = recurs_function(
            _convert_html_to_markdown,
            data=data,
            recurs=True,
            **kwargs
        )

        return recurs_datas
    # endIf

    markdown = discordify(data, **kwargs)

    if isinstance(markdown, (list, tuple)):
        return [e for e in markdown if e]
    #

    if markdown.strip()[0:2] == "\n":
        markdown = markdown.strip()[2:]
    #

    return markdown.strip()

# endDef






if __name__=="__main__":
    import sys
    html_content = 'Coucou<h3>Heading 3</h3>Hello'
    expected_output = '''Coucou

### Heading 3
Hello'''
    markdown = _convert_html_to_markdown(html_content)

    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")

    print()

    html_content = '<ul><li>Item 1</li><li>Item 2</li></ul>'
    expected_output = """- Item 1
- Item 2"""
    markdown = _convert_html_to_markdown(html_content)
    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")
    print()

    html_content = '<b>Bold and <i>italic</i></b>'
    expected_output = '**Bold and *italic***'
    markdown = _convert_html_to_markdown(html_content)
    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")
    print()

    html_content = '<b>Bold and <i>italic</i> two <i>five</i></b> three'
    expected_output = '**Bold and *italic* two *five*** three'
    markdown = _convert_html_to_markdown(html_content)
    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")
    print()

    html_content = '<b>Bold and <i>italic</i> two</b> three <u><b>four</b></u>'
    expected_output = '**Bold and *italic* two** three __**four**__'
    markdown = _convert_html_to_markdown(html_content)
    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")
    print()

    html_content = '<b>Bold and <i>italic</i> and, <u>underline 1</u></b>'
    expected_output = '**Bold and *italic* and, __underline 1__**'
    markdown = _convert_html_to_markdown(html_content)
    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")
    print()

    html_content = '<b>Bold and <i>italic and <u>underline 1</u></i></b>'
    expected_output = '**Bold and *italic and __underline 1__***'
    markdown = _convert_html_to_markdown(html_content)
    print("h",html_content)
    sys.stdout.write("++\n"+expected_output+'\n++\n')
    sys.stdout.write("--\n"+markdown+'\n--\n')
    print("=" if expected_output==markdown else "X")
    print()

    print("GROS TEST")
    html_content = [{'id_deroule': 0, 'cle_element': 'se_signer_office', 'titre_particulier': None, 'ajouter_doxologie': None, 'element_defaut': '1', 'titre': None, 'texte': '<i>(Faire le signe de Croix, au nom du P&egrave;re, du Fils et du Saint Esprit, pendant <b>Dieu, viens &agrave; mon aide</b>)</i>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 1, 'cle_element': 'introduction', 'titre_particulier': 'Introduction', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p><b>V/</b> Dieu, viens &agrave; mon aide,<br/><b>R/</b> Seigneur, &agrave; notre secours.</p> <p>Gloire au P&egrave;re, et au Fils et au Saint&hyphen;Esprit,<br/>au Dieu qui est, qui &eacute;tait et qui vient,<br/>pour les si&egrave;cles des si&egrave;cles.<br/>Amen. (All&eacute;luia.)</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 2, 'cle_element': 'hymne', 'titre_particulier': 'Hymne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': 'Esprit de Dieu, tu es le feu', 'texte': 'Esprit de Dieu, tu es le feu,<br/>Patiente braise dans la cendre,<br/>A tout moment pr&ecirc;te &agrave; surprendre<br/>Le moindre souffle et &agrave; sauter<br/>Comme un &eacute;clair vif et joyeux<br/>Pour consumer en nous la paille,<br/>Eprouver l&rsquo;or aux grandes flammes<br/>Du brasier de ta charit&eacute;.<br/><br/>Esprit de Dieu, tu es le vent,<br/>O&ugrave; prends&hyphen;tu souffle, &agrave; quel rivage?<br/>&Eacute;lie se cache le visage<br/>A ton silence fr&eacute;missant<br/>Aux temps nouveaux tu es donn&eacute;,<br/>Soupir du monde en esp&eacute;rance,<br/>Partout pr&eacute;sent comme une danse,<br/>Eclosion de ta libert&eacute;.<br/><br/>Esprit de Dieu, tu es ros&eacute;e<br/>De joie, de force et de tendresse,<br/>Tu es la pluie de la promesse<br/>Sur une terre abandonn&eacute;e.<br/>Jaillie du Fils ressuscit&eacute;,<br/>Tu nous animes, source claire,<br/>Et nous ram&egrave;nes vers le P&egrave;re,<br/>Au rocher de la v&eacute;rit&eacute;.<br/>', 'editeur': 'CNPL', 'auteur': 'CFC', 'reference': None}, {'id_deroule': 3, 'cle_element': 'antienne_1', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Votre tristesse deviendra joie. All&eacute;luia.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 4, 'cle_element': 'psaume_1', 'titre_particulier': 'Psaume', 'ajouter_doxologie': 'True', 'element_defaut': 'aelf', 'titre': None, 'texte': '<p><b>1 </b> Quand le Seigneur ramena les capt<u>i</u>fs &agrave; Sion,<b>&ast;</b><br/>nous &eacute;ti<u>o</u>ns comme en r&ecirc;ve\xa0!</p><p><b>2 </b> Alors notre bouche &eacute;tait pl<u>e</u>ine de rires,<br/>nous poussi<u>o</u>ns des cris de joie\xa0; <b>&plus;</b><br/>alors on disait parm<u>i</u> les nations\xa0:<br/>&laquo;\xa0Quelles merveilles fait pour e<u>u</u>x le Seigneur\xa0!\xa0&raquo;\xa0<b>&ast;</b><br/><b>3 </b> Quelles merveilles le Seigne<u>u</u>r fit pour nous\xa0:<br/>nous &eacute;ti<u>o</u>ns en grande f&ecirc;te\xa0!<br/><br/><b>4 </b> Ram&egrave;ne, Seigne<u>u</u>r, nos captifs,<br/>comme les torr<u>e</u>nts au d&eacute;sert.<br/><br/><b>5 </b> Qui s<u>&egrave;</u>me dans les larmes<br/>moiss<u>o</u>nne dans la joie\xa0: <b>&plus;</b><br/><b>6 </b> il s&#8217;en va, il s&#8217;en v<u>a</u> en pleurant,<br/>il j<u>e</u>tte la semence\xa0; <b>&ast;</b><br/>il s&#8217;en vient, il s&#8217;en vi<u>e</u>nt dans la joie,<br/>il rapp<u>o</u>rte les gerbes.</p>', 'editeur': None, 'auteur': None, 'reference': '125'}, {'id_deroule': 5, 'cle_element': 'doxologie', 'texte': 'INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER'}, {'id_deroule': 6, 'cle_element': 'antienne_1', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Votre tristesse deviendra joie. All&eacute;luia.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 7, 'cle_element': 'antienne_2', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Que nous vivions, que nous mourions, c&#8217;est pour le Seigneur, all&eacute;luia.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 8, 'cle_element': 'psaume_2', 'titre_particulier': 'Psaume', 'ajouter_doxologie': 'True', 'element_defaut': 'aelf', 'titre': None, 'texte': '<b>1 </b> Si le Seigneur ne b&acirc;t<u>i</u>t la maison,<br/>les b&acirc;tisseurs trav<u>a</u>illent en vain\xa0; <b>&ast;</b><br/>si le Seigneur ne g<u>a</u>rde la ville,<br/>c&#8217;est en vain que v<u>e</u>illent les gardes.<br/><br/><b>2 </b> En vain tu dev<u>a</u>nces le jour,<br/>tu retardes le mom<u>e</u>nt de ton repos, <b>&plus;</b><br/>tu manges un p<u>a</u>in de douleur\xa0: <b>&ast;</b><br/>Dieu comble son bien&hyphen;aim<u>&eacute;</u> quand il dort.<br/><br/><b>3 </b> Des fils, voil&agrave; ce que d<u>o</u>nne le Seigneur,<br/>des enfants, la r&eacute;comp<u>e</u>nse qu&#8217;il accorde\xa0; <b>&ast;</b><br/><b>4 </b> comme des fl&egrave;ches aux m<u>a</u>ins d&#8217;un guerrier,<br/>ainsi les f<u>i</u>ls de la jeunesse.<br/><br/><b>5 </b> Heureux l&#8217;h<u>o</u>mme vaillant<br/>qui a garni son carqu<u>o</u>is de telles armes\xa0! <b>&ast;</b><br/>S&#8217;ils affrontent leurs ennem<u>i</u>s sur la place,<br/>ils ne seront p<u>a</u>s humili&eacute;s.<br/>', 'editeur': None, 'auteur': None, 'reference': '126'}, {'id_deroule': 9, 'cle_element': 'doxologie', 'texte': 'INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER'}, {'id_deroule': 10, 'cle_element': 'antienne_2', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Que nous vivions, que nous mourions, c&#8217;est pour le Seigneur, all&eacute;luia.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 11, 'cle_element': 'antienne_3', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Tout vient de lui, tout est pour lui, tout est en lui\xa0! Gloire &agrave; Dieu dans les si&egrave;cles\xa0!</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 12, 'cle_element': 'psaume_3', 'titre_particulier': 'Psaume', 'ajouter_doxologie': 'True', 'element_defaut': 'aelf', 'titre': None, 'texte': '<p><b>12 </b> Rendons gr&acirc;ce &agrave; Die<u>u</u> le P&egrave;re, <b>&plus;</b><br/>lui qui nous a donn&eacute;<br/>d&rsquo;avoir part &agrave; l&rsquo;h&eacute;rit<u>a</u>ge des saints, <b>&ast;</b><br/>d<u>a</u>ns la lumi&egrave;re.<br/><br/><b>13 </b> Nous arrachant &agrave; la puiss<u>a</u>nce des t&eacute;n&egrave;bres, <b>&plus;</b><br/>il nous a plac&eacute;s<br/>dans le Royaume de son F<u>i</u>ls bien&hyphen;aim&eacute;\xa0: <b>&ast;</b><br/><b>14 </b> en lui nous avons le rachat,<br/>le pard<u>o</u>n des p&eacute;ch&eacute;s.<br/><br/><b>15 </b> Il est l&rsquo;image du Die<u>u</u> invisible, <b>&plus;</b><br/>le premier&hyphen;n&eacute;, avant to<u>u</u>te cr&eacute;ature\xa0: <b>&ast;</b><br/><b>16 </b> en lui, tout fut cr&eacute;&eacute;,<br/>dans le ci<u>e</u>l et sur la terre.<br/><br/>Les &ecirc;tres vis<u>i</u>bles et invisibles, <b>&plus;</b><br/>puissances, principaut&eacute;s,<br/>souverainet<u>&eacute;</u>s, dominations, <b>&ast;</b><br/>tout est cr&eacute;&eacute; par lu<u>i</u> et pour lui.<br/><br/><b>17 </b> Il est avant to<u>u</u>te chose,<br/>et tout subs<u>i</u>ste en lui.<br/><br/><b>18 </b> Il est aussi la t<u>&ecirc;</u>te du corps, la t&ecirc;te de l&rsquo;&Eacute;glise\xa0: <b>&plus;</b><br/>c&rsquo;est lui le commencement,<br/>le premier&hyphen;n<u>&eacute;</u> d&rsquo;entre les morts, <b>&ast;</b><br/>afin qu&rsquo;il ait en to<u>u</u>t la primaut&eacute;.<br/><br/><b>19 </b> Car Dieu a jug&eacute; bon<br/>qu&rsquo;habite en lui to<u>u</u>te pl&eacute;nitude <b>&ast;</b><br/><b>20 </b> et que tout, par le Christ,<br/>lui soit enf<u>i</u>n r&eacute;concili&eacute;,<br/><br/>faisant la paix par le s<u>a</u>ng de sa Croix, <b>&ast;</b><br/>la paix pour tous les &ecirc;tres<br/>sur la t<u>e</u>rre et dans le ciel.</p>', 'editeur': None, 'auteur': None, 'reference': 'CANTIQUE (Col 1)'}, {'id_deroule': 13, 'cle_element': 'doxologie', 'texte': 'INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER'}, {'id_deroule': 14, 'cle_element': 'antienne_3', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Tout vient de lui, tout est pour lui, tout est en lui\xa0! Gloire &agrave; Dieu dans les si&egrave;cles\xa0!</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 15, 'cle_element': 'pericope', 'titre_particulier': 'Parole de Dieu', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': 'Ce que nous proclamons, c&#8217;est, comme dit l&#8217;&Eacute;criture, ce que personne n&#8217;avait vu de ses yeux ni entendu de ses oreilles, ce que le cœur de l&#8217;homme n&#8217;avait pas imagin&eacute;, ce qui avait &eacute;t&eacute; pr&eacute;par&eacute; pour ceux qui aiment Dieu. Et c&#8217;est &agrave; nous que Dieu, par l&#8217;Esprit, a r&eacute;v&eacute;l&eacute; cette sagesse.', 'editeur': None, 'auteur': None, 'reference': '1 Co 2, 9&hyphen;10a'}, {'id_deroule': 16, 'cle_element': 'repons', 'titre_particulier': 'R&eacute;pons', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p><b>R/</b> Toi, le jour sans cr&eacute;puscule,<br/>Esprit de Dieu pour notre terre,<br/>Comment es&hyphen;tu<br/>La nuit la plus obscure\xa0?</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 17, 'cle_element': 'antienne_magnificat', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Un feu br&ucirc;le en moi : l&rsquo;amour qui consumait les proph&egrave;tes et les amis du Christ, all&eacute;luia.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 18, 'cle_element': 'cantique_mariale', 'titre_particulier': None, 'ajouter_doxologie': 'True', 'element_defaut': 'aelf', 'titre': 'Cantique de Marie', 'texte': '<p><b>47 </b> Mon &acirc;me ex<u>a</u>lte le Seigneur,<br/>exulte mon esprit en Die<u>u</u>, mon Sauveur !<br/><br/><b>48 </b> Il s&rsquo;est pench&eacute; sur son h<u>u</u>mble servante ;<br/>d&eacute;sormais, tous les &acirc;ges me dir<u>o</u>nt bienheureuse.<br/><br/><b>49 </b> Le Puissant fit pour m<u>o</u>i des merveilles ;<br/>S<u>a</u>int est son nom !<br/><br/><b>50 </b> Son amour s&rsquo;&eacute;t<u>e</u>nd d&rsquo;&acirc;ge en &acirc;ge<br/>sur ce<u>u</u>x qui le craignent ;<br/><br/><b>51 </b> D&eacute;ployant la f<u>o</u>rce de son bras,<br/>il disp<u>e</u>rse les superbes.<br/><br/><b>52 </b> Il renverse les puiss<u>a</u>nts de leurs tr&ocirc;nes,<br/>il &eacute;l<u>&egrave;</u>ve les humbles.<br/><br/><b>53 </b> Il comble de bi<u>e</u>ns les affam&eacute;s,<br/>renvoie les r<u>i</u>ches les mains vides.<br/><br/><b>54 </b> Il rel&egrave;ve Isra<u>&euml;</u>l, son serviteur,<br/>il se souvi<u>e</u>nt de son amour,<br/><br/><b>55 </b> de la promesse f<u>a</u>ite &agrave; nos p&egrave;res,<br/>en faveur d&rsquo;Abraham et de sa r<u>a</u>ce, &agrave; jamais.</p>', 'editeur': None, 'auteur': None, 'reference': 'Lc 1'}, {'id_deroule': 19, 'cle_element': 'doxologie', 'texte': 'INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER   INSERER'}, {'id_deroule': 20, 'cle_element': 'antienne_magnificat', 'titre_particulier': 'Antienne', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Un feu br&ucirc;le en moi : l&rsquo;amour qui consumait les proph&egrave;tes et les amis du Christ, all&eacute;luia.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 21, 'cle_element': 'intercession', 'titre_particulier': 'Intercession', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Avec ceux qui ont reçu les premiers dons de l&#8217;Esprit, prions Dieu d&#8217;achever notre sanctification\xa0:</p><br/><b>R/</b> <p>Dieu notre P&egrave;re, exauce&hyphen;nous</p><br/><p>Dieu tout&hyphen;puissant, qui as &eacute;lev&eacute; le Christ aupr&egrave;s de toi,<br/>&mdash;\xa0donne &agrave; chacun de reconna&icirc;tre sa pr&eacute;sence dans l&#8217;&Eacute;glise.</p><br/><p>P&egrave;re, dont le Fils unique est notre chemin,<br/>&mdash;\xa0accorde&hyphen;nous de le suivre par&hyphen;del&agrave; la mort.</p><br/><p>Envoie ton Esprit Saint dans le cœur des croyants,<br/>&mdash;\xa0pour qu&#8217;il vienne irriguer leur d&eacute;sert.</p><br/><p>Par la puissance de l&#8217;Esprit, conduis le cours des temps,<br/>&mdash;\xa0pour que la face de la terre en soit renouvel&eacute;e.</p><br/><p>P&egrave;re qui nous aimes sans mesure,<br/>&mdash;\xa0ach&egrave;ve en toi la communion des saints.</p>', 'editeur': None, 'auteur': None, 'reference': None}, {'id_deroule': 22, 'cle_element': 'oraison', 'titre_particulier': 'Oraison', 'ajouter_doxologie': None, 'element_defaut': 'aelf', 'titre': None, 'texte': '<p>Dieu qui as donn&eacute; &agrave; saint Justin, ton martyr, de trouver dans la folie de la croix la connaissance incomparable de J&eacute;sus Christ, accorde&hyphen;nous, par son intercession, de rejeter les erreurs qui nous entourent et d&rsquo;&ecirc;tre affermis dans la foi.</p>', 'editeur': None, 'auteur': None, 'reference': None}]
    markdown = _convert_html_to_markdown(html_content, discordwrap=True, discordwrap_width=120)
    sys.stdout.write("--\n"+str(markdown)+'\n--\n')
    print()
