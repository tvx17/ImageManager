import locale
import os
from pathlib import Path

import pendulum

import checks as mod_checks
import database as mod_database
import exif_data as mod_exif_data
import globals as mod_globals
import helper as mod_helper

_files_count = 0


def _count_all_files():
    global _files_count
    _files_count = sum(len(files) for root, dirs, files in os.walk(mod_globals.path))


def find_files():
    global _files_count
    _count_all_files()
    locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')

    mod_globals.statusbar.showMessage(
        'Lese die Fotos ein! Insgesamt ' + locale.format_string("%d", _files_count, 1) + ' Dateien')
    mod_globals.session = pendulum.now().format('YYYY-MM-DD HH:mm:ss')
    _iterate(Path(mod_globals.path))
    mod_globals.statusbar.showMessage('Einlesen der Fotos abgeschlossen')
    mod_globals.progressbar.setValue(100)


def _check_file(file_item):
    file_data = {'file_name': file_item.stem,
                 'suffix': file_item.suffix.replace(".", ""),
                 'path': str(file_item.parent).replace("\\", "\\\\"),
                 'creation_date': _get_creation_date(file_item.stat().st_mtime),
                 'file_size': file_item.stat().st_size}

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

    mod_globals.files.append(file_data)


def _iterate(image_path):
    try:
        if image_path.is_dir():
            for item in image_path.iterdir():
                if item.is_dir():
                    _iterate(item)
                elif item.is_file():
                    _check_file(item)
                if len(mod_globals.files) == 200:
                    _write_to_db()
                    mod_globals.files = []
    except Exception as ex:
        print(f'In _iter {ex}')


def _get_creation_date(st_ctime):
    cdate = pendulum.from_timestamp(st_ctime)
    cdate_temp = cdate.date()
    now = pendulum.now().date()
    return cdate.format('YYYY-MM-DD HH:mm:ss') if cdate_temp != now else None


def _file_already_in_db(file_data):
    query = f'SELECT count(*) FROM files WHERE file_name = \'{file_data["file_name"]}\' AND suffix = \'{file_data["suffix"]}\' AND path = \'{file_data["path"]}\''
    results = mod_database.exec_return(query)
    for row in results:
        return int(row[0]) >= 1


def _write_to_db():
    global _files_count
    columns = {}

    for file in mod_globals.files:
        mod_globals.file_counter += 1
        mod_helper.calculate_percentages(_files_count, mod_globals.file_counter)
        if not _file_already_in_db(file):
            mod_globals.new_files += 1
            column_count = len(file.keys())
            if column_count not in columns.keys():
                columns[column_count] = _get_db_columns(file)
            query = f'{columns[column_count]}\'{mod_globals.session}\', '

            for key in file.keys():
                query += f'{_set_db_insert_value(file[key])}, '
            query = f'{query[:-2]});'
            mod_database.exec_no_return(query)


def _get_db_columns(dictionary):
    query = 'INSERT INTO files (session, '
    for key in dictionary.keys():
        query += f'{key}, '
    return f'{query[:-2]}) VALUES ('


def _set_db_insert_value(value):
    return f"'{value}'" if isinstance(value, (str, pendulum.DateTime)) else value
