# # Conexión a Base de Datos y manejo de datos
# # Creado por: Totem Bear
# # Fecha: 23-Ago-2023

# from sqlalchemy import create_engine, Table, MetaData, exc, and_, text
# from sqlalchemy.orm import sessionmaker
# from utils import privproperties, logger
# import sys

# sys.path.append("..")


# # Configure database connection
# # POSTGRESQL
# # SQLALCHEMY_DATABASE_URL = utils.dbEngine + "://" + utils.dbUser + ":" + utils.dbPass + utils.dbHost + utils.dbName
# # engine = create_engine(SQLALCHEMY_DATABASE_URL)
# # Session = sessionmaker(bind=engine)

# # # Reflect the tables from the existing database
# # metadata = MetaData()
# # metadata.reflect(engine)

# # Here is used engine.connect() instead of Session() because the latter does not support returning values.
# # engine.connect() context manager automatically commits any changes when the context is exited, unless an
# # exception has been raised. In case of exceptions, the context manager's __exit__() method will also take
# # care of rolling back the transaction. That's why there is no explicit rollback() in the except clause.


# def get_table_object(table_name: str):
#     """Get a Table object for the specified table.

#     Args:
#         table_name (str): The name of the table.

#     Returns:
#         Table: A SQLAlchemy Table object.
#     """
#     try:
#         return Table(table_name, metadata, autoload_with=engine)
#     except exc.NoSuchTableError:
#         msg = f"TotemDB - datamanager - Error: The table '{table_name}' does not exist."
#         print(msg)
#         msj = "Controlador-Inicio - Validar Usuario - IMEI y número de teléfono de usuario válidos - token de acceso generado"
#         tbu.logger.printLog(gd.log_file, msj, "info")
#         utils.printLog("events", msg, "error", False)
#         return None


# def create_record(table_name: str, data):
#     """Create a new record in the specified table.

#     Args:
#         table_name (str): The name of the table.
#         data (dict): A dictionary containing the column names and values for the new record.

#     Returns:
#         dict: The new record.
#     """
#     table = get_table_object(table_name)
#     if table is not None:
#         try:
#             ins = table.insert().values(**data).returning(table)
#             with engine.connect() as conn:
#                 result = conn.execute(ins)
#                 record = result.fetchone()
#                 return dict(record)
#         except exc.DBAPIError as e:
#             msg = f"TotemDB Error: An error occurred while creating a record on {table_name}: {e}"
#             print(msg)
#             utils.printLog("events", msg, "error", False)
#             return None
#     else:
#         return None


# # def update_record(table_name: str, record_id, data):
# #     """Update an existing record in the specified table.

# #     Args:
# #         table_name (str): The name of the table.
# #         record_id (int): The ID of the record to update.
# #         data (dict): A dictionary containing the column names and updated values for the record.

# #     Returns:
# #         dict: The updated record.
# #     """
# #     table = get_table_object(table_name)
# #     if table is not None:
# #         try:
# #             upd = table.update().where(table.c.id == record_id).values(**data).returning(table)
# #             with engine.connect() as conn:
# #                 result = conn.execute(upd)
# #                 record = result.fetchone()
# #                 return dict(record)
# #         except exc.DBAPIError as e:
# #             msg = f"TotemDB Error: An error occurred while updating a record on {table_name}: {e}"
# #             print(msg)
# #             utils.printLog("events", msg, "error", False)
# #             return None
# #     else:
# #         return None


# # def read_records(table_name: str):
# #     """Read all records from the specified table.

# #     Args:
# #         table_name (str): The name of the table.

# #     Returns:
# #         list: A list of dictionaries representing the retrieved records.
# #     """
# #     table = get_table_object(table_name)
# #     if table is not None:
# #         try:
# #             sel = table.select()
# #             with engine.connect() as conn:
# #                 result = conn.execute(sel)
# #                 records = [dict(row) for row in result.fetchall()]
# #                 return records
# #         except exc.DBAPIError as e:
# #             msg = f"TotemDB Error: An error occurred while reading records on {table_name}: {e}"
# #             print(msg)
# #             utils.printLog("events", msg, "error", False)
# #             return None
# #     else:
# #         return None


