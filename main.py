from mov import *
from gpt import gpt, dalle
from eleven import tts, voices


def get_image_description(sentence):
    subprompt = 'An image description is a short sentence that describes the content of an image. \n'
    subprompt += 'For example: "A large plant in winter conditions, cold, photograph" \n'
    subprompt += 'or "A person sneezing into a folded tissue, closeup, photograph" \n'
    subprompt += 'or "A diagram of a molecule, illustration, science" \n'
    subprompt = 'In the same style, describe IN 20 WORDS OR LESS an image to show during this sentence for a video essay: \n'
    subprompt += sentence
    return gpt(subprompt)

def get_script_subject(script):
    subprompt = 'Determine the subject of the following script. Use no more than five words: \n'
    subprompt += script
    return gpt(subprompt)

def get_previous_subjects():
    subprompt = 'Here are all topics previously covered. Do not write about any of these: \n'
    with open('previous_subjects.txt', 'r+') as f:
        pre = f.read()
        subprompt += pre if pre != '' else 'There are no previous subjects. Write about anything!\n'
    return subprompt

def add_latest_subject(script):
    subject = get_script_subject(script)
    with open('previous_subjects.txt', 'a+') as f:
        f.write(subject + '\n')


def download_image_from_text(text, filepath):
    img = dalle(get_image_description(text), filepath)
    return img

def download_audio_from_text(text, filepath):
    audio = tts(voices['Antoni'], text, filepath)
    return audio

def regenerate_sentence(script, sentence):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, re-word or rephrase this sentence from the script: \n'
    subprompt += f"\"{sentence}\"\n\n"
    subprompt += 'Only return the new rephrased sentence. Do not return the entire script.'
    return gpt(subprompt)

def generate_sentence_between(script, prev_sentence, next_sentence):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, write a new sentence that will go between these two sentences: \n'
    subprompt += f"\"{prev_sentence}\"\n"
    subprompt += f"<Your new sentence here>"
    subprompt += f"\"{next_sentence}\"\n"
    subprompt += 'Only return the new sentence. Do not return the entire script.'
    return gpt(subprompt)

def generate_sentence_at_beginning(script):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, write a new sentence that will naturally go at the beginning of the script. \n'
    subprompt += 'Only return the new sentence. Do not return the entire script.'
    return gpt(subprompt)

def generate_sentence_at_end(script):
    subprompt = 'Here is the entire script for context: \n'
    subprompt += script + "\n\n"
    subprompt += 'With that script in mind, write a new sentence that will naturally go at the end of the script. \n'
    subprompt += 'Only return the new sentence. Do not return the entire script.'
    return gpt(subprompt)

def generate_segment(text, filename):
    img = download_image_from_text(text, filename + '.png')
    audio = download_audio_from_text(text, filename + '.mp3')
    return (img, audio)


def get_resources(script):
    ia_arr = []
    ia_count = 0
    # split lines by period
    for line in script.splitlines():
        if line in ['', '\n']: continue
        ia_count += 1
        img = dalle(get_image_description(line), project_name + str(ia_count))
        if (img == False):
            if (ia_count == 1):
                raise Exception('DALL-E failed to generate first image.')
            else:
                # If possible, continue to use last image
                img = ia_arr[ia_count - 2][0]
        audio = tts(voices['Antoni'], line, project_name + str(ia_count))
        # Right now there's no way to tell if tts fails, this is for the future
        if (audio == False): 
            raise Exception('Eleven failed to generate audio.')
        ia_arr.append((img, audio))
    return ia_arr

# # Load default prompt from prompt.txt
# # Prompt contains basic info, ie "Write a script..."
# prompt = ''
# with open('prompt.txt+', 'r') as f:
#     prompt = f.read()

# # Get cli args
# project_name = ''
# custom_subject = ''
# # if main, read first arg as project name
# if __name__ == '__main__':
#     import sys
#     if len(sys.argv) > 1:
#         project_name = sys.argv[1]
#     else:
#         raise Exception('No project name provided.')
#     if len(sys.argv) > 2:
#         # set custom_subject to a string of all argv after the first
#         custom_subject = ' '.join(sys.argv[2:])
#         print("Custom subject specified!")
#         prompt += "\n Write the script about " + custom_subject + "."
#     else:
#         print("No custom subject specified.")
#         prompt += "\n" + get_previous_subjects()
#         prompt += "Write the script about any subject not already covered."

# # Generate the video file
# script = gpt(prompt)
# if (script == False):
#     raise Exception('GPT failed to generate script.')

# # Generate images and audio
# ia_arr = get_resources(script)
# # Combine images and audio
# clip = ia_tuple_arr_to_videoclip(ia_arr)
# # Overlay the generated video onto ADHD background for TikTok / YT Shorts
# clip = overlay_on_bg(clip, 1)
# # Export video
# clip.write_videofile(f"output/{project_name}.mp4")

# # When auto generating, don't cover the same subject twice.
# add_latest_subject(script)