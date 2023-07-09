"""This module contains the Sequence class, which can build a video 
and manage many versions of individual video elements."""
import json
import aiohttp
import moviepy.editor as mov
import gpt
import eleven

# pylint: disable=W0105 # Useless multiline string
# pylint: disable=W1514 # Not specifying encoding in open()
# pylint: disable=W0603 # Global statement

IMAGE_PATH = 'images/'
AUDIO_PATH = 'audio/'
OUTPUT_PATH = 'output/'

CURRENT_ELEVEN_REQUESTS = 0 # max 3 concurrent
MAX_CONCURRENT_ELEVEN_REQUESTS = 3
CURRENT_GPT_REQUESTS = 0 # max 10? concurrent
MAX_CONCURRENT_GPT_REQUESTS = 3
CURRENT_DALLE_REQUESTS = 0 # max 10? concurrent
MAX_CONCURRENT_DALLE_REQUESTS = 3

prompts = {}
try:
    with open('prompts.json', 'r') as f:
        prompts = json.load(f)
except FileNotFoundError:
    print("File not found error: prompts.json")
except json.JSONDecodeError:
    print("JSON parse error: prompts.json")

async def wait_for_eleven_concurrency():
    """Async function that returns when more concurrent ElevenLabs TTS API requests are allowed."""
    while CURRENT_ELEVEN_REQUESTS >= MAX_CONCURRENT_ELEVEN_REQUESTS:
        await asyncio.sleep(1)
    return

async def wait_for_gpt_concurrency():
    """Async function that returns when more concurrent OpenAI GPT API requests are allowed."""
    while CURRENT_GPT_REQUESTS >= MAX_CONCURRENT_GPT_REQUESTS:
        await asyncio.sleep(1)
    return

async def wait_for_dalle_concurrency():
    """Async function that returns when more concurrent OpenAI DALL-E API requests are allowed."""
    while CURRENT_DALLE_REQUESTS >= MAX_CONCURRENT_DALLE_REQUESTS:
        await asyncio.sleep(1)
    return

async def concurrent_tts(session, voiceID, text, filepath):
    """Sends an async API request to ElevenLabs TTS, and 
    waits to do so if maximum concurrent calls have been reached."""
    global CURRENT_ELEVEN_REQUESTS
    await wait_for_eleven_concurrency()
    CURRENT_ELEVEN_REQUESTS += 1
    result = await eleven.async_tts(session, voiceID, text, filepath)
    CURRENT_ELEVEN_REQUESTS -= 1
    return result

async def concurrent_dalle(session, prompt, filepath):
    """Sends an async API request to OpenAI DALL-E, and 
    waits to do so if maximum concurrent calls have been reached."""
    global CURRENT_DALLE_REQUESTS
    await wait_for_dalle_concurrency()
    CURRENT_DALLE_REQUESTS += 1
    result = await gpt.async_dalle(session, prompt, filepath)
    CURRENT_DALLE_REQUESTS -= 1
    return result

async def concurrent_gpt(session, prompt):
    """Sends an async API request to OpenAI GPT, and 
    waits to do so if maximum concurrent calls have been reached."""
    global CURRENT_GPT_REQUESTS
    await wait_for_gpt_concurrency()
    CURRENT_GPT_REQUESTS += 1
    result = await gpt.async_gpt(session, prompt)
    CURRENT_GPT_REQUESTS -= 1
    return result

