import sqlite3


def is_record_inserted(cursor):
    query = 'SELECT COUNT(*) FROM metadata WHERE record_inserted = 1'
    cursor.execute(query)
    count = cursor.fetchone()[0]
    return count > 0


def mark_record_inserted(cursor):
    update_query = 'UPDATE metadata SET record_inserted = 1'
    cursor.execute(update_query)


conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

create_metadata_table_query = """
    CREATE TABLE IF NOT EXISTS metadata (
        record_inserted INTEGER DEFAULT 0
    )
"""
cursor.execute(create_metadata_table_query)

if not is_record_inserted(cursor):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL UNIQUE,
            title TEXT DEFAULT "",
            tags TEXT DEFAULT ",",
            desc TEXT DEFAULT "",
            frequency INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            last_used TIMESTAMP
        )
    """
    cursor.execute(create_table_query)

    insert_query = """
        INSERT INTO bookmarks (url, title, tags, desc, frequency, created_at, last_used)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """
    bookmark_data = (
        'https://example.com',
        'Example Website',
        'example, test',
        'An example website',
        1,
    )
    cursor.execute(insert_query, bookmark_data)

    mark_record_inserted(cursor)
    conn.commit()

conn.close()
