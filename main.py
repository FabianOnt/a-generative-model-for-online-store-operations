import sys
import logging

from config.gen_config import *
from config.db_config import DB_NAME

from db.connection import get_connection
from db.schema import create_database

from generation.model import StoreModel
from generation.query_creator import write_data
from generation.loader import load_schema, load_tables, load_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def generate_data():
    logging.info("Creating store model...")
    try:
        model = StoreModel(
            n_users = N_USERS,
            n_vendors = N_VENDORS,
            n_products = N_PRODUCTS,
            countries=COUNTIRES,
            categories=CATEGORIES,
            mean_price_category=MEAN_PRICE_CATEGORY,
            initial_sex_prob=INITIAL_SEX_PROB
        )
        logging.info("Store model created successfully.")
    except Exception as e:
        logging.error(f"Failed to create store model: {e}")
    
    logging.info(f"Generating {N_ORDERS} orders...")
    try:
        model.run(N_ORDERS)
        logging.info(f"{N_ORDERS} orders generated succesfully")
    except Exception as e:
        logging.error(f"Failed to generate orders: {e}")
    
    logging.info("Writting MySQL query files...")
    try:
        write_data(model)
        logging.info("MySQL query files wrote successfully.")
    except Exception as e:
        logging.error("Failed to write MySQL query files.")

def connect_to_MySQL():
    logging.info("Establishing connection with MySQL...")
    try:
        conn = get_connection()
        logging.info("Connection established successfully.")
    except Exception as e:
        logging.info(f"Failed to connect: {e}")
        return 0
    cursor = conn.cursor()
    return conn, cursor


def build_MySQL_db(conn, cursor):
    logging.info("Creating database...")
    try:
        create_database(cursor, DB_NAME)
        load_schema(cursor, conn)
        load_tables(cursor, conn)
        logging.info("Database created successfully.")
    except Exception as e:
        logging.error(f"Failed to create database: {e}")

    return conn, cursor

def analyze_store(conn, cursor):
    logging.info(f"Creating views from {DB_NAME} tables...")
    try:
        load_file("generation/create_views.sql", cursor, conn)
        logging.info("Views created successfully.")
    except Exception as e:
        logging.error(f"Failed to create views: {e}")

    cursor.close()
    conn.close()


def main():
    generate_data()
    conn, cursor = connect_to_MySQL()
    build_MySQL_db(conn, cursor)
    analyze_store(conn, cursor)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(1)