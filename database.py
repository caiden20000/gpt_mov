import sqlite3

# make a database
con = sqlite3.connect('test_database.db')
cur = con.cursor()

# Test schema
cur.execute('''
PRAGMA foreign_keys = ON;
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER,
    username TEXT,
    password TEXT,
    PRIMARY KEY (id)
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS project (
    id INTEGER,
    user_id INTEGER,
    name TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);
''')

def add_user(username, password):
    cur.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
    con.commit()

def add_project(user_id, name):
    cur.execute("INSERT INTO project (user_id, name) VALUES (?, ?)", (user_id, name))
    con.commit()

def print_user_table():
    res = cur.execute("SELECT * FROM user")
    for row in res:
        print(row)

def print_project_table():
    res = cur.execute("SELECT * FROM project")
    for row in res:
        print(row)

def print_projects():
    res = cur.execute("SELECT name, username FROM project INNER JOIN user ON user_id = user.id")
    for row in res:
        print(row)
    

# add_user("ChigChungos", "passwd1")
# add_project(2, "test projenct")
# add_project(3, "proj1")
# add_project(3, "new projeect 1")
print_user_table()
print("\n")
print_project_table()
print("\n")
print_projects()


