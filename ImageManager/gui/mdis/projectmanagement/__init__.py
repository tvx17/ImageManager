import os
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QFileDialog

from ImageManager.gui import globals as gui_globals
from ImageManager import data as mod_data


def setup():
	path = Path(os.getcwd(), 'gui', 'mdis', 'projectmanagement', 'mdi.ui')
	gui_globals.active_mdis['pm'] = uic.loadUi(str(path))
	_connect_actions()

	project_settings_fill_chooser()

	gui_globals.main_window.mdi_area.addSubWindow(gui_globals.active_mdis['pm'])
	gui_globals.active_mdis['pm'].show()


def _connect_actions():
	gui_globals.active_mdis['pm'].btn_new_project.clicked.connect(lambda: _actions_router('new_project'))
	gui_globals.active_mdis['pm'].btn_save.clicked.connect(lambda: _actions_router('save_project'))
	gui_globals.active_mdis['pm'].cb_project_selection.currentIndexChanged.connect(lambda: _actions_router('load_project_data', 'pm', 'cb_project_selection', ['le_project_name', 'le_scan_path']))
	# gui_globals.active_mdis['pm'].cb_project_selection.currentIndexChanged.connect(
	# 		lambda: _load_project_data('pm', 'cb_project_selection', ['le_project_name', 'le_scan_path']))
	gui_globals.active_mdis['pm'].btn_scan_path.clicked.connect(lambda: _actions_router('get_scan_path','projects', 'le_scan_path'))


# gui_globals.active_mdis['pm'].btn_new_project.btn_delete_project()


def _appearance_settings():
	gui_globals.active_mdis['pm'].setMaximumSize(591, 187)
	gui_globals.active_mdis['pm'].setFixedSize(591, 178)


def _actions_router(action, *args):
	try:
		func = globals()[f'_{action}']
		func(args)
	except Exception:
		if action == '':
			pass
# ---------------------- Helper

def _load_project_data(dialog, source_element, target_elements):
	element_data = getattr(gui_globals.active_mdis[dialog], source_element).currentData()
	if element_data is not None:
		results = mod_data.execute(f'SELECT name, path FROM projects WHERE id = {element_data}')
		if isinstance(target_elements, list):
			if len(results[0]) == len(target_elements):
				for index, target_element in enumerate(target_elements):
					getattr(gui_globals.active_mdis[dialog], target_element).setText(results[0][index])
		else:
			getattr(gui_globals.active_mdis[dialog], target_elements).setText(results[0][0])


def project_settings_fill_chooser():
	projects = mod_data.execute("SELECT * FROM projects WHERE active = 1", mod_data.RequestTypes.ReturnData)
	with gui_globals.active_mdis['pm'].cb_project_selection as cb_element:
		cb_element.clear()
		cb_element.insertItem(0, 'Bitte wählen')
		cb_element.setItemData(0, 0)
		for index, project in enumerate(projects):
			cb_element.insertItem(index + 1, project[1])
			cb_element.setItemData(index + 1, project[0])


# ---------------------- Actions
def _new_project():
	mod_data.execute(f'INSERT INTO projects (name, path, active) VALUES (\'New Project\', \'not set\', 1)', mod_data.RequestTypes.NoReturn)
	project_settings_fill_chooser()


def _get_scan_path(target_mdi, target_element):
	dlg = QFileDialog()
	dlg.setFileMode(QFileDialog.FileMode.Directory)

	if dlg.exec():
		getattr(gui_globals.active_mdis[target_mdi], target_element).setText(dlg.selectedFiles()[0])


if __name__ == '__main__':
	pass
