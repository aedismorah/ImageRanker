import os
import shutil
import pickle
import numpy as np
from PIL import Image
from tqdm import tqdm
from transformers import AutoProcessor, CLIPModel

from albumentations.augmentations.geometric.resize import SmallestMaxSize
from albumentations.augmentations.crops.transforms import CenterCrop

CLIP_MODEL = 'openai/clip-vit-base-patch32'


def create_url_suitable_filenames(source_images_folder, starting_image_folder):
    img_formats = ['png', 'jpg', 'jpeg']
    extension = lambda x: x.split('.')[-1].lower()
    
    source_images    = [filename for filename in os.listdir(source_images_folder) if extension(filename) in img_formats]
    filename_mapping = {}
    files = []
    for idx, filename in enumerate(source_images):
        initial_path = os.path.join(source_images_folder, filename)
        new_path     = os.path.join(starting_image_folder, f'{idx:010d}.{extension(filename)}')
        shutil.copyfile(initial_path, new_path)
        files += [new_path]
        
    return files

def calculate_small_emb(model, processor, img):
    inputs = {k:v for k,v in processor(images=img, return_tensors="pt").items()}
    image_features = model.get_image_features(**inputs).flatten().detach().cpu()
    return image_features

def calculate_emb(model, processor, img):
    inputs = {k:v for k,v in processor(images=img, return_tensors="pt").items()}
    image_features = model.vision_model(**inputs).last_hidden_state.flatten().detach().cpu()
    return image_features

def calculate_embs(model, processor, files, conf):
    embeddings = {}
    for file in tqdm(files):
        try:
            img = Image.open(file)
            key = file.replace(f'{conf.albums_folder}/', '')
            embeddings[key] = np.array(calculate_emb(model, processor, img))
        except:
            print(f'error occured while processing image: {file}')
        
    return embeddings

def init_images_embeddings(conf):
    source_images_folder  = os.path.join(conf.albums_folder, conf.source_images_folder)
    starting_image_folder = os.path.join(conf.albums_folder, conf.starting_image_folder)
    
    if os.path.exists(source_images_folder) and not os.path.exists(starting_image_folder):
        print('CALCULATING CLIP EMBEDDINGS\n')
        os.mkdir(starting_image_folder)
        files = create_url_suitable_filenames(source_images_folder, starting_image_folder)
        files = [file for file in files if os.path.exists(file)]

        model = CLIPModel.from_pretrained(CLIP_MODEL)
        processor = AutoProcessor.from_pretrained(CLIP_MODEL)

        embeddings = calculate_embs(model, processor, files, conf)

        with open(conf.embeddings_path, 'wb') as f:
            pickle.dump(embeddings, f)
            
def init_thumbnails(conf):
    starting_image_folder = os.path.join(conf.albums_folder, conf.starting_image_folder)
    thumbnails_folder     = os.path.join(conf.albums_folder, conf.starting_image_folder.replace('/', '_th/'))
    
    if os.path.exists(starting_image_folder) and not os.path.exists(thumbnails_folder):
        os.mkdir(thumbnails_folder)
        print('GENERATING THUMBNAILS\n')
        
        resize = SmallestMaxSize(conf.thumbnail_size)
        crop = CenterCrop(conf.thumbnail_size, conf.thumbnail_size)

        for filename in tqdm(os.listdir(starting_image_folder)):
            image_path     = os.path.join(starting_image_folder, filename)
            thumbnail_path = os.path.join(thumbnails_folder, filename)

            image = np.array(Image.open(image_path))
            thumbnail = Image.fromarray(crop(**resize(image=image))['image'])
            thumbnail.save(thumbnail_path)