"""
Module for interfacing with the database schema outlined in schema.sql
"""
import sqlite3
from dataclasses import dataclass


''' Just a note for myself:
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




@dataclass
class Sequence:
    """Sequence dataclass for storing sequence information."""
    id: int
    user_id: int
    name: str
    script: str | None = None

@dataclass
class Segment:
    """Segment dataclass for storing segment information."""
    id: int
    sequence_id: int
    sequence_index: int
    text_version: int
    image_version: int
    audio_version: int

from enum import Enum
# Note: Access the string value with the .value attribute
# eg Element.TEXT.value
# Because string casting gives you the enum member name instead...
class Element(Enum):
    """Enum for the different types of elements in a segment."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


# Initialize the database file
connection = sqlite3.connect('database.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# Initialize tables (if not exists)
# Executes the schema.sql file
def init_database():
    """Initializes the database file from schema.sql"""
    script = None
    with open('schema.sql', 'r', encoding='UTF-8') as file:
        script = file.read()
    cursor.executescript(script)
    connection.commit()

# TODO: hashing
def secure_password(username: str , password: str) -> str:
    """Future function for hashing passwords."""
    username = username.lower()
    return password


### Add functions

# SQL query wrapper that returns false on an integrity error
def integrity_query(query: str, values: tuple) -> bool:
    """Executes a query and returns false if it violates constraints like uniqueness."""
    try:
        cursor.execute(query, values)
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        return False
    return True

# Returns the id of the new user, or 0 if the user already exists.
# By default, SQLite starts IDs at 1, so a value of 0 is FALSE.
# TODO: Change the way passwords are stored and/or validated
def add_user(username, password) -> int:
    """Adds a user to the database. Returns the new user ID."""
    result = integrity_query('''
                             INSERT INTO users (username, username_case, password)
                             VALUES (?, ?, ?);
                             ''', (username.lower(), username, password))
    return cursor.lastrowid if result and cursor.lastrowid else 0

# Returns the new sequence ID
def add_sequence(user_id, sequence_name) -> int:
    """Adds a sequence to the database. Returns the new sequence ID."""
    result = integrity_query('''
                             INSERT INTO sequences (user_id, sequence_name)
                             VALUES (?, ?);
                             ''', (user_id, sequence_name))
    return cursor.lastrowid if result and cursor.lastrowid else 0

# Modifies key if already exists
# Returns true if successful
def add_api_key(user_id: int, key_type: str, key_str: str) -> bool:
    """Adds an API key to the database. Returns true if successful."""
    result = integrity_query('''
                             INSERT INTO api_keys (user_id, key_type, key_str)
                             VALUES (?, ?, ?)
                             ON CONFLICT(user_id, key_type) 
                             DO UPDATE SET key_str = EXCLUDED.key_str;
                             ''', (user_id, key_type, key_str))
    return result

# sequence_index outside [0, length] will be put on the closest extreme.
# Unspecified index == length
# All element versions start at 0, meaning NO version.
# Function appropriately increases indices >= insertion index
# Returns new segment ID
def add_segment(sequence_id, sequence_index = None) -> int:
    """Adds a segment to the sequence at the specified index. Returns the new segment ID."""
    max_index = get_segment_count(sequence_id)
    if sequence_index is None:
        sequence_index = max_index
    else:
        if sequence_index >= max_index:
            sequence_index = max_index
        elif sequence_index <= 0:
            sequence_index = 0
    if sequence_index != max_index:
        # Increase the indices of other segments before inserting
        cursor.execute('''
                       UPDATE segments
                       SET sequence_index = sequence_index + 1
                       WHERE sequence_id = ?
                           AND sequence_index >= ?;
                       ''', (sequence_id, sequence_index))
    # Insertion
    result = integrity_query('''
                             INSERT INTO segments (sequence_id, sequence_index)
                             VALUES (?, ?);
                             ''', (sequence_id, sequence_index))
    return_id = cursor.lastrowid if result and cursor.lastrowid else 0
    return return_id


# Setting "switch" to true will automatically select this new version in the segment.
# Returns the version assigned.
def add_segment_element(segment_id: int, element: Element, content: str, switch: bool = False) -> int:
    """Adds a segment element with an incremented version number. Returns the new version number."""
    next_version = 1 + get_segment_element_version_count(segment_id, element)
    cursor.execute(f'''
                   INSERT INTO segment_{element.value}
                   (segment_id, content, version)
                   VALUES (?, ?, ?);
                   ''', (segment_id, content, next_version))
    if switch:
        change_segment_element_version(segment_id, element, next_version)
    return next_version

### Modify functions

# Returns true if successful
def change_username(user_id, new_username) -> bool:
    """Changes the username of a user. Returns True if successful."""
    cursor.execute('''
                   UPDATE users
                   SET username = ?, username_case = ?
                   WHERE id = ?;
                   ''', (new_username.lower(), new_username, user_id))
    connection.commit()
    return bool(cursor.rowcount)

# Returns true if successful
def change_sequence_name(sequence_id, new_sequence_name) -> bool:
    """Changes the name of a sequence. Returns True if successful."""
    cursor.execute('''
                   UPDATE sequences
                   SET sequence_name = ?
                   WHERE id = ?;
                   ''', (new_sequence_name, sequence_id))
    connection.commit()
    return bool(cursor.rowcount)

# Moves a segment to a new index
# Returns the new index, or -1 if unsucessful
# algorithm:
#   Set segment index to -1
#   Set all indices >= old_index --
#   Increase all indices >= new_index
#   Set segment index to new_index
# There is a way to optimize this, but it doesn't sound fun.
def change_segment_index(segment_id, new_index) -> bool:
    """Moves a segment to a new index. Changes the indices of other segments accordingly. 
    Returns True if successful."""
    # Get sequence_id because we need it for increasing indices
    result = cursor.execute('''
                            SELECT sequence_id, sequence_index FROM segments
                            WHERE id = ?;
                            ''', (segment_id,))
    row = result.fetchone()
    if row is None:
        return False
    sequence_id = row['sequence_id']
    old_index = row['sequence_index']
    
    # Set index to -1
    result = cursor.execute('''
                            UPDATE segments
                            SET sequence_index = -1
                            WHERE id = ?;
                            ''', (segment_id,))
    
    # Decrease all indices above old_index
    # Leaves indices above new_index unchanged
    cursor.execute('''
                   UPDATE segments
                   SET sequence_index = sequence_index - 1
                   WHERE sequence_id = ?
                       AND sequence_index >= ?;
                   ''', (sequence_id, old_index))
    
    # Increase the indices of other segments before inserting
    cursor.execute('''
                   UPDATE segments
                   SET sequence_index = sequence_index + 1
                   WHERE sequence_id = ?
                       AND sequence_index >= ?;
                   ''', (sequence_id, new_index))
    # Insert
    result = cursor.execute('''
                            UPDATE segments
                            SET sequence_index = ?
                            WHERE id = ?;
                            ''', (new_index, segment_id))
    connection.commit()
    return bool(cursor.rowcount)

# Does not check if the version exists.
def change_segment_element_version(segment_id: int, element: Element, version: int) -> bool:
    """Changes the active version of a segment element. Returns true if successful."""
    cursor.execute(f'''
                   UPDATE segments
                   SET {element.value}_version = ?
                   WHERE id = ?;
                   ''', (version, segment_id))
    return bool(cursor.rowcount)

### Get functions
# All get functions will return None if the entry doesn't exist.
def get_id_from_username(username: str) -> int | None:
    """Returns the user ID of the given username."""
    result = cursor.execute('''
                            SELECT id FROM users
                            WHERE username = ?;
                            ''', (username.lower(),))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_username_from_id(user_id: int) -> str | None:
    """Returns the username of the given user ID."""
    result = cursor.execute('''
                            SELECT username_case FROM users
                            WHERE id = ?;
                            ''', (user_id,))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_api_key(user_id: int, key_type: str) -> str | None:
    """Returns the API key of the given type belonging to the user.
    Current types are 'openai' and 'elevenlabs'."""
    result = cursor.execute('''
                            SELECT key_str FROM api_keys
                            WHERE user_id = ? AND key_type = ?;
                            ''', (user_id, key_type))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_sequences(user_id: int) -> list[Sequence]:
    """Returns a list of Sequence objects belonging to the user."""
    result = cursor.execute('''
                            SELECT * FROM sequences
                            WHERE user_id = ?;
                            ''', (user_id,))
    rows = result.fetchall()
    return [Sequence(row['id'], row['user_id'], row['name'], row['script']) for row in rows]
    

def get_sequence(sequence_id: int) -> Sequence | None:
    """Returns a Sequence object with the given id."""
    result = cursor.execute('''
                            SELECT * FROM sequences
                            WHERE id = ?;
                            ''', (sequence_id,))
    row = result.fetchone()
    if row is None: 
        return None
    return Sequence(row['id'], row['user_id'], row['sequence_name'], row['script'])

def get_segment(segment_id: int) -> Segment | None:
    """Returns a Segment object with the given id."""
    result = cursor.execute('''
                            SELECT * FROM segments
                            WHERE id = ?;
                            ''', (segment_id,))
    row = result.fetchone()
    if row is None:
        return None
    segment = Segment(row['id'], row['sequence_id'], row['sequence_index'],
                      row['text_version'], row['image_version'], row['audio_version'])
    return segment

def get_segments(sequence_id: int) -> list[Segment] | None:
    """Returns a list of Segment objects in a sequence in index order."""
    result = cursor.execute('''
                            SELECT * from segments
                            WHERE sequence_id = ?
                            ORDER BY sequence_index;
                            ''', (sequence_id,))
    segments = []
    for row in result.fetchall():
        segments.append(Segment(row['id'], row['sequence_id'], row['sequence_index'],
                      row['text_version'], row['image_version'], row['audio_version']))
    return segments

def get_segment_from_index(sequence_id: int, sequence_index: int) -> Segment | None:
    """Returns the segment at the index in a sequence."""
    result = cursor.execute('''
                            SELECT * FROM segments
                            WHERE sequence_id = ?
                                AND sequence_index = ?;
                            ''', (sequence_id, sequence_index))
    row = result.fetchone()
    if row is None:
        return None
    segment = Segment(row['id'], row['sequence_id'], row['sequence_index'],
                      row['text_version'], row['image_version'], row['audio_version'])
    return segment

# If version is unspecified, the function will return the version specified by the segment.
def get_segment_element(segment_id: int, element: Element, version: int = 0) -> str | None:
    """Returns the content of a segment element.
    If version is unspecified, the function will return the version specified by the segment."""
    if version == 0:
        # If version is unspecified, get the version specified in segment.{element.value}_version
        result = cursor.execute(f'''
                        SELECT content FROM sequence_{element.value}
                        INNER JOIN segments
                            ON segment_id = segments.id
                        WHERE segment_id = ? 
                            AND version = {element.value}_version;
                        ''', (segment_id,))
    else:
        result = cursor.execute(f'''
                        SELECT content FROM sequence_{element.value}
                        INNER JOIN segments
                            ON segment_id = segments.id
                        WHERE segment_id = ? 
                            AND version = ?;
                        ''', (segment_id, version))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_segment_count(sequence_id: int) -> int:
    """Returns the number of segments in a sequence."""
    result = cursor.execute('''
                            SELECT COUNT(*) FROM segments
                            WHERE sequence_id = ?;
                            ''', (sequence_id,))
    # Usually check for row == None, but aggregate function should guarantee return.
    return result.fetchone()[0]
    
def get_segment_element_version_count(segment_id: int, element: Element) -> int:
    """Returns the number of versions of a segment element."""
    result = cursor.execute(f'''
                            SELECT COUNT(*) FROM segment_{element.value}
                            WHERE segment_id = ?;
                            ''', (segment_id,))
    return result.fetchone()[0]



# Existential functions

def does_username_exist(username: str) -> bool:
    """Returns true if the username exists in the database. Case insensitive."""
    result = cursor.execute('''
                            SELECT id FROM users
                            WHERE username = ?;
                            ''', (username.lower(),))
    return bool(result.fetchone())

def does_user_id_exist(user_id: int) -> bool:
    """Returns true if the user id exists in the database."""
    result = cursor.execute('''
                            SELECT id FROM users
                            WHERE id = ?;
                            ''', (user_id,))
    return bool(result.fetchone())

def does_sequence_name_exist(sequence_name: str, user_id: int = 0) -> bool:
    """Returns true if the sequence name exists in the database. Case insensitive."""
    if user_id == 0:
        result = cursor.execute('''
                                SELECT id FROM sequences
                                WHERE sequence_name = ?;
                                ''', (sequence_name.lower(),))
    else:
        result = cursor.execute('''
                                SELECT id FROM sequences
                                WHERE sequence_name = ?
                                    AND user_id = ?;
                                ''', (sequence_name.lower(), user_id))
    return bool(result.fetchone())

def does_sequence_id_exist(sequence_id: int) -> bool:
    """Returns true if the sequence id exists in the database."""
    result = cursor.execute('''
                            SELECT id FROM sequences
                            WHERE id = ?;
                            ''', (sequence_id,))
    return bool(result.fetchone())

def does_segment_id_exist(segment_id: int) -> bool:
    """Returns true if the segment id exists in the database."""
    result = cursor.execute('''
                            SELECT id FROM segments
                            WHERE id = ?;
                            ''', (segment_id,))
    return bool(result.fetchone())

def does_sequence_index_exist(sequence_id: int, sequence_index: int) -> bool:
    """Returns true if a segment exists at the given sequence index."""
    result = cursor.execute('''
                            SELECT id FROM segments
                            WHERE sequence_id = ?
                                AND sequence_index = ?;
                            ''', (sequence_id, sequence_index))
    return bool(result.fetchone())

def does_segment_element_version_exist(segment_id: int, element: Element, version: int) -> bool:
    """Returns true if a segment element exists with the specified version.
    Segment element versions begin at 1."""
    result = cursor.execute(f'''
                            SELECT id FROM segment_{element.value}
                            WHERE segment_id = ?
                                AND version = ?;
                            ''', (segment_id, version))
    return bool(result.fetchone())

init_database()
