import json
import random
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import csv 


url = ""

def base64_to_image(base64_string):
    try:
        image_data = base64.b64decode(base64_string)
        image_bytes = io.BytesIO(image_data)
        img = Image.open(image_bytes)
        return img
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        return None

async def txt2img (prompt :str,
                negative_prompt :str="",
                image_height :int=768,
                image_width :int=768,
                guidance_scale :int=7,
                steps :int=20,
                model:str="Ultimate_XL",
                style:str='No Style XL'):



    payload = {
      "prompt": prompt,
      "negative_prompt": negative_prompt,
      "scheduler": "DPM++ 2M Karras",
      "styles": [
    style
            ],
      "height": image_height,
      "width": image_width,
      "guidance_scale": guidance_scale,
      "steps": steps,
      "seed": -1,"override_settings": {"sd_model_checkpoint": model}
    }
    response = requests.post(url=f'{url}sdapi/v1/txt2img', json=payload)
    r = response.json()
    image = r['images'][0]
    #image = base64_to_image(image)
    return image
#for j, i in enumerate(r['images'][:2]):
#    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[1])))
#    image.save(f'output{j+1}.png')
#    image.show()
#img=txt2img(prompt="a man")
#img.save("output.png")
def get_models():
    try:
        response = requests.get(url=f'{url}sdapi/v1/sd-models')
        r = response.json()
        index=len(r)
        models=[]

        for i in range(index):
            model=r[i]['model_name']
            models.append(model)
        return models
    except:
        return "error"

def get_wait_msg():
    with open('wait_dialogue.csv', 'r') as file:
        reader = csv.reader(file)
        lines = list(reader)  # Convert CSV rows into a list of lines

    if len(lines) > 1:  # Check if there is more than one line
        random_line = random.choice(lines)
        return ' '.join(random_line)  # Assuming each line is a list of words

    return "Sorry, the CSV file is empty or contains only headers."

def get_styles(model:str='XL'):
    response = requests.get(url=f'{url}sdapi/v1/prompt-styles')
    data = response.json()  # Parse JSON content

    names = [entry['name'] for entry in data if entry['name'].endswith(f'{model}')]
    return names