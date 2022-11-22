import pendulum
from exif import Image as ExifImage

from ImageManager import data as mod_db
from ImageManager.app import globals as mod_globals
from ImageManager.app import helper as mod_helper


def get_exif_data(path):
    exif_items = {}
    with open(str(path), 'rb') as img_file:
        image_exif_data = ExifImage(img_file)
        if image_exif_data.has_exif and hasattr(image_exif_data, 'datetime'):
            exif_items['exif_date'] = pendulum.parse(image_exif_data.datetime).format('YYYY-MM-DD HH:mm:ss')
        if image_exif_data.has_exif and \
                hasattr(image_exif_data, 'gps_longitude') and \
                hasattr(image_exif_data, 'gps_latitude') and \
                hasattr(image_exif_data, 'gps_altitude'):
            exif_location = _convert_cords(image_exif_data.gps_longitude,
                                           image_exif_data.gps_longitude_ref,
                                           image_exif_data.gps_latitude,
                                           image_exif_data.gps_latitude_ref,
                                           image_exif_data.gps_altitude,
                                           image_exif_data.gps_altitude_ref)
            for key in exif_location.keys():
                exif_items[key] = exif_location[key]
    return exif_items


def exif_date_file_date():
    mod_globals.statusbar.showMessage('Prüfe die Dateien, ob es ein abweichendes EXIF-Datum gibt!')
    mod_globals.progressbar.setValue(0)
    query = 'SELECT * FROM files WHERE exif_date is not null'
    results = mod_db.exec_return(query)
    over_all_count = len(results)
    for counter, row in enumerate(results, start=1):
        if row[6] is not None:
            mod_helper.calculate_percentages(over_all_count, counter)
            local_creation_date = pendulum.datetime(year=row[5].year, month=row[5].month,
                                                    day=row[5].day, hour=row[5].hour,
                                                    minute=row[5].minute, second=row[5].second)
            local_exif_date = pendulum.datetime(year=row[6].year, month=row[6].month,
                                                day=row[6].day, hour=row[6].hour,
                                                minute=row[6].minute, second=row[6].second)
            if local_creation_date.diff(local_exif_date).days > 0:
                query = f'UPDATE files SET creation_date = \'{row[6]}\' WHERE id = {row[0]}'
                mod_db.exec_no_return(query)

    mod_globals.statusbar.showMessage('Prüfung der Dateien auf das EXIF-Datum abgeschlossen.')


def _decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def _convert_cords(long_coords, long_ref, lat_coords, lat_ref, alt_coords, alt_ref):
    return {'long_coords': _decimal_coords(long_coords, long_ref),
            'long_ref': long_ref,
            'lat_coords': _decimal_coords(lat_coords, lat_ref),
            'lat_ref': lat_ref,
            'altitude': alt_coords,
            'altitude_ref': alt_ref.value}
