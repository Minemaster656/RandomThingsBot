import sqlite3

WPG_whitelist = [609348530498437140]

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
def writeUserToDB(user):
    cursor.execute("INSERT INTO users (userid, username) VALUES (?, ?)", (user.id, user.name))
    conn.commit()
def initTables():
    cursor.execute('''CREATE IF NOT EXISTS TABLE countries (
    userid         INTEGER,
    countryname    TEXT,
    government     TEXT,
    ideology       TEXT,
    currency       TEXT,
    about          TEXT,
    flagURL        TEXT,
    extraSymbols   TEXT,
    ownerdata      TEXT,
    id             TEXT,
    money          INTEGER DEFAULT (0),
    population     INTEGER DEFAULT (0),
    agreement      INTEGER DEFAULT (0),
    area           INTEGER DEFAULT (0),
    infrastructure INTEGER DEFAULT (0),
    medicine       INTEGER DEFAULT (0),
    eudication     INTEGER DEFAULT (0),
    attack         INTEGER DEFAULT (0),
    armor          INTEGER DEFAULT (0),
    fuel           INTEGER DEFAULT (0),
    fuel_space     INTEGER DEFAULT (0),
    fuel_star      INTEGER DEFAULT (0),
    fuel_void      INTEGER DEFAULT (0),
    transport      INTEGER DEFAULT (0),
    tech_index     INTEGER DEFAULT (0),
    tech           TEXT,
    food           INTEGER DEFAULT (0),
    materials      INTEGER DEFAULT (0) 
)''')