# Segment class represents a video segment with specific properties.
# Each segment has 3 elements: Image, Audio, and Text.
# This represents a portion of video that shows an image whule audio TTS
# of someone saying the contents of the text plays.
# This Segment class is built with version control in mind, enabling trying combinations
# of different versions until the user picks the right one for them.
class Segment:
    """Represents a video segment.
    Contains multiple versions of image paths, audio paths, and script text.
    Has methods to change between versions, generate new ones,
    and return a snapshot of the current elements versions."""
    def __init__(self, index, name):
        self.name = name
        self.index = index;
        # List of element versions. Image and Audio elements are paths to the resources.
        # Text elements are stored inside the list itself. Should this change?
        self.image_list: list[str] = []
        self.text_list: list[str] = []
        self.audio_list: list[str] = []
        # Element versions, -1 indicates NO version exists.
        # Versions start at 0, first version will be in xxxx_list[0]
        self.image_version = -1
        self.text_version = -1
        self.audio_version = -1
        # The AsyncIO session, used for API requests
        self.session = None
    
    async def init(self, session, text):
        self.session = session
        self.text_list.append(text)
        self.text_version = 0
        await asyncio.gather(self.new_image(), self.new_audio())
        # await self.new_image()
        # await self.new_audio()
    
    def path(self, ver):
        return self.name + "_" + str(ver)
    
    def change_image_version(self, new_version):
        if 0 <= new_version < len(self.image_list):
            self.image_version = new_version
            return self.image_list[new_version]
        return False

    def change_text_version(self, new_version):
        if 0 <= new_version < len(self.text_list):
            self.text_version = new_version
            return self.text_list[new_version]
        return False
    
    def change_audio_version(self, new_version):
        if 0 <= new_version < len(self.audio_list):
            self.audio_version = new_version
            return self.audio_list[new_version]
        return False

    # Can return false!
    def get_current_image(self):
        if self.image_version < 0:
            return False
        return self.image_list[self.image_version]
    
    def get_current_text(self):
        return self.text_list[self.text_version]
    
    def get_current_audio(self):
        return self.audio_list[self.audio_version]
    
    async def new_image(self, image_prompt=None):
        new_version = len(self.image_list)
        image_prompt = image_prompt or await concurrent_gpt(self.session, prompts['get_image_description'] + self.get_current_text())
        image_prompt = image_prompt or self.get_current_text()
        image_filepath = await concurrent_dalle(self.session, image_prompt, IMAGE_PATH + self.path(new_version))
        if type(image_filepath) == str:
            self.image_list.append(image_filepath)
            self.image_version = new_version
            return image_filepath
        else:
            return False
        
    async def new_audio(self, audio_prompt=None):
        new_version = len(self.audio_list)
        audio_prompt = audio_prompt or self.get_current_text()
        audio_filepath = await concurrent_tts(self.session, eleven.voices['Antoni'], audio_prompt, AUDIO_PATH + self.path(new_version))
        if type(audio_filepath) == str:
            self.audio_list.append(audio_filepath)
            self.audio_version = new_version
            return audio_filepath
        else:
            return False
    
    async def new_text(self, script=None, text_prompt=None):
        new_version = len(self.text_list)
        if text_prompt is None:
            text_prompt = prompts['regenerate_sentence'][0]
            text_prompt += script
            text_prompt += prompts['regenerate_sentence'][1]
            text_prompt += self.get_current_text()
            text_prompt += prompts['regenerate_sentence'][2]
        text = await concurrent_gpt(self.session, text_prompt)
        if type(text) == str:
            self.text_list.append(text)
            self.text_version = new_version
            return text
        else:
            return False
        
    def get_snapshot(self, iv=None, tv=None, av=None):
        iv = iv or self.image_version
        tv = tv or self.text_version
        av = av or self.audio_version
        return {
            "image": self.image_list[iv],
            "text": self.text_list[tv],
            "audio": self.audio_list[av]
        }
    
    def jsonify(self):
        return_object = {
            "index": self.index,
            "images": {
                "list": self.image_list,
                "current_version": self.image_version
            },
            "text": {
                "list": self.text_list,
                "current_version": self.text_version
            },
            "audio": {
                "list": self.audio_list,
                "current_version": self.audio_version
            }
        }
        return return_object
        
        

