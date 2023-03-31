import os
import time
import json
import pickle

import numpy as np
import hnswlib
from omegaconf import OmegaConf

from flask import Flask, send_file, send_from_directory, request
from flask_cors import CORS

from lib.preprocessing import init_images_embeddings, init_thumbnails
from lib.db import get_db_connection, get_folder, add_reaction_to_db, select_from_db, init_db
from lib.utils import load_embeddings, get_last_item, get_next_image, process_user_assessment
from lib.consts import LIKE, DISLIKE, GAMMA, THUMBNAIL_POSTFIX, CONF_PATH, EMBEDDING_SHAPE


conf = OmegaConf.load(CONF_PATH)
init_db(conf)
init_images_embeddings(conf)
init_thumbnails(conf)


mapping   = load_embeddings(conf.embeddings_path)
embs      = np.vstack(list(mapping.values()))
filenames = list(mapping.keys())


hnsw_search = hnswlib.Index(space='l2', dim=EMBEDDING_SHAPE)
hnsw_search.init_index(max_elements=len(embs), ef_construction=200, M=16)
hnsw_search.add_items(embs, np.arange(len(embs)))
hnsw_search.set_ef(50)



app = Flask(__name__)
cors = CORS()
cors.init_app(app)

def get_random_image(folder):
#     image_path = np.random.choice([image_path for image_path in list(mapping.keys()) if folder in image_path])
    image_path = np.random.choice([image_path for image_path in list(mapping.keys())])
    return image_path

@app.route("/get_last/<user>")
def get_last(user):
    usr_data = select_from_db(user, 'image, reaction', conf)
    folder = get_folder(user, conf)
    image = get_last_item('image', usr_data) if len(usr_data) else get_random_image(folder)

    return f'http://{conf.server_ip}:{conf.flask_port}/assess/{user}/{image}'

@app.route("/get_liked/<user>")
def get_liked(user):
    usr_data = select_from_db(user, 'image, folder, reaction', conf)
    folder = get_last_item('folder', usr_data)

    liked_images = [row['image'] for row in usr_data if (row['reaction'] == LIKE) and (row['folder'] == folder)]
    liked_images_th = [image.replace(folder, f'{folder}{THUMBNAIL_POSTFIX}') for image in liked_images]

    thumbnails_URLs = [f'http://{conf.server_ip}:{conf.flask_port}/assess/{user}/{image}' for image in liked_images_th]
    unique_thumbnails_URLs = list(set(thumbnails_URLs))
    return unique_thumbnails_URLs

@app.route("/like/<user>/<liked_image>")
def like(user, liked_image):
    start = time.time()
    usr_data = add_reaction_to_db(user, image=liked_image, reaction=LIKE, conf=conf)
    URL = process_user_assessment(usr_data, user, conf, mapping, embs, filenames, hnsw_search)
    print(f'debug like: {URL}')
    print(time.time() - start)
    return URL

@app.route("/dislike/<user>/<disliked_image>")
def dislike(user, disliked_image):
    start = time.time()
    usr_data = add_reaction_to_db(user, image=disliked_image, reaction=DISLIKE, conf=conf)
    URL = process_user_assessment(usr_data, user, conf, mapping, embs, filenames, hnsw_search)
    print(f'debug dislike: {URL}')
    print(time.time() - start)
    return URL

# @app.route("/set_folder/<user>/<folder>")
# def set_folder(user, folder):
#     usr_data = add_reaction_to_db(user, image='0', reaction=0, conf=conf, folder=folder + '/')
#     return 'good!'

@app.route("/assess/<user>/<folder>/<filename>", methods=['GET', 'POST'])
def assess(user, folder, filename):
    print(f'{conf.albums_folder}/{folder}/{filename}')
    return send_file(f'{conf.albums_folder}/{folder}/{filename}', mimetype='image/jpg')

@app.route("/download/<directory>/<filename>")
def download(directory, filename):
    return send_file(f'{directory}/{filename}', as_attachment=True)

### meeds fixin
@app.route("/listdir/<directory>")
def listdir(directory):
    URLs = [f'http://{conf.server_ip}:{conf.flask_port}/image/{directory}/{file}' for file in os.listdir(directory)]
    URLs_json = json.dumps(URLs, ensure_ascii=False)
    return URLs_json

@app.route("/available_folders/<user>")
def available_folders(user):
    available_folders = [folder_path for folder_path in os.listdir(conf.albums_folder) if THUMBNAIL_POSTFIX not in folder_path]
    return json.dumps(available_folders, ensure_ascii=False)

@app.route("/get_folder/<user>")
def get_user_folder(user):
    folder = get_folder(user, conf)
    return folder

app.run(host='0.0.0.0', port=conf.flask_port)