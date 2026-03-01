import logging
from generation.model import StoreModel

def write_sql_to_file(query: str, filename: str) -> None:
    """
    Writes a given MySQL query string into a .sql file.
    
    Parameters
    ----------
    query : str
        A MySQL query string.
    filename : str
        Name of the output .sql file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            t = query.replace("),","),\n")
            top, bottom = t.split("VALUES ")
            text = top + "VALUES\n" + bottom
            f.write(text)
        logging.info(f"\tQuery written into {filename}")
    except Exception as e:
        logging.error(f"\tError writing to file: {e}")

def write_data(model: StoreModel):
    write_sql_to_file(model.get_query_users(), "generation/data/users.sql")
    write_sql_to_file(model.get_query_vendors(), "generation/data/vendors.sql")
    write_sql_to_file(model.get_query_products(), "generation/data/products.sql")
    write_sql_to_file(model.get_query_orders(), "generation/data/orders.sql")
    write_sql_to_file(model.get_query_stock(update=True), "generation/data/stock.sql")