class Sequence:
    """Sequence represents a list of Segments which make up a video."""
    def __init__(self, project_name):
        self.name = project_name
        self.segments: list[Segment] = []
        self.session = aiohttp.ClientSession()
    
    async def open_session(self):
        self.session = await self.session.__aenter__()
    
    async def close_session(self):
        await self.session.close()
    
    def seg_name(self, segment_number):
        return self.name + "_" + str(segment_number)
    
    async def generate_script_from_subject(self, subject=None):
        prompt = prompts['script_prompt']
        if subject is not None: prompt += "\nWrite the script about " + subject
        return await gpt.async_gpt(self.session, prompt)

    async def generate_sequence_from_subject(self, subject=None):
        script = await self.generate_script_from_subject(subject)
        if type(script) == bool: return False
        return await self.generate_sequence(script)
    
    # Warning: Resets sequence before generating
    async def generate_sequence(self, script: str):
        self.segments = []
        line_number = 0
        coroutines = []
        for line in script.splitlines():
            if line in ['', '\n']: continue
            seg = Segment(line_number, self.seg_name(line_number))
            coroutines.append(seg.init(self.session, line))
            self.add_segment(seg)
            line_number += 1
        await asyncio.gather(*coroutines)
    
    def reindex_segments(self):
        for (i, seg) in enumerate(self.segments):
            seg.index = i
    
    def add_segment(self, segment):
        self.segments.append(segment)
        self.reindex_segments()
     
    def insert_segment(self, segment, index):
        self.segments.insert(index, segment)
        self.reindex_segments()
        
        
    async def generate_insert_segment(self, index):
        script = self.compile_script()
        text_prompt = ''
        if not (0 <= index < len(self.segments)): return False
        elif index == 0:    # beginning
            text_prompt = prompts['generate_sentence_at_beginning'][0]
            text_prompt += script
            text_prompt = prompts['generate_sentence_at_beginning'][1]
        elif index == len(self.segments)-1:    # end
            text_prompt = prompts['generate_sentence_at_end'][0]
            text_prompt += script
            text_prompt = prompts['generate_sentence_at_end'][1]
        else:   # between
            text_prompt = prompts['generate_sentence_between'][0]
            text_prompt += script
            text_prompt += prompts['generate_sentence_between'][1]
            text_prompt += self.segments[index-1].get_current_text()
            text_prompt += prompts['generate_sentence_between'][2]
            text_prompt += self.segments[index+1].get_current_text()
            text_prompt += prompts['generate_sentence_between'][3]
        seg = Segment(index, self.seg_name(index))
        await seg.init(self.session, text_prompt)
        self.insert_segment(seg, index);
    
    def remove_segment(self, index):
        self.segments.pop(index)
    
    def get_segment(self, index):
        return self.segments[index]

    def compile_script(self):
        script = ''
        for seg in self.segments:
            script += seg.get_current_text()
            script += '\n'
        return script
    
    # Future advanced option: "compile audio"
    #   - Generates audio from the compiled script
    #   - Uses some library to get timestamped captions for the audio
    #   - Cuts the audio up into segments based on the timestamps
    #   - Generates the exported video with the cut pieces of audio matched to the images
    # This would make the audio sound more matural, but it would be a lot more work
    def export_video(self, filepath):
        clips = []
        seg_count = 0
        for seg in self.segments:
            audio_clip = mov.AudioFileClip(seg.get_current_audio())
            image_path = seg.get_current_image()
            if image_path is False:
                if seg_count == 0:
                    image_clip = mov.ColorClip(size=(1024, 1024), color=(0, 0, 0))
                else:
                    image_path = self.segments[seg_count-1].get_current_image()
                    image_clip = mov.ImageClip(image_path)
            else:
                image_clip = mov.ImageClip(image_path)
            video_clip = image_clip.set_audio(audio_clip)
            video_clip.duration = audio_clip.duration
            video_clip.fps = 5
            clips.append(video_clip)
            seg_count += 1
        final_clip = mov.concatenate_videoclips(clips, method='compose')
        final_clip.write_videofile(OUTPUT_PATH + filepath + ".mp4")
        return OUTPUT_PATH + filepath + ".mp4"

async def sequence_test_generate_video(output_name, topic):
    """Generates a video from the given topic."""
    seq = Sequence(output_name);
    await seq.open_session()
    await seq.generate_sequence_from_subject(topic)
    seq.export_video(output_name)
    await seq.close_session()

async def main():
    """Main entry point for async execution. Used for isolated testing."""
    sequence_test_generate_video("seq-test", "lettuce")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
