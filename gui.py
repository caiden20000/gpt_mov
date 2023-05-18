from dataclasses import dataclass
# import eel
import eel
import multiprocessing

import gpt
import eleven
import async_api
import aiohttp
import main

'''
Problem: The API calls are synchronous, and the local server resources are not served until the function exits.
Solution: Asynchronous code.
Methods:
    - Multiprocessing
        - I don't see a way to async share data through the processes.
            Every method I see of passing data between processes makes it synchronous.
            (queue.get() waits, pipe.recv() waits, etc.)
        - What are pools?
    - Asyncio
        - I would have to convert all API calls to async, in each file.
            The receiving of the data would still be synchronous, I think.
            Think about await, all that.
The way I'm seeing it:
    1. Break up all the script sentences into segments.
    2. For each segment, generate the resources in a separate process.
    3. When the resources are generated, the process has a callback I think? This is the shaky step.
    4. The callback adds the image and audio to the segment.
    5. 

async api_call(callback):
    data = await request(...)
    callback(data)

def append_to_sequence(segment, index):
    sequence.insert(index, segment)

# index is important because it's asynchronous
api_call(lambda data: append_to_sequence(Segment(data), index))

# with a Segment containing __init__(self, img, text, audio, name)
def generate_sequence(prompt):
    script = await gpt(prompt)
    
    I implemented async, but it turns out eel doesn't support it...

'''

eel.init('www', allowed_extensions=['.js'])

class Segment:
    def __init__(self, text, name):
        self.text = [text]
        self.name = name
        self.img: list[str | bool] = [False]
        self.audio: list[str] = ['']
        
        self.img_ver = 0
        self.audio_ver = 0
        self.text_ver = 0
        
    @classmethod
    async def async_create(cls, session, text, name, img: str | None=None, audio: str | None=None):
        initial = Segment(text, name);
        initial.img = [await async_text_to_image(session, text, name + "_0")] if img is None else [img]
        initial.audio = [await async_text_to_audio(session, text, name + "_0")] if audio is None else [audio]
        return initial
    
    def get_img(self):
        img = self.img[self.img_ver]
        if type(img) is bool: return False
        return img[4:] # www/
    
    def get_audio(self):
        audio = self.audio[self.audio_ver]
        if type(audio) is bool: return False
        return audio[4:] # www/
    
    def get_text(self):
        return self.text[self.text_ver]
    
    async def add_img_ver(self, session):
        self.img_ver = len(self.img)
        img = await async_text_to_image(session, self.get_text(), self.name + "_" + str(self.img_ver))
        if type(img) is bool: return False
        self.img.append(await img)

    async def add_audio_ver(self, session):
        self.audio_ver = len(self.audio)
        audio = await async_text_to_audio(session, self.get_text(), self.name + "_" + str(self.audio_ver))
        self.audio.append(await audio)
    
    async def add_text_ver(self, session, script):
        self.text_ver = len(self.text)
        self.text.append(await async_regenerate_sentence(session, script, self.get_text()))
        # TODO: Use the before, a fter, andb etween generators instead.
    


# ordered list of segments
project_name = ""
script = ""
sequence = []
default_prompt = ""
with open('prompt.txt', 'r') as f:
    default_prompt = f.read()

#  builtin-prompts

async def async_regenerate_sentence(session, script, sentence):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, re-word or rephrase this sentence from the script: \n'
    subprompt += f"\"{sentence}\"\n\n"
    subprompt += 'Only return the new rephrased sentence. Do not return the entire script.'
    return gpt.async_gpt(session, subprompt)

async def async_generate_sentence_between(session, script, prev_sentence, next_sentence):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, write a new sentence that will go between these two sentences: \n'
    subprompt += f"\"{prev_sentence}\"\n"
    subprompt += f"<Your new sentence here>"
    subprompt += f"\"{next_sentence}\"\n"
    subprompt += 'Only return the new sentence. Do not return the entire script.'
    return gpt.async_gpt(session, subprompt)

async def async_generate_sentence_at_beginning(session, script):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, write a new sentence that will naturally go at the beginning of the script. \n'
    subprompt += 'Only return the new sentence. Do not return the entire script.'
    return gpt.async_gpt(session, subprompt)

async def async_generate_sentence_at_end(session, script):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, write a new sentence that will naturally go at the end of the script. \n'
    subprompt += 'Only return the new sentence. Do not return the entire script.'
    return gpt.async_gpt(session, subprompt)

