import database
from faker import Faker

fake = Faker()

def generate_user():
    return database.add_user(fake.user_name(), fake.password(length=12))

def generate_api_key(username, key_type):
    user_id = database.get_id_from_username(username)
    if user_id is None: 
        return
    key_str = fake.lexify(text='????????????????????')
    return database.add_api_key(user_id, key_type, key_str)

def generate_empty_sequence(username):
    user_id = database.get_id_from_username(username)
    sequence_name = ' '.join(fake.words(nb=2))
    return database.add_sequence(user_id, sequence_name)

def generate_empty_segment(sequence_id):
    return database.add_segment(sequence_id)

def generate_segment_text(segment_id):
    return database.add_segment_element(segment_id, database.Element.TEXT, 
                                        fake.paragraph(nb_sentences=1, variable_nb_sentences=False), True)

def generate_segment_image(segment_id):
    return database.add_segment_element(segment_id, database.Element.IMAGE, 
                                        fake.file_path(depth=3, category='image'), True)
    
def generate_segment_audio(segment_id):
    return database.add_segment_element(segment_id, database.Element.IMAGE, 
                                        fake.file_path(depth=3, category='audio'), True)

def generate_segment(sequence_id, versions = 1):
    segment_id = generate_empty_segment(sequence_id)
    for i in range(versions):
        generate_segment_text(segment_id)
        generate_segment_image(segment_id)
        generate_segment_audio(segment_id)
    return segment_id

def generate_sequence(username, length = 5):
    sequence_id = generate_empty_sequence(username)
    for i in range(length):
        generate_segment(sequence_id)
    return sequence_id

