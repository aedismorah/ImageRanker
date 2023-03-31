import os
import sqlite3

def init_db(conf):
    if not os.path.exists(conf.database_folder):
        os.mkdir(conf.database_folder)
        
        connection = sqlite3.connect(conf.database_path)
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE reactions (username TEXT, folder TEXT, image TEXT, reaction INTEGER)")
        connection.commit()
        connection.close()

def get_last_item(key, usr_data):
    item = usr_data[-1][key]
    return item

def get_db_connection(conf):
    conn = sqlite3.connect(conf.database_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_folder(user, conf):
    usr_data = select_from_db(user, 'folder', conf)
    folder = get_last_item('folder', usr_data) if usr_data else conf.starting_image_folder
    ### bad
    folder = folder.replace('/', '')
    return folder

def add_reaction_to_db(user, image, reaction, conf, folder=None):
    conn = get_db_connection(conf)
    if not folder:
        folder = get_folder(user, conf)
    conn.execute(f"INSERT INTO reactions VALUES ('{user}', '{folder}', '{folder}/{image}', {reaction})")
    conn.commit()
    usr_data =  select_from_db(user, 'image, folder, reaction', conf)
    conn.close()

    return usr_data

def select_from_db(user, query, conf):
    conn = get_db_connection(conf)
    usr_data = conn.execute(f"SELECT {query} FROM reactions WHERE username is '{user}'").fetchall()
    conn.close()
    return usr_data