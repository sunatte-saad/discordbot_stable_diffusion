import discord
import asyncio
import random
import time 
import os
import aiohttp
import io
import csv
from discord.ext import bridge,commands
from dotenv import load_dotenv
from sample_request import txt2img,get_models,get_wait_msg,get_styles
import base64
from typing import Optional,Literal
from discord.ext.commands import cooldown,BucketType
from discord import user
from discord.ui import Button, View
from firebase import get_credits_email,update_credits_email,check_email,reduce_credits_by_one
from helper_func import check_user_id_exists,get_email_by_user_id,get_email_csv
import tempfile

from queue import Queue
import threading
from threading import Lock
import requests
import discord
import time
import io
import base64
from discord.ext import commands

url = "http://110.93.223.194:7000/"
app_lock = threading.Lock()

class Text2Image:
    def __init__(self):
        self.queue = Queue()
        self.lock = Lock()

    def process_txt2img(self, 
                        prompt: str, 
                        negative_prompt: str = "", 
                        image_height: int = 768, 
                        image_width: int = 768,
                         guidance_scale: int = 7, 
                         steps: int = 20, 
                         model: str = "Ultimate_XL",
                         style:str='No Style XL'):
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
                  "styles": [
                        style
            ],
            "scheduler": "DPM++ 2M Karras",
            "height": image_height,
            "width": image_width,
            "guidance_scale": guidance_scale,
            "steps": steps,
            "seed": -1, "override_settings": {"sd_model_checkpoint": model}
        }
        response = requests.post(url=f'{url}sdapi/v1/txt2img', json=payload)
        r = response.json()
        image = r['images'][0]
        return image

    def process_txt2img_queue(self):
        while True:
            request = self.queue.get()
            self.process_txt2img(**request)
            self.queue.task_done()

processor_txt2img = Text2Image()
threading.Thread(target=processor_txt2img.process_txt2img_queue, daemon=True).start()
load_dotenv()
styles=get_styles()
models=get_models()
if models=='error':
    print ('No Response from the server, please run it')
csv_file_path = 'users.csv'
url="http://110.93.223.194:7000/"

class Pycord(bridge.Bot):
    Token= os.getenv('TOKEN')
    intents=discord.Intents.all


client= Pycord(intent=Pycord.intents,command_prefix="!")


@client.listen()
async def on_ready():
    print(f"{client.user} has connected to Discord!")

@client.bridge_command(description="Ping.Pong")
async def ping(ctx,msg):   
    latency=(str(client.latency * 1000) + "ms")
    await ctx.respond(f"Pong! It took {latency} to complete the {msg}")

async def  main_bot():
    print ('Bot is starting')
    await client.start(Pycord().Token)



# Define the path to the CSV file
CSV_FILE_PATH = "function_calls.csv"

# Check if the CSV file exists; if not, create it
if not os.path.exists(CSV_FILE_PATH):
    with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
        csv.writer(csvfile).writerow(["timestamp", "user_id", "prompt", "height", "width", "model"])

#@client.bridge_command(description="Visualizes your imagination")
#@discord.option("model", choices=models)
#async def dream(ctx: discord.ApplicationContext, prompt: str, height: int = 768, width: int = 768, model: str = "Ultimate XL" ):
#    
#    user_email =await get_email_by_user_id(ctx.author.id)
#    if user_email is not None:
#        user_id = ctx.author.id
#        #user_credits=get_credits_email(user_email)
#        #updated_credits=int(user_credits)-1
#        #reduce_credits_by_one(user_email)
#        #update_credits_email(email=user_email,credits=updated_credits)
#        #await ctx.send(f'Your current credits are {user_credits-1}')
#        timestamp = time.time()
#
#        #with open(CSV_FILE_PATH, 'r', newline='') as csvfile:
#        #    rows = list(csv.reader(csvfile))
#        #queue_number = len(rows)   # Calculate the queue number 
#        #queue_msg= await ctx.send (f"Your request has been queued on {queue_number}")
        