async def async_get_image_description(session, sentence):
    subprompt = 'An image description is a short sentence that describes the content of an image. \n'
    subprompt += 'For example: "A large plant in winter conditions, cold, photograph" \n'
    subprompt += 'or "A person sneezing into a folded tissue, closeup, photograph" \n'
    subprompt += 'or "A diagram of a molecule, illustration, science" \n'
    subprompt = 'In the same style, describe IN 20 WORDS OR LESS an image to show during this sentence for a video essay: \n'
    subprompt += sentence
    return gpt.async_gpt(session, subprompt)

    
async def async_text_to_image(session, text, name):
    return await gpt.async_dalle(session, await async_get_image_description(session, text), name)

async def async_text_to_audio(session, text, name):
    return await eleven.async_tts(session, eleven.voices['Antoni'], text, name)

@eel.expose
async def async_generate_sequence(project_name, prompt=default_prompt):
    print("Starting async generation!")
    with aiohttp.ClientSession() as session:
        script = await gpt.async_gpt(session, prompt)
        if script == False: return False
        for line in script.splitlines():
            if line in ['', '\n']: continue
            seg = await Segment.async_create(session, line, f'{project_name}_seg{len(sequence)}')
            append_to_sequence(seg)
            eel.refresh_sequence() # type: ignore
            

@eel.expose
async def ags(project_name, prompt=default_prompt):
    print("ELLO!")
    await async_generate_sequence(project_name, prompt)


def append_to_sequence(segment):
    sequence.append(segment)
    eel.append_segment(segment.get_img(), segment.get_audio(), segment.get_text()) # type: ignore

# Issue: EEL doesn't serve resources until this function exits
# So resources populate at once. How to thread it?
# @eel.expose
# def generate_sequence(append_func, project_name, prompt=default_prompt):
#     script = gpt(prompt)
#     for line in script.splitlines():
#         if line in ['', '\n']: continue
#         seg = Segment(line, f'{project_name}_seg{len(sequence)}')
#         append_func(seg)
#         # sequence.append(seg)
#         # eel.append_segment(seg.get_img(), seg.get_audio(), seg.get_text())
#     eel.refresh_sequence()

# @eel.expose
# def generate_sequence_thread(project_name):
#     append_func = multiprocessing.Value('P', append_to_sequence)
#     process = multiprocessing.Process(target=generate_sequence, args=(append_func, project_name))
#     process.start()

@eel.expose
def get_sequence_length():
    return len(sequence)

# @eel.expose
# def add_segment(index):
#     text = ""
#     if index <= 0:
#         text = generate_sentence_at_beginning(script)
#     elif index >= len(sequence)-1:
#         text = generate_sentence_at_end(script)
#     else:
#         text = generate_sentence_between(script, sequence[index-1].get_text(), sequence[index+1].get_text())
#     sequence.insert(index, Segment(text,f'{project_name}_seg{len(sequence)}'))

def get_segment(num):
    return sequence[num]

@eel.expose
def get_segment_as_arr(num):
    seg = get_segment(num)
    return [seg.get_img(), seg.get_audio(), seg.get_text()]

@eel.expose
def get_segment_img(num):
    return get_segment(num).get_img()

@eel.expose
def get_segment_audio(num):
    return get_segment(num).get_audio()

@eel.expose
def get_segment_text(num):
    return get_segment(num).get_text()

@eel.expose
def add_segment_img_ver(num):
    get_segment(num).add_img_ver()
    return get_segment_img(num)

@eel.expose
def add_segment_audio_ver(num):
    get_segment(num).add_audio_ver()
    return get_segment_audio(num)

@eel.expose
def add_segment_text_ver(num):
    get_segment(num).add_text_ver()
    return get_segment_text(num)

@eel.expose
def get_segment_img_ver_count(num):
    return len(get_segment(num).img)

@eel.expose
def get_segment_audio_ver_count(num):
    return len(get_segment(num).audio)

@eel.expose
def get_segment_text_ver_count(num):
    return len(get_segment(num).text)

@eel.expose
def change_segment_img_ver(num):
    get_segment(num).img_ver = num
    return get_segment_img(num)

@eel.expose
def change_segment_audio_ver(num):
    get_segment(num).audio_ver = num
    return get_segment_audio(num)

@eel.expose
def change_segment_text_ver(num):
    get_segment(num).text_ver = num
    return get_segment_text(num)


eel.start('index.html')