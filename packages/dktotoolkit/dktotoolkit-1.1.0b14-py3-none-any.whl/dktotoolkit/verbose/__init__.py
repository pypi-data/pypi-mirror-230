import sys
import logging
import inspect

def write_message(
        message: str = None,
        verbose: bool = False,
        prefix_verbose: str = "",
        logger: logging.Logger = None,
        level: str = 'info',
        not_break: bool = False,
        caller_context: bool = True
)->None:
    """
    Écrit un message sur la sortie standard ou dans un logger avec différents niveaux de journalisation.

    :param str message: Le message à écrire.
    :param bool verbose: Si True, le message sera écrit sur la sortie standard. (default: False)
    :param logging.Logger logger: Le logger où écrire le message. (default: None)
    :param str level: Le niveau de journalisation ('info', 'warning', 'error', 'critical'). (default: 'info')
    :param bool not_break: Si True, le message ne passera pas à la ligne. (default: False)

    :return: La fonction renvoie la sortie de la fonction d'écriture correspondante.
    :rtype: Varies
    """

    if caller_context:
        caller = inspect.stack()[1]
        module = inspect.getmodule(caller[0])
        module_name = module.__name__
        line_number = caller[2]
        function_name = caller[3]
        message_with_info = f"{module_name}.{function_name},{line_number}: {message}"
    else:
        message_with_info = message
    #
    
    if verbose or logger is None:
        logger = logging.getLogger('dktotoolkit.write_message')
        logger.setLevel(logging.INFO)
    #
    writer = getattr(logger, level)

    add_new_handler = not logger.hasHandlers()

    if add_new_handler:
        formatter = logging.Formatter(f'{prefix_verbose if verbose else ""}%(message)s')
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
    #

    old_terminators = [None for e in logger.handlers]
    # old_formater = l.handlers[0].formatter._fmt
    rg = range(len(logger.handlers))
    for i in rg:
        old_terminators[i] = logger.handlers[i].terminator
        (logger.handlers[i]).terminator = ' ' if not_break else '\n'
    #

    writer(message_with_info)

    for i in rg:
        (logger.handlers[i]).terminator = old_terminators[i]
    #

    if add_new_handler:
        logger.removeHandler(logger.handlers[0])
    #

    return

#
