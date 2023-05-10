from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

def add_static_image_to_audio(image_path, audio_path):
    """Create and save a video file to `output_path` after 
    combining a static image that is located in `image_path` 
    with an audio file in `audio_path`"""
    # create the audio clip object
    audio_clip = AudioFileClip(audio_path)
    # create the image clip object
    image_clip = ImageClip(image_path)
    # use set_audio method from image clip to combine the audio with the image
    video_clip = image_clip.set_audio(audio_clip)
    # specify the duration of the new clip to be the duration of the audio clip
    video_clip.duration = audio_clip.duration
    # set the FPS to 1
    video_clip.fps = 5
    # write the resuling video clip
    # video_clip.write_videofile(output_path)
    # return video file
    return video_clip

# ia_tuple = (image_file_name, audio_file_name)
def ia_tuple_to_clip(ia_tuple):
    return add_static_image_to_audio(ia_tuple[0], ia_tuple[1])

def ia_tuple_arr_to_videofile(ia_tuple_array, output_path):
    clip_array = []
    for ia_tuple in ia_tuple_array:
        clip_array.append(ia_tuple_to_clip(ia_tuple))
    concatenate_videoclips(clip_array, method='compose').write_videofile(output_path)


def generate_n_ia_tuples(n):
    ia_tuple_array = []
    for i in range(n):
        ia_tuple_array.append((f"images/{i+1}.jpg", f"audio/{i+1}.wav"))
    return ia_tuple_array


# src = generate_n_ia_tuples(15)
# ia_tuple_arr_to_videofile(src, "output/output.mp4")

# o1 = add_static_image_to_audio("i1.jpg", "a1.wav", "o1.mp4")
# o2 = add_static_image_to_audio("i2.jpg", "a2.wav", "o2.mp4")

# output = concatenate_videoclips([o2, o1], method='compose')
# output.write_videofile("output.mp4")