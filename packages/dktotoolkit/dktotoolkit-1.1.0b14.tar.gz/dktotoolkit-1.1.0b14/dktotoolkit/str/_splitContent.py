import logging
import re

# Source (Rewrote): https://framagit.org/1sixunhuit/discord_breviaire/-/blob/release_lav/formatStrings.py?ref_type=heads

def split_long_sentences(sentence, max_length):
    """
    Divise une phrase longue en sous-phrases plus courtes.

    :param str sentence: La phrase longue à diviser.
    :param int max_length: La longueur maximale permise pour chaque sous-phrase.
    :return: Une liste de sous-phrases découpées.
    :rtype: list[str]
    """

    try:
        long_sentences = re.findall(r'(?:\d[,]|[^,])*(?:[,]|$)', sentence)
    except re.error as e:
        raise ValueError("Erreur lors de l'application de l'expression régulière") from e
    #

    sentence_chunk = [""]
    subsentence_index = 0
    word_index = None

    for part in long_sentences:
        if len(part) >= max_length:
            words = [word + " " for word in part.split(" ")]
            word_index = 0
            word_group = [""]

            for word in words:
                if len(word_group[word_index]) + len(word) >= max_length:
                    word_index += 1
                    word_group.append("")

                word_group[word_index] += word

            sentence_chunk += word_group
            subsentence_index += word_index + 1

        elif len(sentence_chunk[subsentence_index]) + len(part) >= max_length:
            subsentence_index += 1
            sentence_chunk.append("")

        if word_index is None:
            sentence_chunk[subsentence_index] += part

        if word_index is None:
            sentence_chunk[subsentence_index] += part

    return sentence_chunk


def split_long_paragraph(paragraph, max_length):
    """
    Divise un paragraphe en phrases plus courtes.

    :param str paragraph: Le paragraphe à diviser.
    :param int max_length: La longueur maximale permise pour chaque phrase.
    :return: Une liste de phrases découpées.
    :rtype: list[str]
    """
    try:
        sentences = re.findall(r'(?:\d[.\!\?\:\;]|[^.\!\?\:\;])*(?:[.\!\?\:\;]|$)', paragraph)
    except re.error as e:
        raise ValueError("Erreur lors de l'application de l'expression régulière") from e
    #

    split_sentences = []

    for sentence in sentences:
        if not sentence:
            continue
        elif len(sentence) >= max_length:
            split_sentences += split_long_sentences(sentence, max_length)
        else:
            split_sentences.append(sentence)
        #

    return split_sentences


def split_content(content, max_length:int=0, regroup:bool=False, adaptative_length:bool=True):
    """
    Divise un contenu textuel en parties plus courtes tout en respectant les longueurs maximales.

    :param str content: Le contenu textuel à diviser.
    :param int,optional max_length: La longueur maximale permise pour chaque partie. (Default: 0)
    :param bool regroup: Regrouper
    :param bool adaptative_length: Adapter la longueur de la découpe
    :return: Une liste de parties découpées.
    :rtype: list[str]
    """
    if isinstance(max_length, str) and max_length.isdigit():
        max_length=int(max_length)
    elif not isinstance(max_length, int):
        raise ValueError(max_length)
    #

    if max_length < 0:
        raise ValueError(max_length)
    elif max_length == 0:
        return content
    #

    newline_br = "<br/>" in content
    sep="<br/>" if newline_br else (
        "\n\n" if "\n\n" in content else "\n" )

    lines_temp = [e + sep for e in content.split(sep)]

    split_content = [""]
    paragraph_index = 0

    for line in lines_temp:
        if len(line) >= max_length:
            split_paragraphs = split_long_paragraph(line, max_length)
            split_content += split_paragraphs
        else:
            if len(split_content[paragraph_index]) + len(line) >= max_length:
                paragraph_index += 1
                split_content.append("")

            split_content[paragraph_index] += line
        #
    #
    regroup=True

    if regroup:

        try:
            if (adaptative_length and
                len(split_content) == 2 and
                len(split_content[0]) > 1.5*len(split_content[1]) ):
                max_length = int(0.6 * max_length)
                logging.debug("Adaptative length not working !")
            #
        except:
            print("ERROR ADAPTATIVE MESH")
            raise
        #
        ltmp = [""]
        for e in split_content:
            if (len(ltmp[-1])+len(e)+len(sep)) < max_length:
                ltmp[-1] += sep+e
            else:
                ltmp += [e,]
            #
        #
        split_content=ltmp
    #

    return [e for e in split_content if e not in ["\n", ""]]
#

if __name__=="__main__":
    content = "Your long content here..."
    result = split_long_content(content)
    print(result)
#
