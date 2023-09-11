# create_user_and_db.py
""" Create User and database """
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_user_and_grant_privileges(config) -> None:
    """
    Creates a PostgreSQL user role and grants privileges.

    Args:
        config (Callable):
            A callable that takes a configuration key as an argument
            and returns the corresponding configuration value.

    This function reads the DB_USER and DB_PASSWORD from the configuration file
    and uses DB_SUPERUSER credentials to
    establish a connection to the PostgreSQL server.

    If the user role does not exist,
    it creates the user role with the provided credentials.

    Raises:
        psycopg2.Error:
            If there is an error connecting to PostgreSQL or
            executing queries.
    """
    username = config("DB_USER")
    password = config("DB_PASSWORD")
    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            dbname=config("DEFAULT_DB_NAME"),
            user=config("DB_SUPERUSER"),
            password=config("DB_SUPERUSER_PASSWORD"),
            host=config("DB_HOST"),
            port=config("DB_PORT"),
        )

        # Set isolation level to autocommit
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Create a cursor to execute SQL queries
        with connection.cursor() as cursor:
            # Check if the user role exists
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", [username])
            user_exists = bool(cursor.fetchone())

            if not user_exists:
                # Create the user role if it doesn't exist
                cursor.execute(
                    f"CREATE ROLE {username} WITH CREATEDB LOGIN ENCRYPTED PASSWORD %s;",
                    [password],
                )
                print("User role created successfully.")
            else:
                print("User role already exists. Skipping creation.")

    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL:", error)

    finally:
        # Close the connection
        if "connection" in locals():
            connection.close()


def create_database(config) -> None:
    """
    Create a PostgreSQL database if it doesn't exist.

    Args:
        config (Callable):
            A callable that takes a configuration key as an argument
            and returns the corresponding configuration value.

    This function establishes a connection to the
    PostgreSQL server using DB_SUPERUSER credentials.
    It checks if the database exists,
    and if not, it creates the database with the provided owner.

    Raises:
        psycopg2.Error:
            If there is an error connecting to
            PostgreSQL or executing queries.
    """
    db_name = config("DB_NAME")
    db_owner = config("DB_USER")

    try:
        # Establish a connection to the PostgreSQL server
        connection = psycopg2.connect(
            dbname=config("DEFAULT_DB_NAME"),
            user=config("DB_SUPERUSER"),
            password=config("DB_SUPERUSER_PASSWORD"),
            host=config("DB_HOST"),
            port=config("DB_PORT"),
        )

        # Set isolation level to autocommit
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Create a cursor to execute SQL queries
        with connection.cursor() as cursor:
            # Check if the database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", [db_name])
            db_exists = bool(cursor.fetchone())

            if not db_exists:
                # Create the database if it doesn't exist
                cursor.execute(
                    f"CREATE DATABASE {db_name} WITH OWNER = {db_owner} "
                    f"ENCODING = 'UTF8' CONNECTION LIMIT = -1 IS_TEMPLATE = False;"
                )
                print(f'Database "{db_name}" created successfully.')
            else:
                print(f'Database "{db_name}" already exists. Skipping creation.')

    except psycopg2.Error as error:
        print(f"Error creating database: {error}")

    finally:
        # Close the connection
        if "connection" in locals():
            connection.close()
