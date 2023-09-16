import os
def recursive_sql(sql_file, basepath=None):
    """
    Lire les scripts sql recursivement si .read est present
"""
    if basepath is None:
        basepath = os.path.dirname(sql_file) if os.path.dirname(sql_file) else "."
        sql_file = os.path.basename(sql_file)
    #

    # Exécution du script SQL
    sql_file=os.path.join(basepath, sql_file)
    if not os.path.exists(sql_file):
        raise ValueError(sql_file)
    #
    with open(sql_file, 'r') as fichier_sql:
        sql_script = fichier_sql.read()
        #cursor.executescript(script_sql)
    #
    # Exécution des commandes SQL du fichier

    to_add = []

    for lines in sql_script.split("\n"):
        if lines[0:5] == ".read":
            to_add.append(lines.split(".read")[1].strip())
        #
    #
    return [recursive_sql(e, basepath) for e in to_add] if to_add else sql_script
#
