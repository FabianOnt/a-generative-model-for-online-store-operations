import logging

table_filenames = [
    "users.sql",
    "vendors.sql",
    "products.sql",
    "stock.sql",
    "orders.sql"
]

def load_file(path: str, cursor, conn):
    with open(path, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    for cmd in sql_commands.split(";"):
        cursor.execute(cmd)

    conn.commit()


def load_schema(cursor, conn):
    logging.info("\tLoading schema...")
    try:
        load_file("db/schema.sql", cursor, conn)
        logging.info("\tSchema loaded successfully.")
    except Exception as e:
        logging.error(f"\tError loading schema: {e}")

def load_tables(cursor, conn):
    global table_filenames

    for filename in table_filenames:
        logging.info(f"\tLoading file {filename}...")
        try:
            load_file(f"generation/data/{filename}", cursor, conn)
            logging.info("\tTable loaded successfully.")
        except Exception as e:
            logging.error(f"\tError loading file {filename}: {e}")
