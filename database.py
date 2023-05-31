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

from enum import Enum
class Element(Enum):
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


### Add functions

# SQL query wrapper that returns false on an integrity error
def integrity_query(query: str, values: tuple) -> bool:
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

# sequence_index outside [0, length] will be put on the closest extreme.
# Unspecified index == length
# All element versions start at 0, meaning NO version.
# Function appropriately increases indices >= insertion index
# Returns new segment ID
def add_segment(sequence_id, sequence_index = None) -> int:
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
    pass
 
### Modify functions

# Returns true if successful
def change_username(user_id, new_username) -> bool:
    cursor.execute('''
                   UPDATE users
                   SET username = ?, username_case = ?
                   WHERE id = ?;
                   ''', (new_username.lower(), new_username, user_id))
    connection.commit()
    return bool(cursor.rowcount)

# Returns true if successful
def change_sequence_name(sequence_id, new_sequence_name) -> bool:
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
def change_segment_index(segment_id, new_index) -> int:
    # Get sequence_id because we need it for increasing indices
    result = cursor.execute('''
                            SELECT sequence_id, sequence_index FROM segments
                            WHERE id = ?;
                            ''', (segment_id,))
    row = result.fetchone()
    if row is None:
        return -1
    sequence_id = row.sequence_id
    old_index = row.sequence_index
    
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
                            WHERE id = ?
                            ''', (new_index, segment_id))
    connection.commit()
    return new_index

# Does not check if the version exists.
def change_segment_element_version(segment_id: int, element: Element, version: int) -> bool:
    """Changes the active version of a segment element. Returns true if successful."""
    cursor.execute(f'''
                   UPDATE segments
                   SET {element}_version = ?
                   WHERE segment_id = ?;
                   ''', (version, segment_id))
    return bool(cursor.rowcount)

### Get functions
# All get functions will return None if the entry doesn't exist.
def get_id_from_username(username: str) -> int | None:
    result = cursor.execute('''
                            SELECT id FROM users
                            WHERE username = ?;
                            ''', (username.lower(),))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_username_from_id(user_id: int) -> str | None:
    result = cursor.execute('''
                            SELECT username_case FROM users
                            WHERE id = ?;
                            ''', (user_id,))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_api_key(user_id: int, type: str) -> str | None:
    result = cursor.execute('''
                            SELECT key_str FROM api_keys
                            WHERE user_id = ? AND key_type = ?;
                            ''', (user_id, type))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_sequences(user_id: int) -> list[Sequence]:
    result = cursor.execute('''
                            SELECT * FROM sequence
                            WHERE user_id = ?;
                            ''', (user_id,))
    rows = result.fetchall()
    return [Sequence(row.id, row.user_id, row.name, row.script) for row in rows]
    

def get_sequence(sequence_id: int) -> Sequence | None:
    result = cursor.execute('''
                            SELECT * FROM sequence
                            WHERE id = ?;
                            ''', (sequence_id,))
    row = result.fetchone()
    if row is None: 
        return None
    return Sequence(row.id, row.user_id, row.name, row.script)

def get_segment(segment_id: int) -> Segment | None:
    result = cursor.execute('''
                            SELECT * FROM segments
                            WHERE id = ?;
                            ''', (segment_id,))
    row = result.fetchone()
    if row is None:
        return None
    segment = Segment(row.id, row.sequence_id, row.sequence_index,
                      row.text_version, row.image_version, row.audio_version)
    return segment

def get_segment_from_index(sequence_id: int, sequence_index: int) -> Segment | None:
    result = cursor.execute('''
                            SELECT * FROM segments
                            WHERE sequence_id = ?
                                AND sequence_index = ?;
                            ''', (sequence_id, sequence_index))
    row = result.fetchone()
    if row is None:
        return None
    segment = Segment(row.id, row.sequence_id, row.sequence_index,
                      row.text_version, row.image_version, row.audio_version)
    return segment

# If version is unspecified, the function will return the version specified by the segment.
def get_segment_element(segment_id: int, element: Element, version: int = 0) -> str | None:
    if version == 0:
        # If version is unspecified, get the version specified in segment.{element}_version
        result = cursor.execute(f'''
                        SELECT content FROM sequence_{element}
                        INNER JOIN segments
                            ON segment_id = segments.id
                        WHERE segment_id = ? 
                            AND version = {element}_version;
                        ''', (segment_id,))
    else:
        result = cursor.execute(f'''
                        SELECT content FROM sequence_{element}
                        INNER JOIN segments
                            ON segment_id = segments.id
                        WHERE segment_id = ? 
                            AND version = ?;
                        ''', (segment_id, version))
    row = result.fetchone()
    return row[0] if row is not None else None

def get_segment_count(sequence_id: int) -> int:
    result = cursor.execute('''
                            SELECT COUNT(*) FROM segments
                            WHERE sequence_id = ?;
                            ''', (sequence_id,))
    # Usually check for row == None, but aggregate function should guarantee return.
    return result.fetchone()[0]
    
def get_segment_element_version_count(segment_id: int, element: Element) -> int:
    result = cursor.execute(f'''
                            SELECT COUNT(*) FROM segment_{element}
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
                            SELECT id FROM segment_{element}
                            WHERE segment_id = ?
                                AND version = ?;
                            ''', (segment_id, version))
    return bool(result.fetchone())

init_database()