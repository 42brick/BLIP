"""
Download the weights in ./checkpoints beforehand for fast inference
wget https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model*_base_caption.pth
wget https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model*_vqa.pth
wget https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_retrieval_coco.pth
"""

import pandas as pd
from PIL import Image
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from tqdm import tqdm

from models.blip import blip_decoder
import argparse
import os

class Predictor :
    def __init__(self):
        self.device = "cuda:0"
        self.models = blip_decoder(pretrained='checkpoints/model_blip.pth', image_size=384, vit='base')

    def predict(self, path):
        model = self.models
        model.eval()
        model = model.to(self.device)

        caption_list = []
        image_list = []
        img_names = os.listdir(path)
        for img_name in tqdm(img_names) :
            img = f'{path}/{img_name}'
            im, im_b = load_image(img, image_size=384, device=self.device)
                
            # similar coding like pokemon 
            bytes_dict = {}
            bytes_dict['bytes'] = im_b
            bytes_dict['path'] = None
            image_list.append(bytes_dict)            
            with torch.no_grad():
                caption = model.generate(im, sample=False, num_beams=3, max_length=20, min_length=5)
                caption_list.append(caption[0])
            
        return image_list, caption_list

    def predict_one(self, img_path):
        model = self.models
        model.eval()
        model = model.to(self.device)

        im, _ = load_image(img_path, image_size=384, device=self.device)

        with torch.no_grad():
            caption = model.generate(im, sample=True,num_beams=3, max_length=30, min_length=20)
        caption = caption[0] + ' ,with lego face, lego figure,4k,8k'
        return caption

def load_image(image, image_size, device):
    with open(image,'rb') as f:
        image_binary = f.read()
        f.close()

    raw_image = Image.open(str(image)).convert('RGB')
    

    w, h = raw_image.size

    transform = transforms.Compose([
        transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
    ])
    image = transform(raw_image).unsqueeze(0).to(device)
    return image, image_binary





if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", default = './image/test.jpg') #test???
    #parser.add_argument('-p',"--path",type=str, default='./image')
    parser.add_argument('-o',"--outdir",type=str,default='')

    args = parser.parse_args()
    image_path = args.image
    outdir = args.outdir


    # ?????? Load
    print("????????? ???????????????...")
    model = Predictor()


    # ?????? Inference ??? caption, image_bytes ??????
    print('????????? ???????????????...')
    caption = model.predict_one(image_path)

    
    with open(f'{outdir}.txt', 'w') as f :
        f.write(caption)
        f.close()
            
