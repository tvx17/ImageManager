import locale
import os

from ImageManager.app import globals as globals_app
from ImageManager.gui import globals as globals_gui
from ImageManager import data as mod_data


def get_files(where):
	if where == 'os':
		globals_app.files_count = sum(len(files) for root, dirs, files in os.walk(globals_app.current_project['path']))
	if where == 'db':
		query = 'SELECT COUNT(*) FROM files'
		results = mod_data.execute(query, mod_data.RequestTypes.ReturnData)
		globals_app.files_count = results[0][0]


def set_amount(where):
	try:
		if where == 'files_count':
			formated_string = locale.format_string("%d", globals_app.files_count, 1)
			globals_gui.active_mdis['progress'].le_files_count.setText(formated_string)
		if where == 'current_new':
			formated_string = locale.format_string("%d", globals_app.new_files, 1)
			globals_gui.active_mdis['progress'].le_new_files.setText(formated_string)
		if where == 'current_scanned':
			formated_string = locale.format_string("%d", globals_app.file_counter, 1)
			globals_gui.active_mdis['progress'].le_current_files_count.setText(formated_string)
	except Exception as ex:
		print(ex)


def calculate_percentages(over_all, current, which = 1):
	percentage = round((current * 100) / over_all, 0)
	if which == 1:
		globals_gui.active_mdis['progress'].pgb_progress.setValue(int(percentage))
	if which == 2:
		globals_gui.active_mdis['progress'].pgb_progress_ii.setValue(int(percentage))
