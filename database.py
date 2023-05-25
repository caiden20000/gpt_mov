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





