'''
Interface:

### Add functions

# Returns new user ID
add_user(username, password) -> int
# Returns the new sequence ID
add_sequence(sequence_name, user_id) -> int
# Modifies key if already exists
# Returns true if successful
add_api_key(user_id: int, type: string, key: string) -> bool

# If index < 0, segment is added to the beginning of the sequence
# If index > max, segment is added to the end of the sequence
# All versions start at 0, meaning NO version.
# Function will ++ all >= indices to insert.
# sequence_index unspecified will add to the end of the sequence.
# Returns new segment ID
add_segment(sequence_id, sequence_index = last) -> int

# Setting "switch" to true will automatically select this new version in the segment.
# Returns the version assigned.
add_segment_element(segment_id: int, element: Element, content: str, switch: bool = false) -> int


### Modify functions

# Returns true if successful
change_username(user_id) -> bool
# Returns true if successful
change_sequence_name(sequence_id) -> bool

# Returns the new index, or false if unsucessful
change_segment_index(segment_id, new_index) -> int | bool

# No modifying segment elements, all "changes" are new versions.
# For text, GUI will have a "lock in new version" button after modification


### Get functions
# All get functions will return false if the entry doesn't exist.

get_id_from_username(username: str) -> int | False
get_username_from_id(user_id: int) -> str | False

get_api_key(user_id: int, type: str) -> str | False

get_sequences(user_id: int) -> Sequence[]
get_sequence(sequence_id: int) -> Sequence

get_segment(segment_id: int) -> Segment
get_segment_element(segment_id: int, element: Element, version: int = -1) -> str

get_segment_count(sequence_id: int) -> int
get_segment_element_version_count(segment_id: int, element: Element) -> int



# Existential functions

does_username_exist(username: str) -> bool
does_user_id_exist(user_id: int) -> bool

does_sequence_name_exist(user_id, sequence_name: str) -> bool
does_sequence_id_exist(sequence_id: int) -> bool

does_segment_id_exist(segment_id: int) -> bool
does_sequence_index_exist(sequence_id: int, sequence_index: int) -> bool

does_segment_element_version_exist(sequence_id: int, element: Element, version: int) -> bool


-- Generate the script for a sequence automatically:
-- Boy I hope this would work!
SELECT GROUP_CONCAT(content, ' ')
FROM segment_text
INNER JOIN segments
    ON segment_id = segments.id
WHERE sequence_id = <?>
    AND version = text_version
ORDER BY sequence_index;


'''


import sqlite3
from dataclasses import dataclass

@dataclass
class Sequence:
    id: int
    user_id: int
    name: str
    script: str | None = None

@dataclass
class Segment:
    id: int
    sequence_id: int
    sequence_index: int
    text_version: int
    image_version: int
    audio_version: int
    


# Initialize the database file
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Initialize tables (if not exists)
# Executes the schema.sql file
def init_database():
    script = None;
    with open('schema.sql', 'r') as file:
        script = file.read()
    cursor.executescript(script)
    connection.commit()

# TODO: Straight up, PLEASE delete this function before production
def clear_database():
    cursor.execute("DROP TABLE users;")
    cursor.execute("DROP TABLE api_keys;")
    cursor.execute("DROP TABLE sequences;")
    cursor.execute("DROP TABLE segments;")
    cursor.execute("DROP TABLE segment_text;")
    cursor.execute("DROP TABLE segment_image;")
    cursor.execute("DROP TABLE segment_audio;")

# TODO: hashing
def secure_password(username: str , password: str) -> str:
    return password

# # Returns true if username is inserted successfully (ie. username is unique)
# def add_user(username: str, password: str) -> bool:
#     try:
#         cursor.execute('''
#                     INSERT INTO users (username, username_case, password)
#                     VALUES (?, ?, ?);
#                     ''', (username.lower(), username, secure_password(username, password)))
#         connection.commit()
#     except sqlite3.IntegrityError:
#         return False
#     except Exception as e:
#         print("Error: " + str(e))
#         return False
#     return True

# def add_sequence(user_id: int, name: str) -> bool:
#     try:
#         cursor.execute('''
#                     INSERT INTO sequences (user_id, name)
#                     VALUES (?, ?)
#                     ''', (user_id, name))
#     except Exception as e:
#         print("Error: " + str(e))
#         return False
#     return True

# def get_username_from_user_id(user_id):
#     ret = cursor.execute('''
#                        SELECT username FROM users
#                        WHERE id = ?;
#                        ''', (user_id,))
#     return ret.fetchall()[0][0]

# def get_user_id_from_username(username):
#     ret = cursor.execute('''
#                        SELECT id FROM users
#                        WHERE username = ?
#                        ''', (username.lower(),))
#     return ret.fetchall()[0][0]

# def get_sequences_by_user_id(user_id):
#     ret = cursor.execute('''
#                        SELECT id, name FROM sequences
#                        WHERE user_id = ?
#                        ''', (user_id,))
#     return ret.fetchall()

