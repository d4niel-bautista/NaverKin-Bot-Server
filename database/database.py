from sqlalchemy import create_engine, MetaData, Table, select, update, insert, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()
import os
from utils import convert_date

USER = os.getenv("DB_USER")
PASS = os.getenv("DB_PASS")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
NAME = os.getenv("DB_NAME")
DATABASE_URL = f"mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_conn():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def dynamic_query(query_dict, engine, session = next(get_db_conn())):
    # Extract values from the query_dict
    tables = query_dict.get("table", [])
    columns = ",".join(query_dict.get("column"))
    params = query_dict.get("params", {})

    # Initialize a MetaData object to reflect tables
    metadata = MetaData()

    # Create SQLAlchemy Table objects for the specified tables
    table_objects = [Table(table, metadata, autoload_with=engine) for table in tables]

    # Build the query
    query = select(columns)

    # Add FROM clause to the query based on the specified tables
    if table_objects:
        query = query.select_from(table_objects[0])
        for table_object in table_objects[1:]:
            query = query.outerjoin(table_object)

    # Build a list of filter conditions based on the specified parameters
    filter_conditions = []
    for param_column, param_value in params.items():
        if "and " in param_column:
            param_column = param_column.replace("and ", "")
            filter_conditions.append(and_(*[getattr(table_objects[0].c, param_column) == value for value in param_value.split(",")]))
        elif "or " in param_column:
            param_column = param_column.replace("or ", "")
            filter_conditions.append(or_(*[getattr(table_objects[0].c, param_column) == value for value in param_value.split(",")]))
        else:
            if "." in param_column:
                table_name, column_name = param_column.split('.')
                table_alias = next((t for t in table_objects if t.name == table_name), None)
                if table_alias:
                    filter_conditions.append(getattr(table_alias.c, column_name) == param_value)

    # Combine filter conditions using AND by default
    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    result = convert_date(dict(session.execute(query).mappings().fetchone()))

    session.commit()
    session.close()
    return result

async def dynamic_update(query_dict, engine, session = next(get_db_conn())):
    # Extract values from the query_dict
    table_name = query_dict.get("table")
    columns = query_dict.get("column", {})
    params = query_dict.get("params", {})

    # Initialize a MetaData object to reflect tables
    metadata = MetaData()

    # Create a SQLAlchemy Table object for the specified table
    table = Table(table_name, metadata, autoload_with=engine)

    # Build the update statement
    update_stmt = update(table)

    # Set the columns to update
    for column_name, new_value in columns.items():
        update_stmt = update_stmt.values({column_name: new_value})

    # Build a list of filter conditions based on the specified parameters
    filter_conditions = []
    for param_column, param_value in params.items():
        print(param_column, param_value)
        if "and " in param_column:
            param_column = param_column.replace("and ", "")
            filter_conditions.append(getattr(table.c, param_column) == param_value)
        elif "or " in param_column:
            param_column = param_column.replace("or ", "")
            filter_conditions.append(getattr(table.c, param_column) == param_value)
        else:
            filter_conditions.append(getattr(table.c, param_column) == param_value)

    # Combine filter conditions using AND by default
    if filter_conditions:
        update_stmt = update_stmt.where(and_(*filter_conditions))

    session.execute(update_stmt)

    session.commit()
    session.close()
    return "UPDATE DONE"

async def dynamic_insert(query_dict, engine, session = next(get_db_conn())):
    # Extract values from the query_dict
    table_name = query_dict.get("table")
    columns = query_dict.get("column", [])
    values = query_dict.get("values", [])
    params = query_dict.get("params", {})

    # Initialize a MetaData object to reflect tables
    metadata = MetaData()

    # Create a SQLAlchemy Table object for the specified table
    table = Table(table_name, metadata, autoload_with=engine)

    # Build the insert statement
    insert_stmt = insert(table)

    # Map columns to values
    if len(columns) != len(values):
        raise ValueError("Columns and values lists must have the same length")

    values_dict = {}
    for column, value in zip(columns, values):
        values_dict[column] = value

    # Set the values to insert
    insert_stmt = insert_stmt.values(values_dict)

    # Build a list of filter conditions based on the specified parameters
    filter_conditions = []

    for param_column, param_value in params.items():
        if "or " in param_column:
            param_column = param_column.replace("or ", "")
            filter_conditions.append(getattr(table.c, param_column) == param_value)
        elif "and " in param_column:
            param_column = param_column.replace("and ", "")
            filter_conditions.append(getattr(table.c, param_column) == param_value)
        else:
            filter_conditions.append(getattr(table.c, param_column) == param_value)

    # Combine filter conditions using AND by default, or OR if specified
    if filter_conditions:
        or_conditions = []
        and_conditions = []
        for condition in filter_conditions:
            if isinstance(condition, or_):
                or_conditions.extend(condition.clauses)
            elif isinstance(condition, and_):
                and_conditions.extend(condition.clauses)
            else:
                and_conditions.append(condition)

        final_conditions = []

        if or_conditions:
            final_conditions.append(or_(*or_conditions))
        if and_conditions:
            final_conditions.append(and_(*and_conditions))

        if final_conditions:
            insert_stmt = insert_stmt.where(and_(*final_conditions))

    session.execute(insert_stmt)

    session.commit()
    session.close()
    return "INSERT DONE"