from typing import Any

from dotenv import load_dotenv
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum

from .connector import Connector
from .utils import validate_select_table_name, validate_none_select_table_name

load_dotenv()

# Constants
DATABASE_WITHOUT_ORM_PYTHON_GENERIC_CRUD_COMPONENT_ID = 206
DATABASE_WITHOUT_ORM_PYTHON_GENERIC_CRUD_COMPONENT_NAME = 'circles_local_database_python\\generic_crud'
DEVELOPER_EMAIL = 'akiva.s@circ.zone'

# Logger setup
logger = Logger.create_logger(object={
    'component_id': DATABASE_WITHOUT_ORM_PYTHON_GENERIC_CRUD_COMPONENT_ID,
    'component_name': DATABASE_WITHOUT_ORM_PYTHON_GENERIC_CRUD_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
})

class GenericCRUD:
    """A class that provides generic CRUD functionality"""
    def __init__(self, schema_name: str, connection: Connector = None) -> None:
        """Initializes the GenericCRUD class. If connection is not provided, a new connection will be created."""
        self.schema_name = schema_name
        self.connection = connection or Connector.connect(schema_name=schema_name)
        self.cursor = self.connection.cursor()
        self.id_column_name = None

    def set_id_column_name(self, id_column_name: str) -> None:
        self.id_column_name = id_column_name

    def insert(self, table_name: str, json_data: dict) -> int:
        """Inserts a new row into the table and returns the id of the new row or -1 if an error occurred."""
        logger.start(object={"table_name": table_name, "json_data": json_data})
        try:
            validate_none_select_table_name(table_name)
            columns = ','.join(json_data.keys())
            values = ','.join(['%s' for _ in json_data])
            insert_query = f"INSERT INTO {self.schema_name}.{table_name} ({columns}) VALUES ({values})"
            self.cursor.execute(insert_query, tuple(json_data.values()))
            self.connection.commit()
            logger.end("Data inserted successfully.")
            return self.cursor.lastrowid()
        except Exception as e:
            logger.exception("Error inserting json_data", object=e)
            logger.end()
            raise
    # TODO: We should split this method to select (....where ...) and select( ...id_column_name, id_column_value ...) which uses the 1st one.
    # TODO: When using named parameters the id_column_name will have a default value of self.id_column_name
    # TODO: We should split into two select() methods one with where_clause and one with the two id_column fields.        

    def select(self, table_name: str, select_clause_value: str = "*", id_column_name: str = None, id_column_value: Any = None,
               where: str = None, limit: int = 100) -> list:
        """Selects data from the table and returns it as a list of tuples."""

        logger.start(object={"table_name": table_name, "select_clause_value": select_clause_value, "id_column_name": id_column_name,
                             "id_column_value": id_column_value, "where": where})
        try:
            validate_select_table_name(table_name)
            if id_column_name and id_column_value:
                where = f"{id_column_name}={id_column_value}"
            select_query = f"SELECT {select_clause_value} FROM {self.schema_name}.{table_name} " + (f"WHERE {where} " if where else "") + f"LIMIT {limit}"
            self.cursor.execute(select_query)
            result = self.cursor.fetchall()
            logger.end("Data selected successfully.", object={"result": str(result)})
            return result           
        except Exception as e:
            logger.exception("Error selecting json_data", object=e)
            logger.end()
            raise

    # TODO: We should split into two select() select_by_where() and select_by_id() methods one with the where clause and one with the two id_column fields.
    # TODO: id_column_name should have default value from self.id_column_name
    def select_one(self, table_name: str, select_clause_value: str = "*", id_column_name: str = None, id_column_value: Any = None,
                   where: str = None) -> tuple:
        """Selects data from the table and returns it as a tuple."""
        # select handles all the validation / logs
        logger.start("select_one")
        result = self.select(table_name, select_clause_value, id_column_name, id_column_value, where, limit=1)
        return result[0] if result else None

    def update(self, table_name: str, json_data: dict, id_column_name: str = None, id_column_value: Any = None,
               where: str = None) -> None:
        """Updates data in the table.
        If id_column_name and id_column_value are provided, the row with the given id_column_value will be updated.
        If where is provided, the rows that match the where clause will be updated."""
        logger.start(object={"table_name": table_name, "json_data": json_data, "id_column_name": id_column_name,
                             "id_column_value": id_column_value, "where": where})
        try:
            validate_none_select_table_name(table_name)
            set_values = ', '.join([f"{k}=%s" for k in json_data.keys()]) + ("," if json_data else "")
            if id_column_name and id_column_value:
                where = f"{id_column_name}={id_column_value}"
            if where:
                update_query = f"UPDATE {self.schema_name}.{table_name} SET {set_values} updated_timestamp=CURRENT_TIMESTAMP() WHERE {where}"
                self.cursor.execute(update_query, tuple(json_data.values()))
            else:
                message = "Update requires a 'where', or id_column_name and id_column_value."
                logger.error(message)
                logger.end()
                raise Exception(message)

            self.connection.commit()
            logger.end("Data updated successfully.")
        except Exception as e:
            logger.exception("Error updating json_data", object=e)
            logger.end()
            raise

    # TODO: Rename to delete_by_where and delte_by_id
    # TODO: As we don't need to send both id_column_value and where we should either use union or split to two methods
    def delete(self, table_name: str, id_column_name: str = None, id_column_value: Any = None,
               where: str = None) -> None:
        """Deletes data from the table.
        If id_column_name and id_column_value are provided, the row with the given id_column_value will be deleted.
        If a where clause is provided, the rows that match the where clause will be deleted."""
        logger.start(object={"table_name": table_name, "id_column_name": self.id_column_name,
                             "id_column_value": id_column_value, "where": where})
        try:
            self.update(table_name, {}, id_column_name, id_column_value, where)
            if id_column_name and id_column_name != None:
                update_query = f"UPDATE {self.schema_name}.{table_name} SET end_timestamp=CURRENT_TIMESTAMP() WHERE {id_column_name}={id_column_value}"
                self.cursor.execute(update_query)
                self.connection.commit()
            logger.end("Deleted successfully.")
        except Exception as e:
            logger.exception("Error while deleting", object=e)
            logger.end()
            raise

    def switch_db(self, new_database: str) -> None:
        """Switches the database to the given database name."""
        logger.start(object={"schema_name": new_database})
        self.connection.set_schema(new_database)
        self.schema_name = new_database
        logger.end("Schema set successfully.")

    def close(self) -> None:
        """Closes the connection to the database."""
        logger.start()
        self.connection.close()
        logger.end()


