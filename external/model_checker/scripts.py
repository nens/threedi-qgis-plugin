import click

from .model_checks import ThreediModelChecker
from .threedi_database import ThreediDatabase


@click.command()
@click.option('-d', '--database', help='database name to connect to')
@click.option('-h', '--host', help='database server host')
@click.option('-p', '--port', default=5432, help='database server port')
@click.option('-u', '--username', help='database username')
@click.option('-W', '--password', prompt=True, hide_input=True,
              confirmation_prompt=True,
              help='force password prompt (should happen automatically)')
def check_postgis_model(database, host, port, username, password):
    """Parse a postgis threedi-model and check its validity"""
    postgis_settings = {
        'host': host,
        'port': port,
        'database': database,
        'username': username,
        'password': password
    }
    db = ThreediDatabase(
        connection_settings=postgis_settings,
        db_type='postgres',
        echo=False
    )
    mc = ThreediModelChecker(db)
    print('abc')
    mc.parse_model()


@click.command()
@click.option('-s', '--sqlite', type=click.Path(exists=True, readable=True),
              help='sqlite file')
def check_sqlite_model(sqlite):
    """Parse a sqlite threedi-model and check its validity"""
    sqlite_settings =  {
        'db_path': sqlite,
        'db_file': sqlite
    }
    db = ThreediDatabase(
        connection_settings=sqlite_settings,
        db_type='spatialite',
        echo=False
    )
    mc = ThreediModelChecker(db)
    mc.parse_model()


if __name__ == '__main__':
    check_postgis_model()