#        #with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
#        #    csv.writer(csvfile).writerow([timestamp, user_id, prompt, height, width, model])
#
#        await ctx.defer()
#        #await queue_msg.delete()
#        wait_msg = await ctx.respond(get_wait_msg())
#
#        base64_image = await txt2img(prompt=prompt, image_height=height, image_width=width, model=model)
#        image_data = base64.b64decode(base64_image)
#        
#        with open(CSV_FILE_PATH, 'r', newline='') as csvfile:
#            rows = list(csv.reader(csvfile))
#        with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
#            csv.writer(csvfile).writerows(rows[1:])  # Exclude the first row (header)
#
#        await wait_msg.delete()
#
#        #latency = str(client.latency * 1000) + "ms"
#        await ctx.send(f"{ctx.author.mention}\nHere is your art \nPrompt:{prompt}\nHeight:{height},Width:{width}, Model:{model} ",
#                       file=discord.File(io.BytesIO(image_data), filename='image.png'), view=View())
#    else:
#        await ctx.send("Please register yourself using command : /register_user")
@client.slash_command(description="Visualizes your imagination")
@discord.option("model", choices=models)
@discord.option("style", choices=
[
"No Style XL",
"cinematic-default XL",
"3d-model XL",
"analog film XL",
"anime XL",
"cinematic XL",
"comic book XL",
"craft clay XL",
"digital art XL",
"enhance XL"])
#@commands.cooldown(1,5,commands.BucketType.user)
async def imagine(ctx: commands.Context, prompt: str, height: int = 1024, width: int = 1024,style:str='No Style XL', model: str = "Ultimate XL"):
    await ctx.defer()
    user_email = await get_email_by_user_id(ctx.author.id)

    if user_email is not None:
        #await ctx.defer()
        user_id = ctx.author.id
        timestamp = time.time()
        #user_credits=await get_credits_email(user_email)
        #updated_credits=int(user_credits)-1
        user_credits=await reduce_credits_by_one(user_email)
        #update_credits_email(email=user_email,credits=updated_credits)
        #await ctx.send(f'Your current credits are {user_credits-1}')
        #await ctx.defer()
        wait_msg = await ctx.send(get_wait_msg())

        # Add the request to the queue
        processor_txt2img.queue.put({"prompt": prompt, "image_height": height, "image_width": width, "model": model,"style":style})


        # Fetch the processed image from the queue
        base64_image = processor_txt2img.process_txt2img(prompt=prompt, image_height=height, image_width=width,
                                                          model=model,style=style)
        image_data = base64.b64decode(base64_image)
        output_file = f"{user_id}+{timestamp}"  # Adjust the file extension based on the image format