# # def read_all_records_by_fields(table_name: str, fields: dict):
# #     """Read all records from the specified table based on a field and its value.

# #     Args:
# #         table_name (str): The name of the table.
# #         fields (dict): A dictionary containing the fields and their corresponding values to search.

# #     Returns:
# #         list: A list of dictionaries representing the retrieved records.
# #     """
# #     table = get_table_object(table_name)
# #     if table is not None:
# #         try:
# #             conditions = [table.c[field] == value for field, value in fields.items()]
# #             sel = table.select().where(and_(*conditions))
# #             with engine.connect() as conn:
# #                 result = conn.execute(sel)
# #                 records = [dict(row) for row in result.fetchall()]
# #                 return records
# #         except exc.DBAPIError as e:
# #             msg = f"TotemDB Error: An error occurred while reading records on {table_name}: {e}"
# #             print(msg)
# #             utils.printLog("events", msg, "error", False)
# #             return None
# #     else:
# #         return None


# # def read_record_by_fields(table_name: str, fields: dict):
# #     """
# #     Read a record from the specified table based on multiple fields and their values.

# #     Args:
# #         table_name (str): The name of the table.
# #         fields (dict): A dictionary containing the fields and their corresponding values to search.

# #     Returns:
# #         dict: A dictionary representing the retrieved record, or None if no matching record is found.
# #     """
# #     table = get_table_object(table_name)
# #     if table is not None:
# #         try:
# #             conditions = [table.c[field] == value for field, value in fields.items()]
# #             sel = table.select().where(and_(*conditions))
# #             with engine.connect() as conn:
# #                 result = conn.execute(sel)
# #                 record = result.fetchone()
# #                 return dict(record) if record else None
# #         except exc.DBAPIError as e:
# #             msg = f"TotemDB Error: An error occurred while reading a record on {table_name}: {e}"
# #             print(msg)
# #             utils.printLog("events", msg, "error", False)
# #             return None
# #     else:
# #         return None


# # def delete_record(table_name: str, field: str, value):
# #     """Delete a record from the specified table by its ID.

# #     Args:
# #         table_name (str): The name of the table.
# #         field (str): The name of the field to search.
# #         value: The value to match in the specified field.

# #     Returns:
# #         dict: The deleted record, or None if the record was not found.
# #     """
# #     table = get_table_object(table_name)
# #     if table is not None:
# #         try:
# #             delete = table.delete().where(table.c[field] == value).returning(table)
# #             with engine.connect() as conn:
# #                 result = conn.execute(delete)
# #                 record = result.fetchone()
# #                 return dict(record) if record else None
# #         except exc.DBAPIError as e:
# #             msg = f"TotemDB Error: An error occurred while deleting a record from {table_name}: {e}"
# #             print(msg)
# #             utils.printLog("events", msg, "error", False)
# #             return None
# #     else:
# #         return None


# def execute_stored_procedure(procedure_name: str, args: tuple):
#     """Execute a stored procedure with the given arguments.

#     Args:
#         procedure_name (str): The name of the stored procedure.
#         args (tuple): The arguments to pass to the stored procedure.

#     Returns:
#         dict: The result returned by the stored procedure, or None if an error occurs.

#     Raises:
#         ValueError: For invalid store procedure name.
#     """
    
#     # Input validation to prevent malicious handling
#     if not procedure_name.isidentifier():
#         raise ValueError("TotemDB Error: Invalid stored procedure name.")

#     try:
#         # Create a connection to the database
#         with engine.connect() as conn:
#             # Start a transaction
#             transaction = conn.begin()            
#             # Create a SQL expression text
#             stmt = text(f"CALL {procedure_name}({','.join([':%s' % i for i in range(len(args))])})")
#             # Bind parameters and execute the stored procedure
#             result = conn.execute(stmt, args)
#             # Get the row of the result
#             record = result.fetchone()
#             # Commit the transaction
#             transaction.commit()
#             # Close the connection
#             conn.close()
#             return dict(record) if record else None
#     except exc.DBAPIError as e:
#         msg = f"TotemDB Error: An error occurred while executing a stored procedure {procedure_name}: {e}"
#         print(msg)
#         utils.printLog("events", msg, "error", False)
#         return e
