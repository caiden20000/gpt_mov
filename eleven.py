import requests

voicesURL = 'https://api.elevenlabs.io/v1/voices'
ttsURL = 'https://api.elevenlabs.io/v1/text-to-speech/'
elevenkey = ''
# get key from elevenkey.txt
with open('keys/elevenkey.txt', 'r+') as f:
    elevenkey = f.readline().strip()


def request_voice_list():
    headers = {
        'Content-Type': 'application/json',
        'xi-api-key': elevenkey
    }
    response = requests.get(voicesURL, headers=headers)
    if response.ok:
        return response.json()['voices']
    else:
        return 'Error: ' + response.text

def tts(voiceID, text, filename):
    print("Fetching tts...")
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        'xi-api-key': elevenkey
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0
        }
    }
    response = requests.post(ttsURL + voiceID, headers=headers, json=data)
    filepath = "audio/" + filename + '.mp3'
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("File created! (?) " + filepath)
    return filepath
    # if response.ok:
    #     print("Response OK! Writing to file " + filename + ".mp3...")
    #     with open(filename + '.mp3', 'wb') as file:
    #         file.write(response.content)
    #         print('File saved successfully.')
    # else:
    #     print('Error: ' + response.text)
# voices = request_voice_list()
# for voice in voices:
#     print(f"{voice['voice_id']}: {voice['name']}")


voices = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Arnold": "VR6AewLTigWG4xSOukaG",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Sam": "yoZ06aMxZJJ28mfd3POQ",
    "kiwi historio": "5Yi1qKBaQH9k2LxPy9U5",
    "Luddy": "GhsUqu2Ut3upfgNa579f",
    "Explano": "gg15OiMVm7XQFCA9VB58"
}

def generate_test_list():
    for voice in voices.items():
        tts(voice[1], "Hello! This is a test.", "audio/" + voice[0])

# generate_test_list()
# tts(voices['Luddy'], "BOYS! Today, the plan is simple.", "audio/test")


# interface Sample {
#     sample_id: string;
#     file_name: string;
#     mime_type: string;
#     size_bytes: number;
#     hash: string;
# }

# interface VoiceSettings {
#     stabilit: number;
#     similarity_boost: number;
# }

# interface Voice {
#     voice_id: string;
#     name: string;
#     samples: Sample[];
#     category: string;
#     fine_tuning: any;
#     labels: {[key: string]: string};
#     description: string;
#     preview_url: string;
#     available_for_tiers: string[];
#     settings: VoiceSettings;
# }

# interface VoiceRequest {
#     text: string;
#     voice_settings: VoiceSettings;
# }
