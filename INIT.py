import sqlite3
def initDB(db_path):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создание таблицы countries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            userid INTEGER,
            countryname TEXT,
            government TEXT,
            ideology TEXT,
            currency TEXT,
            about TEXT,
            flagURL TEXT,
            extraSymbols TEXT,
            ownerdata TEXT,
            id TEXT,
            money INTEGER DEFAULT 0,
            population INTEGER DEFAULT 0,
            agreement INTEGER DEFAULT 0,
            area INTEGER DEFAULT 0,
            infrastructure INTEGER DEFAULT 0,
            medicine INTEGER DEFAULT 0,
            eudication INTEGER DEFAULT 0,
            attack INTEGER DEFAULT 0,
            armor INTEGER DEFAULT 0,
            fuel INTEGER DEFAULT 0,
            fuel_space INTEGER DEFAULT 0,
            fuel_star INTEGER DEFAULT 0,
            fuel_void INTEGER DEFAULT 0,
            transport INTEGER DEFAULT 0,
            tech_index INTEGER DEFAULT 0,
            tech TEXT,
            food INTEGER DEFAULT 0,
            materials INTEGER DEFAULT 0
        )
    ''')

    # Создание таблицы users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            userid INTEGER,
            about TEXT,
            age INTEGER,
            timezone INTEGER,
            color TEXT,
            karma INTEGER DEFAULT 0,
            luck INTEGER DEFAULT 0,
            permissions TEXT,
            money NUMERIC DEFAULT 0,
            money_bank NUMERIC DEFAULT 0
        )
    ''')

    # Создание таблицы system
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system (
            reports TEXT
        )
    ''')

    # Создание таблицы partners
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            serverid INTEGER,
            servername TEXT,
            ownerid INTEGER,
            link TEXT,
            text TEXT,
            color TEXT
        )
    ''')

    # Создание таблицы servers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            serverid INTEGER,
            muteroleid INTEGER,
            mutes TEXT,
            bumpcolor TEXT,
            bumptext TEXT,
            invitelink TEXT,
            ownerid INTEGER,
            apocalypseChannel INTEGER,
            apocalypseChannelHook TEXT,
            apocalypseLastSendDay INTEGER DEFAULT 0,
            isThread INTEGER DEFAULT 0,
            parentID INTEGER,
            autoPublish INTEGER DEFAULT 0
        )
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()