from enum import Enum
class Element(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"

def get_segment_element(element: Element, sequence_id: int, sequence_index: int, version: int = -1):
    if version == -1:
        # If version is unspecified, get the version specified in segment.{element}_version
        ret = cursor.execute(f'''
                        SELECT content FROM sequence_{element}
                        INNER JOIN segments
                            ON segment_id = segments.id
                        WHERE sequence_id = ? 
                            AND sequence_index = ?
                            AND version = {element}_version;
                        ''', (sequence_id, sequence_index))
    else:
        ret = cursor.execute(f'''
                        SELECT content FROM sequence_{element}
                        INNER JOIN segments
                            ON segment_id = segments.id
                        WHERE sequence_id = ? 
                            AND sequence_index = ?
                            AND version = ?;
                        ''', (sequence_id, sequence_index, version))
    return ret.fetchall()[0][0]


### Add functions

# SQL query wrapper that returns false on an integrity error
def integrity_query(query: str, values: tuple) -> bool:
    try:
        cursor.execute(query, values)
        connection.commit()
    except sqlite3.IntegrityError:
        return False
    return True

# Returns the id of the new user, or 0 if the user already exists.
# By default, SQLite starts IDs at 1, so a value of 0 is FALSE.
# TODO: Change the way passwords are stored and/or validated
def add_user(username, password) -> int:
    result = integrity_query('''
                             INSERT INTO users (username, username_case, password)
                             VALUES (?, ?, ?)
                             ''', (username.lower(), username, password))
    return cursor.lastrowid if result and cursor.lastrowid else 0

# Returns the new sequence ID
def add_sequence(user_id, sequence_name) -> int:
    result = integrity_query('''
                             INSERT INTO sequences (user_id, sequence_name)
                             VALUES (?, ?)
                             ''', (user_id, sequence_name))
    return cursor.lastrowid if result and cursor.lastrowid else 0

# Modifies key if already exists
# Returns true if successful
def add_api_key(user_id: int, key_type: str, key_str: str) -> bool:
    result = integrity_query('''
                             INSERT INTO api_keys (user_id, key_type, key_str)
                             VALUES (?, ?, ?)
                             ON CONFLICT(user_id, key_type) 
                             DO UPDATE SET key_str = EXCLUDED.key_str
                             ''', (user_id, key_type, key_str))
    return result

# If index < 0, segment is added to the beginning of the sequence
# If index > max, segment is added to the end of the sequence
# All versions start at 0, meaning NO version.
# Function will ++ all >= indices to insert.
# sequence_index unspecified will add to the end of the sequence.
# Returns new segment ID
def add_segment(sequence_id, sequence_index = None) -> int:
    if sequence_index is None:
        sequence_index = get_segment_count(sequence_id)
    else:
        max_index = get_segment_count(sequence_id)
        if sequence_index >= max_index:
            sequence_index = max_index
        elif sequence_index <= 0:
            sequence_index = 0
    result = integrity_query('''
                             INSERT INTO segments (sequence_id, sequence_index)
                             VALUES (?, ?)
                             ''', (sequence_id, sequence_index))
    return_id = cursor.lastrowid if result and cursor.lastrowid else 0
    # TODO: increase the indices of all segments >= sequence_index
    return return_id
    

# Setting "switch" to true will automatically select this new version in the segment.
# Returns the version assigned.
def add_segment_element(segment_id: int, element: Element, content: str, switch: bool = False) -> int:
    pass
 
### Modify functions

# Returns true if successful
def change_username(user_id) -> bool:
    pass
# Returns true if successful
def change_sequence_name(sequence_id) -> bool:
    pass

# Returns the new index, or -1 if unsucessful
def change_segment_index(segment_id, new_index) -> int:
    result = cursor.execute('''
                            UPDATE segments
                            SET sequence_index = ?
                            WHERE id = ?
                            ''', (new_index, segment_id))
    connection.commit()
    return new_index
    
        
    

def change_segment_element_version(segment_id: int, element: Element, version: int) -> bool:
    pass

### Get functions
# All get functions will return false if the entry doesn't exist.
def get_id_from_username(username: str) -> int | bool:
    pass
def get_username_from_id(user_id: int) -> str | bool:
    pass

def get_api_key(user_id: int, type: str) -> str | bool:
    pass

def get_sequences(user_id: int) -> Sequence[]:
    pass
def get_sequence(sequence_id: int) -> Sequence:
    pass

def get_segment(segment_id: int) -> Segment:
    pass
def get_segment_element(segment_id: int, element: Element, version: int = -1) -> str:
    pass

def get_segment_count(sequence_id: int) -> int:
    result = cursor.execute('''
                            SELECT COUNT(*) FROM segments
                            WHERE sequence_id = ?
                            ''')
    
    
    
def get_segment_element_version_count(segment_id: int, element: Element) -> int:
    pass



# Existential functions

def does_username_exist(username: str) -> bool:
    pass
def does_user_id_exist(user_id: int) -> bool:
    pass
def does_sequence_name_exist(user_id, sequence_name: str) -> bool:
    pass
def does_sequence_id_exist(sequence_id: int) -> bool:
    pass
def does_segment_id_exist(segment_id: int) -> bool:
    pass
def does_sequence_index_exist(sequence_id: int, sequence_index: int) -> bool:
    pass
def does_segment_element_version_exist(sequence_id: int, element: Element, version: int) -> bool:
    pass

init_database()