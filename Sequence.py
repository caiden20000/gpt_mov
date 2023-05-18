import gpt
import eleven

class Segment:
    def __init__(self, name):
        self.name = name
        self.image_list: list[str] = []
        self.text_list: list[str] = []
        self.audio_list: list[str] = []
        self.image_version = -1
        self.text_version = -1
        self.audio_version = -1
        self.session = None
    
    async def init(self, session, text):
        self.session = session
        self.text_list.append(text)
        self.text_version = 0
        await self.new_image()
        await self.new_audio()
    
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

    def get_current_image(self):
        return self.image_list[self.image_version]
    
    def get_current_text(self):
        return self.text_list[self.text_version]
    
    def get_current_audio(self):
        return self.audio_list[self.audio_version]
    
    async def new_image(self, image_prompt=None):
        new_version = len(self.image_list)
        image_prompt = image_prompt or self.get_current_text()  # Replace with image prompt generator
        image_filepath = await gpt.async_dalle(self.session, image_prompt, self.path(new_version))
        if type(image_filepath) == str:
            self.image_list.append(image_filepath)
            self.image_version = new_version
            return image_filepath
        else:
            return False
        
    async def new_audio(self, audio_prompt=None):
        new_version = len(self.audio_list)
        audio_prompt = audio_prompt or self.get_current_text()
        audio_filepath = await eleven.async_tts(self.session, eleven.voices['Antoni'], audio_prompt, self.path(new_version))
        if type(audio_filepath) == str:
            self.audio_list.append(audio_filepath)
            self.audio_version = new_version
            return audio_filepath
        else:
            return False
    
    async def new_text(self, text_prompt=None):
        new_version = len(self.text_list)
        text_prompt = text_prompt or self.get_current_text()    # Replace with text prompt generator
        text = await gpt.async_gpt(self.session, text_prompt)
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
        
        

class Sequence:
    pass

