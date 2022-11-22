import re
from pathlib import Path

import imagehash
import pendulum
from PIL import Image

from ImageManager import data as mod_db
from ImageManager.app import globals as mod_globals
from ImageManager.app import helper as mod_helper
from ImageManager.gui import globals as globals_gui


def clean_up():
    mod_helper.get_files('db')
    query = 'SELECT * FROM files WHERE suffix = \'db\''
    results = mod_db.execute(query=query, type=mod_db.RequestTypes.ReturnData)
    count = len(results)
    mod_globals.file_counter = 0
    mod_globals.files_count = count
    mod_helper.set_amount('files_count')
    for current_count, result in enumerate(results, start=1):
        mod_globals.file_counter += 1
        mod_helper.set_amount('current_scanned')

        mod_helper.calculate_percentages(count, current_count)
        # Path(result['path'].decode('utf-8'), f'{result["file_name"]}.{result["suffix"]}').unlink()
        query = f'DELETE FROM files WHERE id = {result[0]}'
        mod_db.execute(query, mod_db.RequestTypes.NoReturn)
    globals_gui.active_mdis['progress'].pgb_progress.setValue(100)


def check_hashes():
    query = 'SELECT * FROM files where suffix in (\'jpg\', \'JPG\', \'jpeg\', \'JPEG\') AND check_image_hash IS NULL'
    results = mod_db.execute(query, mod_db.RequestTypes.ReturnData)
    mod_globals.file_counter = 0
    cutoff = 5

    count = len(results)

    mod_globals.files_count = (count * count) - count
    mod_helper.set_amount('files_count')
    for counter, row in enumerate(results, start=1):
        mod_globals.file_counter += 1
        mod_helper.set_amount('current_scanned')
        mod_helper.calculate_percentages(count, counter)

        source_image_path = Path(row[4], f'{row[2]}.{row[3]}')

        source_hash = imagehash.average_hash(Image.open(str(source_image_path)))

        query = f'SELECT * FROM files where id != {row[0]} AND suffix in (\'jpg\', \'JPG\', \'jpeg\', \'JPEG\')'
        sub_results = mod_db.execute(query, mod_db.RequestTypes.ReturnData)
        sub_count = len(sub_results)

        for subcounter, sub_row in enumerate(sub_results, start=1):
            mod_globals.file_counter += 1
            mod_helper.set_amount('current_scanned')
            mod_helper.calculate_percentages(sub_count, subcounter, 2)
            check_image_path = Path(sub_row[4], f'{sub_row[2]}.{sub_row[3]}')
            check_hash = imagehash.average_hash(Image.open(str(check_image_path)))
            if source_hash - check_hash < cutoff:
                query = f'INSERT INTO doublets_mapping (source_id, destination_id, type) VALUES ({row[0]}, {sub_row[0]}, \'hash\')'
                mod_db.execute(query, mod_db.RequestTypes.ReturnData)
        query = f'UPDATE files SET check_image_hash = 1 WHERE id = {row[0]}'
        mod_db.execute(query, mod_db.RequestTypes.ReturnData)


def check_doublets_files():
    query = 'SELECT * FROM files WHERE check_file_size IS NULL'
    results = mod_db.execute(query)
    count = len(results)
    mod_globals.files_count = count
    mod_helper.set_amount('files_count')
    mod_globals.file_counter = 0
    for counter, row in enumerate(results, start=1):
        mod_globals.file_counter += 1
        mod_helper.set_amount('current_scanned')
        mod_helper.calculate_percentages(count, counter)

        query = f'SELECT * FROM files WHERE file_size = \'{row[15]}\' AND id != {row[0]}'
        sub_results = mod_db.execute(query)
        if len(sub_results) != 0:
            for sub_row in sub_results:
                query = f'INSERT INTO doublets_mapping (source_id, destination_id, type) VALUES ({row[0]}, {sub_row[0]}, \'file_size\')'
                mod_db.execute(query, mod_db.RequestTypes.NoReturn)
        query = f'UPDATE files SET check_file_size = 1 WHERE id = {row[0]}'
        mod_db.execute(query, mod_db.RequestTypes.NoReturn)

    globals_gui.active_mdis['progress'].pgb_progress.setValue(0)
    globals_gui.active_mdis['progress'].pgb_progress_ii.setValue(0)
    query = 'SELECT * FROM files WHERE check_file_name IS NULL'
    results = mod_db.execute(query)
    count = len(results)
    mod_globals.files_count = count
    mod_helper.set_amount('files_count')
    mod_globals.file_counter = 0
    for counter, row in enumerate(results, start=1):
        mod_globals.file_counter += 1
        mod_helper.set_amount('current_scanned')
        mod_helper.calculate_percentages(count, counter)
        query = f'SELECT * FROM files WHERE file_name = \'{row[2]}\' AND id != {row[0]}'
        sub_results = mod_db.execute(query)
        if len(sub_results) != 0:
            for sub_row in sub_results:
                query = f'INSERT INTO doublets_mapping (source_id, destination_id, type) VALUES ({row[0]}, {sub_row[0]}, \'file_name\')'
                mod_db.execute(query, mod_db.RequestTypes.NoReturn)
        query = f'UPDATE files SET check_file_name = 1 WHERE id = {row[0]}'
        mod_db.execute(query, mod_db.RequestTypes.NoReturn)
        # --------------------------------------------------------------------------------------------------------------
    globals_gui.active_mdis['progress'].pgb_progress.setValue(100)
    globals_gui.active_mdis['progress'].pgb_progress_ii.setValue(100)


def check_filename(filename):
    filename = re.sub('(IMG|PANO)[_-]', '', filename)
    filename = re.sub('[_-][a-zA-Z].*', '', filename)

    if re.match('[1-2][0-9][0-2][0-9][0-1][0-9][0-1][0-9]$', filename) is not None:
        return pendulum.date(year=int(filename[:4]), month=int(filename[4:6]), day=int(filename[6:8]))
    if re.match('[1-2][0-9][0-2][0-9][0-1][0-9][0-1][0-9][_-][0-2][0-9][0-5][0-9][0-5][0-9]', filename) is not None:
        return pendulum.datetime(year=int(filename[:4]), month=int(filename[4:6]), day=int(filename[6:8]),
                                 hour=int(filename[9:11]),
                                 minute=int(filename[11:13]), second=int(filename[13:15]))

    return None
