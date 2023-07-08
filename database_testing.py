"""
This module is used for running test code to see if my database works as intended.
This is not intended to be interfaced with in production.
"""
from faker import Faker
import database

fake = Faker()

def generate_user():
    return database.add_user(fake.user_name(), fake.password(length=12))

def generate_api_key(user_id, key_type):
    key_str = fake.lexify(text='????????????????????')
    return database.add_api_key(user_id, key_type, key_str)

def generate_empty_sequence(user_id):
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
    return database.add_segment_element(segment_id, database.Element.AUDIO, 
                                        fake.file_path(depth=3, category='audio'), True)

def generate_segment(sequence_id, versions = 1):
    segment_id = generate_empty_segment(sequence_id)
    for i in range(versions):
        generate_segment_text(segment_id)
        generate_segment_image(segment_id)
        generate_segment_audio(segment_id)
    return segment_id

def generate_sequence(user_id, length = 5, ver_count = 1):
    sequence_id = generate_empty_sequence(user_id)
    for i in range(length):
        generate_segment(sequence_id, ver_count)
    return sequence_id

def generate_user_with_sequences(seq_count = 2, seq_len = 5, ver_count = 1):
    user_id = generate_user()
    for i in range(seq_count):
        generate_sequence(user_id, seq_len, ver_count)
    return user_id



# Ad-hoc population
def populate():
    sequence_count = 5
    sequence_length = 8
    version_count = 4
    for i in range(10):
        print(f"Generating user {i} with {sequence_count} sequences...")
        user_id = generate_user_with_sequences(sequence_count, sequence_length, version_count)
        generate_api_key(user_id, 'openai')
        generate_api_key(user_id, 'elevenlabs')

database.drop_all()
database.init_database()
populate()

# Expected output:
# 1 2 3 4 5 6 7 8 -> 1 2 3 5 6 4 7 8
# Works as expected
def test_change_segment_index(froom, too):
    """Tests the database function change_segment_index"""
    first_seq = database.get_sequence(1)
    if first_seq is None: exit()
    segments = database.get_segments(first_seq.id)
    if segments is None: exit()
    segid = 0
    for seg in segments:
        if seg.sequence_index == froom: segid = seg.id
        print(f'index {seg.sequence_index}\tid {seg.id}')
        
    print(f"\nChanging {froom} to {too}...\n")
    database.change_segment_index(segid, too)

    segments = database.get_segments(first_seq.id)
    if segments is None: exit()
    for seg in segments:
        print(f'index {seg.sequence_index}\tid {seg.id}')