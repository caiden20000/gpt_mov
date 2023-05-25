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

# Straight up delete this function before production
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


def get_username_from_user_id(user_id):
    ret = cur.execute('''
                       SELECT username FROM user
                       WHERE id = ?;
                       ''', (user_id))
    return ret.fetchall() 

def get_user_id_from_username(username):
    ret = cur.execute('''
                       SELECT id FROM user
                       WHERE username = ?
                       ''', (username))
    return ret.fetchall()[0]

def get_sequence_names_by_user_id(user_id):
    ret = cur.execute('''
                       SELECT name FROM sequence
                       WHERE user_id = ?
                       ''', (user_id))
    return ret.fetchall()



init_database()

