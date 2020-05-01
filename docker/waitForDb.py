import psycopg2
from time import sleep
import argparse

from DeviceManager.conf import CONFIG


def wait_for_db(db_args):
    """ blocks execution until database is ready """

    print('Waiting for database to become available...')
    retries = db_args.retries
    while retries > 0:
        try:
            connection = psycopg2.connect(user=CONFIG.dbuser, password=CONFIG.dbpass,
                                          host=CONFIG.dbhost)
            if CONFIG.create_db:
                connection.autocommit = True
                cursor = connection.cursor()
                cursor.execute(
                    "select true from pg_database where datname = '%s';" % CONFIG.dbname)
                if len(cursor.fetchall()) == 0:
                    print("will attempt to create database")
                    cursor.execute("CREATE database %s;" % CONFIG.dbname)
            print("Ready to go")
            exit(0)
        except psycopg2.Error as e:
            print("Database connection error | {}".format(e.pgerror))
        except Exception as e:
            print("Error | {}".format(e))

        retries -= 1
        print('Will try again in ' + str(db_args.wait))
        sleep(db_args.wait)

    print('Max retries reached, failed to connect to Postgres')
    exit(1)


if __name__ == '__main__':
    desc = """Waits for database"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-w', '--wait', help="", default=5, type=int)
    parser.add_argument('-r', '--retries', help="", default=20, type=int)
    args = parser.parse_args()
    wait_for_db(args)
