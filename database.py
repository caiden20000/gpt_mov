import sqlite3

# Initialize the database file
con = sqlite3.connect('database.db')
cur = con.cursor()

# Initialize tables (if not exists)
def init_database():
    cur.execute('PRAGMA foreign_keys = ON;')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER NOT NULL,
                    username TEXT UNIQUE,
                    password TEXT,
                    PRIMARY KEY (id)
                );
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER NOT NULL,
                    openai TEXT,
                    elevenlabs TEXT,
                    PRIMARY KEY (id)
                );
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS sequence (
                    id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    script TEXT,
                    PRIMARY KEY (id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS segment (
                    id INTEGER NOT NULL,
                    sequence_id INTEGER NOT NULL,
                    index INTEGER NOT NULL,
                    text_version INTEGER,
                    image_version INTEGER,
                    audio_version INTEGER,
                    PRIMARY KEY (id),
                    FOREIGN KEY (sequence_id) REFERENCES sequence(id)
                );
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS segment_text (
                    segment_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    FOREIGN KEY (segment_id) REFERENCES segment(id)
                );
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS segment_image (
                    segment_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    FOREIGN KEY (segment_id) REFERENCES segment(id)
                );
                ''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS segment_audio (
                    segment_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    FOREIGN KEY (segment_id) REFERENCES segment(id)
                );
                ''')


def get_username_from_user_id(user_id):
    ret = cur.execute('''
                       SELECT username FROM user
                       WHERE id = ?
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





