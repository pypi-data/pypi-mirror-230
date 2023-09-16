from typing import Union
def get_datas(self, table_name:str, fields:Union[list, tuple]=None, conditions:dict={}, if_present:bool=False):
    """
    Récupère des données depuis une table.

    :param str table_name: Nom de la table.
    :param list or tuple fields: Liste des champs à récupérer (par défaut: None, ce qui signifie tous les champs).
    :param dict conditions: Conditions pour filtrer les résultats (par défaut: {}).
    :param bool if_present: Indique si on doit vérifier si au moins une ligne existe (par défaut: False).

    :return: Si `if_present` est True, retourne True si au moins une ligne existe
             Si `if_present` est False, retourne les données.
    :rtype: bool or list
    """

    if fields is None:
        fields = "*"
    else:
        fields = ",".join(fields)
    #

    if if_present:
        query = f"SELECT COUNT(*) from {table_name} "
    else:
        query = f"SELECT {fields} from {table_name} "
    #
    if conditions:
        query += f"WHERE {' AND '.join([f'{key}=?' for key in conditions.keys()])}"
    #


    if if_present:
        d = self.request_db(query=query, datas=list(conditions.values()))
        return d[0][0] > 0
    else:
        d = self.request_db(query=query, datas=list(conditions.values()))
        return d
    #
