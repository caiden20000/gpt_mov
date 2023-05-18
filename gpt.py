import requests
import async_api

gpturl = 'https://api.openai.com/v1/chat/completions'
dalleurl = 'https://api.openai.com/v1/images/generations'
openaikey = ''
# get key from openaikey.txt
with open('keys/openaikey.txt', 'r+') as f:
    openaikey = f.readline().strip()

models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-32k"]
use_model = models[0]

# Makes a request to the OpenAI API
# Uses headers:
#   Authorization": "Bearer " + openaikey,
#   "Content-Type": "application/json"
def gpt(prompt):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + openaikey}
    request = {
        "model": use_model,
        "messages": [
            {
                "role": "system",
                "content": prompt
            }
        ]
    }
    print("Sending GPT request...")
    response = requests.post(gpturl, headers=headers, json=request)
    if response.ok:
        print("Got GPT response!")
        return response.json()['choices'][0]['message']['content']
    else:
        print('Error: ' + response.text)

def download_image(url, filename):
    print("Downloading image...")
    response = requests.get(url)
    if response.ok:
        print("Response OK! Writing to file " + filename + "...")
        with open(filename, 'wb') as file:
            file.write(response.content)
            print('File saved successfully.')
    else:
        print('Error: ' + response.text)
        return False

def dalle(prompt, filename):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + openaikey}
    request = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024" #256x256, 512x512, or 1024x1024
    }
    print(f"Getting DALL-E image from prompt: {prompt}")
    response = requests.post(dalleurl, headers=headers, json=request)
    if response.ok:
        url = response.json()["data"][0]['url']
        filepath = "www/images/" + filename + ".png"
        download_image(url, "www/images/" + filename + ".png")
        return filepath
    else:
        print('Error: ' + response.text)
        return False

# Async versions below


async def async_gpt(session, prompt):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + openaikey}
    request = {
        "model": use_model,
        "messages": [
            {
                "role": "system",
                "content": prompt
            }
        ]
    }
    print("Sending GPT request...")
    #response = requests.post(gpturl, headers=headers, json=request)
    response = await async_api.send_post_request(session, gpturl, headers, request)
    if response.ok:
        print("Got GPT response!")
        return response.json()['choices'][0]['message']['content']
    else:
        print('Error: ' + response.text)
        return False

async def async_download_image(session, url, filename):
    print("Downloading image...")
    # response = requests.get(url)
    response = await async_api.send_get_request(session, url)
    if response.ok:
        print("Response OK! Writing to file " + filename + "...")
        with open(filename, 'wb') as file:
            file.write(response.content)
            print('File saved successfully.')
        return filename
    else:
        print('Error: ' + response.text)
        return False

async def async_dalle(session, prompt, filename):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + openaikey}
    request = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024" #256x256, 512x512, or 1024x1024
    }
    print(f"Getting DALL-E image from prompt: {prompt}")
    # response = requests.post(dalleurl, headers=headers, json=request)
    response = await async_api.send_post_request(session, dalleurl, headers, request)
    if response.ok:
        url = response.json()["data"][0]['url']
        filepath = "www/images/" + filename + ".png"
        img_succ = download_image(url, "www/images/" + filename + ".png")
        return filepath if img_succ else False
    else:
        print('Error: ' + response.text)
        return False