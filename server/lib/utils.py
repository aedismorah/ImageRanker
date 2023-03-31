import pickle
import numpy as np
import hnswlib

from lib.db import get_folder, select_from_db
from lib.consts import EMBEDDING_SHAPE, LIKE, DISLIKE, GAMMA, SUBSET_SIZE


def load_embeddings(path):
    with open(path, 'rb') as f:
        embeddings = pickle.load(f)
    return embeddings

def get_last_item(key, usr_data):
    item = usr_data[-1][key]
    return item

def sample(folder, mapping, N=SUBSET_SIZE):
    lst = list(mapping.keys())
    subset = [image_path for image_path in lst if folder in image_path]
    subset = np.random.choice(subset, min(N, len(subset)), replace=False)
    subset = {key: mapping[key] for key in subset}
    return subset

def process_user_assessment(usr_data, user, conf, mapping, embs, filenames, hnsw_search):
    folder = get_folder(user, conf)
    image_filename = get_next_image(usr_data, mapping, embs, filenames, hnsw_search)
    URL = f'http://{conf.server_ip}:{conf.flask_port}/assess/{user}/{image_filename}'
    return URL

def get_weighted_average(images, mapping):
    weighted_image_embeddings = [mapping[image] * np.exp(-idx * GAMMA) for idx, image in enumerate(reversed(images))]
    weighted_average = np.mean(np.vstack(weighted_image_embeddings), axis=0)
    return weighted_average

def get_next_image(usr_data, mapping, embs, filenames, hnsw_search):
    cossim = lambda emb, embs: np.sum(emb * embs, axis=-1)

    liked_images    = [row['image'] for row in usr_data if row['reaction'] == LIKE]
    disliked_images = [row['image'] for row in usr_data if row['reaction'] == DISLIKE]
    seen_images = set(liked_images).union(set(disliked_images))

    positive_taste = get_weighted_average(liked_images, mapping)    if liked_images    else np.random.rand(EMBEDDING_SHAPE)
    negative_taste = get_weighted_average(disliked_images, mapping) if disliked_images else np.random.rand(EMBEDDING_SHAPE)


    if np.random.randint(10) > 8:
        rand_vec       = np.random.rand(EMBEDDING_SHAPE)
        positive_taste = (positive_taste + rand_vec) / 2
        negative_taste = (positive_taste - rand_vec) / 2
        
    resulting_taste = (positive_taste - negative_taste) / 2
    
    top_cands = []

    while not top_cands:
        labels, distances = hnsw_search.knn_query(resulting_taste, k=100)
        top_cands = [filenames[idx] for idx in labels[0] if filenames[idx] not in seen_images]
        resulting_taste = (resulting_taste + np.random.rand(EMBEDDING_SHAPE)) / 2
    
    return top_cands[0]