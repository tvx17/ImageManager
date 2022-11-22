import os
from pathlib import Path
from ImageManager.data import globals as data_globals
from ImageManager.app import globals as app_globals
from ImageManager import data as mod_data


def check_first_run():
    mod_data.database_file()
    # if not data_globals.db_file.exists():
    #     mod_data.new_database()
    _check_projects()


def _check_projects():
    results = mod_data.execute("SELECT * FROM projects", mod_data.RequestTypes.ReturnData)
    if results is None or len(results) == 0:
        mod_data.execute(f"INSERT INTO projects (name, active, path) VALUES ('first_project', 1, '{str(Path.home())}')",
                         mod_data.RequestTypes.NoReturn)

    if results is None:
        raise ('There was an error getting the projects')