#       
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            print(f"Image saved to temporary file: {temp_file_path}")
        except Exception as e:
            print(f"An error occurred while saving the image: {e}")
        #try:
        #    with open(output_file, 'wb') as f:
        #        f.write(image_data)
        #    print(f"Image saved to {output_file}")
        #except Exception as e:
        #    print(f"An error occurred while saving the image: {e}")
        await wait_msg.delete()

        file = discord.File(f"{temp_file_path}", filename="output.png")
        #response_embed=discord.Embed(title="Image Generation", description=f"{ctx.author.mention} Here is your art \n prompt:{prompt}, height:{height},width:{width}\n  Model:{model}\n Remaining Credits:{user_credits-1} ",
        #                              color=discord.Color.random())
        response_embed=discord.Embed(title="Image Generation", description=f"{ctx.author.mention} Here is your art ",color=discord.Color.random())
        
        response_embed.set_image(url="attachment://output.png")
        response_embed.add_field(name='Prompt', value=prompt, inline=False)
        response_embed.add_field(name='Height', value=height, inline=False)
        response_embed.add_field(name='Width', value=width, inline=False)
        response_embed.add_field(name='Model', value=model, inline=False)
        response_embed.add_field(name='Remaining Credits', value=user_credits-1, inline=False)
        response_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        response_embed.set_footer(text='Powered by Adicto AI',icon_url='https://lh3.googleusercontent.com/pw/AP1GczOXe-V3KMpxwB7MxK51t2dYya3h425TaqCCcw1vsb9GbE6LfTsgjOiV4yEUFjRy5MSr2EkjmtrT_jBjlBtxO21s-gFs4c3gqK61W1kS2x_ODMo4nQyoO4Kn_GsLzoQL8OUOzUl_AjgzkRY4NGPP5T4ExGfkSmSHY7FWFoylEITsm3nV2_KcPolAC4QZrMJu0sZj6cnpo8uclIL7iWJNQMU2UkoUPi8IljYCdS9nCQj7LpLoaPkOfXKUaxKa-gQs5T3c2El9wHE2Zxt8xerQTZ5971Q2g8q30S48Xn4uynU3lDIHavnj7DTcq7p4h0PzWGltJRTQjRewfjt4UJlnQM6wm7Vl9vs32tIaKkAB4PlhdRpjezeWQuUOlWnanmJEkKGboUkF6V_Jdu5-u2v8wOhUsVU16Zyn4nwS1IsBNUHbfXWxnWqSqjJGTL7C5qKjHr9lw1rJFxBTOeMLie6s-aYSW6QIQXnWFkyeYZ5VU61WVGk_8Xt9TiTsjo8ujVwP1cWyXa-Emi1ntlMUsG-2x7aDQvm-Sr-UNqLNL-04ZL9P4rycZnGjX-GRvJ-Myrc8a_cjK4bGK4BRAwFQRx5mB0es3nKr4nZbyRybebvi8gFgfeugyI_078u0Qgl08meCKjqFKlPhmNfgtij3Zlj_w1XF8jaAvGr6PtCUx4KDtVQia-27G9QBay9IcXfeC6oaD1oOQcOLAtd8KpACqcY1d7j3dAGkmPuYtzRqns0ggcRHZoSTFQPL2mrdULdjs0ZavOeqPHiQU9xv4sTnQEz7k-r-zwYJZ2DBFe9G-pF4DebD8qb6V1T9PNapDWDK3v2TRXk5_GirZw0xGkQYX4v-iVVR5KmAAbbr-aoE2L2E9xIGNeFdX_ZOu79fdZHuMsFa1qbTngkrfpmJbBKdDWdRz3s=w742-h551-s-no-gm?authuser=0')
        #response_embed.set_image(file=discord.File(io.BytesIO(image_data), filename='image.png'))
        await ctx.respond(embed=response_embed,file=file)
        os.remove(temp_file_path)
        #await ctx.send(f"{ctx.author.mention} Here is your art \n prompt:{prompt}, height:{height},width:{width}\n  Model:{model} ",
                       #file=discord.File(io.BytesIO(image_data), filename='image.png'), view=View())
    else:
        register_adicto_embed=discord.Embed(title="Please register yourself using command: /register_user",color=discord.Colour.red())
        await ctx.send(embed=register_adicto_embed,ephemeral=True)
        #await ctx.send("Please register yourself using command: /register_user")
@client.bridge_command(description="Registers a new user using your Adicto Web login")
async def register_user(ctx:discord.ApplicationContext, email_address: str):
    await ctx.defer()
    user_id = ctx.author.id
    credit_user=await get_credits_email(email_address)
    if credit_user == "Email not found":
        reg_yourself_embed=discord.Embed(title="Registration Failed", description=f"{ctx.author.mention}\nPlease register yourself on https://adictoai.com/",color=discord.Color.red())
        await ctx.respond(embed=reg_yourself_embed,ephemeral=True)
        #await ctx.respond(f"{ctx.author.mention} Please register yourself on https://adictoai.com/")
    else:
        user_email=await get_email_csv(csv_file='users.csv',user_id=user_id)
        if user_email is not None:
            already_reg_embed=discord.Embed(title="Already registered", description=f"{ctx.author.mention} You have already been registered with the email ID : {user_email}", color=discord.Colour.red())
            await ctx.respond(embed=already_reg_embed,ephemeral=True)
            #await ctx.respond(f"{ctx.author.mention}\nYou have already been registered with the email ID: {user_email}")
        else:
            with open(csv_file_path, 'a', newline='') as csvfile:
                fieldnames = ['email', 'user_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'email': email_address, 'user_id': str(user_id)})
                registered_embed=discord.Embed(title="Registered Successfully", description=f"You have successfully been registered with: {email_address}", color=discord.Colour.green())
                await ctx.respond(embed=registered_embed,ephemeral=True)
                #await ctx.respond(f"{ctx.author.mention}\nYou have successfully been registered with: {user_email}")
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}',ephemeral=True)
    else:
        # If it's not a CommandOnCooldown error, let the default handler print to the terminal
        raise error
if __name__ =="__main__":
    loop=asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(main_bot()))

