from dataclasses import dataclass
import eel
from main import *
from gpt import *

eel.init('www', allowed_extensions=['.js'])

class Segment:
    def __init__(self, text, name):
        self.text = [text]
        self.name = name
        self.img = [download_image_from_text(text, name + "_0")]
        self.audio = [download_audio_from_text(text, name + "_0")]

        self.img_ver = 0
        self.audio_ver = 0
        self.text_ver = 0
    
    def get_img(self):
        return self.img[self.img_ver][4:] # www/
    
    def get_audio(self):
        return self.audio[self.audio_ver][4:] # www/
    
    def get_text(self):
        return self.text[self.text_ver]
    
    def add_img_ver(self):
        self.img_ver = len(self.img)
        self.img.append(download_image_from_text(self.get_text(), self.name + "_" + str(self.img_ver)))

    def add_audio_ver(self):
        self.audio_ver = len(self.audio)
        self.audio.append(download_audio_from_text(self.get_text(), self.name + "_" + str(self.audio_ver)))

    def add_text_ver(self, script):
        self.text_ver = len(self.text)
        self.text.append(regenerate_sentence(script, self.get_text()))
    


# ordered list of segments
project_name = ""
script = ""
sequence = []
default_prompt = ""
with open('prompt.txt', 'r') as f:
    default_prompt = f.read()

# Issue: EEL doesn't serve resources until this function exits
# So resources populate at once. How to thread it?
@eel.expose
def generate_sequence(project_name, prompt=default_prompt):
    script = gpt(prompt)
    for line in script.splitlines():
        if line in ['', '\n']: continue
        seg = Segment(line, f'{project_name}_seg{len(sequence)}')
        sequence.append(seg)
        eel.append_segment(seg.get_img(), seg.get_audio(), seg.get_text())
    eel.refresh_sequence()

@eel.expose
def generate_sequence_thread(project_name):
    # no worky
    eel.spawn(lambda : generate_sequence(project_name))

@eel.expose
def get_sequence_length():
    return len(sequence)

@eel.expose
def add_segment(index):
    text = ""
    if index <= 0:
        text = generate_sentence_at_beginning(script)
    elif index >= len(sequence)-1:
        text = generate_sentence_at_end(script)
    else:
        text = generate_sentence_between(script, sequence[index-1].get_text(), sequence[index+1].get_text())
    sequence.insert(index, Segment(text,f'{project_name}_seg{len(sequence)}'))

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