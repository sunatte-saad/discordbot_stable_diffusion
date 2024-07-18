from queue import Queue
import threading
from threading import Lock
import threading
import requests
url = "http://110.93.223.194:7000/"
app_lock= threading.Lock()
class Text2Image:
    def __init__(self):
        self.queue = Queue()
        self.lock = Lock()
    def process_txt2img (self, prompt :str,
                negative_prompt :str="",
                image_height :int=768,
                image_width :int=768,
                guidance_scale :int=7,
                steps :int=20,
                model:str="Ultimate_XL"):



                payload = {
                  "prompt": prompt,
                  "negative_prompt": negative_prompt,
                  "scheduler": "DPM++ 2M Karras",
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
    def process_txt2img_queue(self):
           while True:
                  request = self.queue.get()
                  self.process_txt2img(**request)
                  self.queue.task_done()
processor_txt2img= Text2Image()
threading.Thread(target=processor_txt2img.process_txt2img_queue,daemon=True).start()