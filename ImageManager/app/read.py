import locale
import os
from pathlib import Path

import pendulum

from ImageManager.app import checks as mod_checks
from ImageManager.app import globals as globals_app
from ImageManager.app import exif_data as mod_exif_data
from ImageManager.app import globals as globals_app
from ImageManager.app import helper as mod_helper
from ImageManager import data as mod_data
from ImageManager.gui import globals as globals_gui


def _count_all_files():
    globals_app.files_count = sum(len(files) for root, dirs, files in os.walk(globals_app.current_project['path']))
    try:
        formated_string = locale.format_string("%d", globals_app.files_count, 1)
        globals_gui.active_mdis['progress'].le_files_count.setText(formated_string)
    except Exception as ex:
        print(ex)


def __set_current_files_amount(which):
    if which == 'new':
        formated_string = locale.format_string("%d", globals_app.new_files, 1)
        globals_gui.active_mdis['progress'].le_new_files.setText(formated_string)
    if which == 'scanned':
        formated_string = locale.format_string("%d", globals_app.file_counter, 1)
        globals_gui.active_mdis['progress'].le_current_files_count.setText(formated_string)


def find_files():
    try:
        locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
        _count_all_files()

        globals_app.session = pendulum.now().format('YYYY-MM-DD HH:mm:ss')
        _iterate(Path(globals_app.current_project['path']))

        globals_gui.active_mdis['progress'].pgb_progress.setValue(100)
    except Exception as ex:
        print(ex)


def _check_file(file_item):
    file_data = {
            'file_name':     file_item.stem,
            'suffix':        file_item.suffix.replace(".", ""),
            'path':          str(file_item.parent).replace("\\", "\\\\"),
            'creation_date': _get_creation_date(file_item.stat().st_mtime),
            'file_size':     file_item.stat().st_size
            }

    if file_item.suffix.lower() in ('.jpg', '.jpeg'):
        exif_data = mod_exif_data.get_exif_data(file_item)
        dt = None
        if len(exif_data) > 0:
            for key in exif_data.keys():
                file_data[key] = exif_data[key]
            if not hasattr(exif_data, 'exif_date'):
                dt = mod_checks.check_filename(file_data['file_name'])
        if len(exif_data) == 0:
            dt = mod_checks.check_filename(file_data['file_name'])
        if dt is not None:
            file_data['exif_date'] = dt

    globals_app.files.append(file_data)


def _iterate(image_path):
    try:
        if image_path.is_dir():
            for item in image_path.iterdir():
                if item.is_dir():
                    _iterate(item)
                elif item.is_file():
                    _check_file(item)
                if len(globals_app.files) == 200:
                    _write_to_db()
                    globals_app.files = []
    except Exception as ex:
        print(f'In _iter {ex}')


def _get_creation_date(st_ctime):
    cdate = pendulum.from_timestamp(st_ctime)
    cdate_temp = cdate.date()
    now = pendulum.now().date()
    return cdate.format('YYYY-MM-DD HH:mm:ss') if cdate_temp != now else None


def _file_already_in_db(file_data):
    query = f'SELECT count(*) FROM files WHERE file_name = \'{file_data["file_name"]}\' AND suffix = \'{file_data["suffix"]}\' AND path = \'{file_data["path"]}\''
    results = mod_data.execute(query, mod_data.RequestTypes.ReturnData)
    return False if results[0][0] == 0 else True


def _write_to_db():
    columns = {}
    try:
        for file in globals_app.files:
            globals_app.file_counter += 1
            mod_helper.set_amount('current_scanned')
            mod_helper.calculate_percentages(globals_app.files_count, globals_app.file_counter)
            if not _file_already_in_db(file):
                globals_app.new_files += 1
                mod_helper.set_amount('current_new')
                column_count = len(file.keys())
                if column_count not in columns.keys():
                    columns[column_count] = _get_db_columns(file)
                query = f'{columns[column_count]}\'{globals_app.session}\', '

                for key in file.keys():
                    query += f'{_set_db_insert_value(file[key])}, '
                query = f'{query[:-2]});'
                mod_data.execute(query, mod_data.RequestTypes.NoReturn)
    except Exception as ex:
        print(ex)


def _get_db_columns(dictionary):
    query = r'INSERT INTO files (session, '
    for key in dictionary.keys():
        query += f'{key}, '
    return f'{query[:-2]}) VALUES ('


def _set_db_insert_value(value):
    return f"'{value}'" if isinstance(value, (str, pendulum.DateTime)) else value
