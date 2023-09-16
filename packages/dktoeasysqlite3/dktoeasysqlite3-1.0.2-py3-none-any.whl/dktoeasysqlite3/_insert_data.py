from dktotoolkit import write_message
def insert_data(self, table_name:str, data_dict:dict, allow_duplicates:bool=True, commit:bool=True, replace_on_datas=None):
    """
    Insère des données dans une table.

    :param table_name: Nom de la table cible.
    :type table_name: str
    :param data_dict: Dictionnaire contenant les colonnes et leurs valeurs.
    :type data_dict: dict
    :param allow_duplicates: Indique si les doublons sont autorisés (par défaut: True).
    :type allow_duplicates: bool
    :param commit: Indique si la transaction doit être validée immédiatement (par défaut: False).
    :type commit: bool
    :param replace_on_datas: Colonnes à mettre à jour avec de nouvelles valeurs si elles existent.
    :type replace_on_datas: str or list

    :return: None
    :rtype: None
    """

    columns = ", ".join(data_dict.keys())
    #placeholders = ":" + ", :".join(data_dict.keys()) #[e if e is not None else "NULL" for e in data_dict.values()])
    placeholders = ", ".join(["?" for e in data_dict.keys()]) #[e if e is not None else "NULL" for e in data_dict.values()])

    datas = list(data_dict.values())

    # Mettez à jour les colonnes spécifiées dans replace_on_datas si elles existent
    if (replace_on_datas and
        self.get_datas(table_name=table_name, conditions=data_dict, if_present=True) ):

        new_values=' , '.join([f"{k} = ?" for k,v in data_dict.items()])
        data_dict = {e:(data_dict[e] if e in data_dict.keys() else None) for e in replace_on_datas}

        datas_to_find=' AND '.join([f"{k} = ?" for k in data_dict.keys()])

        datas = [*datas, *[data_dict[e] for e in replace_on_datas]]
        query = f"UPDATE {table_name} SET {new_values} WHERE {datas_to_find}"
        write_message(f"Update datas in table : {query} :: datas = {datas}")

    elif allow_duplicates:
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        write_message("May insert duplicated datas in table")
    else:
        query = f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})"
        # query = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
    #endIf

    try:
        self.add_db(query=query, datas=datas, commit=commit)
    except Exception as e:
        print(e)
        raise
#endIl
