# Prerequisites
### API keys
You must provide API keys for the following services:
- OpenAI
- ElevenLabs

To use your personal keys in this program, do the following:
- Create the file `keys/elevenkey.txt` and paste your ElevenLabs API key inside.
- Create the file `keys/openaikey.txt` and paste your OpenAI API key inside.
- Make sure you do not include other content such as whitespace or newlines in these files.

Your API keys will be read and used by the program when running. There is NO rate limit implemented (as of yet). It is your responsibility to understand how and when calls are made and use the program in a financially mindful way. Or don't. It's your money.

### Requirements
- I'd recommend the latest version of python, since I don't know if there's any version-specific syntax or features. Python 3.10.8 is good.
- Make sure to install all requirements with `pip install -r requirements.txt`

### TODO
- Remeber how it works and tie it all together. It kind of got away from me.
- Clearly outline the requirements for the completion of the project.
- Design the functions based on those requirements.
- Implmenet those functions

### TODO afterwards
- Convert prompts.json from string arrays to a formatted string for more customizability.
- Implement video captions