import sqlite3

# Initialize the database file
con = sqlite3.connect('database.db')
cur = con.cursor()

# Initialize tables (if not exists)
# Executes the schema.sql file
def init_database():
    script = None;
    with open('schema.sql', 'r') as file:
        script = file.read()
    cur.executescript(script)
    con.commit()

# TODO: Straight up, PLEASE delete this function before production
def clear_database():
    cur.execute("DROP TABLE users;")
    cur.execute("DROP TABLE api_keys;")
    cur.execute("DROP TABLE sequences;")
    cur.execute("DROP TABLE segments;")
    cur.execute("DROP TABLE segment_text;")
    cur.execute("DROP TABLE segment_image;")
    cur.execute("DROP TABLE segment_audio;")

# TODO: hashing
def secure_password(username: str , password: str) -> str:
    return password

# Returns true if username is inserted successfully (ie. username is unique)
def add_user(username: str, password: str) -> bool:
    try:
        cur.execute('''
                    INSERT INTO users (username, username_case, password)
                    VALUES (?, ?, ?);
                    ''', (username.lower(), username, secure_password(username, password)))
        con.commit()
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print("Error: " + str(e))
        return False
    return True

def add_sequence(user_id: int, name: str) -> bool:
    try:
        cur.execute('''
                    INSERT INTO sequences (user_id, name)
                    VALUES (?, ?)
                    ''', (user_id, name))
    except Exception as e:
        print("Error: " + str(e))
        return False
    return True

def get_username_from_user_id(user_id):
    ret = cur.execute('''
                       SELECT username FROM users
                       WHERE id = ?;
                       ''', (user_id,))
    return ret.fetchall()[0][0]

def get_user_id_from_username(username):
    ret = cur.execute('''
                       SELECT id FROM users
                       WHERE username = ?
                       ''', (username.lower(),))
    return ret.fetchall()[0][0]

def get_sequence_names_by_user_id(user_id):
    ret = cur.execute('''
                       SELECT name FROM sequences
                       WHERE user_id = ?
                       ''', (user_id,))
    return [n[0] for n in ret.fetchall()]



init_database()

print(add_user("Caiden2000", "password123"))
uid = get_user_id_from_username("Caiden2000")
add_sequence(uid, "project1")
add_sequence(uid, "project2")
add_sequence(uid, "da_prOjeckt thr33")

print(get_sequence_names_by_user_id(uid))
