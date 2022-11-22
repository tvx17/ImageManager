import os
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (QDockWidget, QTreeView, QPushButton,
                             QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, )
from PyQt6.QtWidgets import QLabel

from ImageManager import data as mod_data

from ImageManager.gui import globals as gui_globals

_toolbar = None
_mdis = {}
_current_project_id = 0
_current_project = {'id': 0, 'name': None, 'path': None}
_sb_project_name = None


def setup():
	connect_actions()
	_get_projects()
	_statusbar()


def _statusbar():
	global _sb_project_name
	_sb_project_name = QLabel()
	_sb_project_name.setText('Kein Projekt gewählt')
	gui_globals.main_window.sb_statusbar.addPermanentWidget(_sb_project_name)


def _get_projects():
	projects_menu = gui_globals.main_window.submn_app_projects
	projects = mod_data.execute("SELECT * FROM projects", mod_data.RequestTypes.ReturnData)
	for project in projects:
		new_action = QAction(project[1], gui_globals.main_window)
		new_action.triggered.connect(lambda: project_router(project[0]))
		projects_menu.addAction(new_action)


def project_router(id):
	global _current_project
	projects = mod_data.execute(f'SELECT id, name, path FROM projects WHERE id={id}', mod_data.RequestTypes.ReturnData)
	_current_project['id'] = id
	_current_project['name'] = projects[0][1]
	_current_project['path'] = projects[0][2]
	_sb_project_name.setText(_current_project['name'])


# def _project_indexed():
# 	global _toolbar
# 	if _toolbar.currentData() is not None:
# 		results = mod_data.execute(f'SELECT path FROM projects WHERE id = {_toolbar.currentData()}')
# 		gui_globals.main_window.le_path.setText(results[0][0])


# def _project_changed(value):
# 	print(value)


def test_dock():
	treeView = QTreeView(gui_globals.main_window)
	treeView.setHeaderHidden(True)

	treeModel = QStandardItemModel()
	rootNode = treeModel.invisibleRootItem()
	america = QStandardItem('America')
	california = QStandardItem('California')
	america.appendRow(california)

	oakland = QStandardItem('Oakland')
	sanfrancisco = QStandardItem('San Francisco')
	sanjose = QStandardItem('San Jose')

	california.appendRow(oakland)
	california.appendRow(sanfrancisco)
	california.appendRow(sanjose)

	rootNode.appendRow(america)

	treeView.setModel(treeModel)
	treeView.expandAll()
	treeView.doubleClicked.connect(get_value)

	the_dock = QDockWidget('Struktur', gui_globals.main_window)
	the_dock.setWidget(treeView)
	gui_globals.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, the_dock)


def get_value(val):
	print(val.data())
	print(val.row())
	print(val.column())


def connect_actions():
	gui_globals.main_window.act_mn_project_quit.triggered.connect(lambda: act_mn_project_quit())
	gui_globals.main_window.act_mn_app_projectmanager.triggered.connect(lambda: project_settings())
	# gui_globals.main_window.btn_get_scan_path.clicked.connect(lambda: btn_get_scan_path())
	gui_globals.main_window.act_mn_tb_ReadImages.triggered.connect(lambda: midi())


# gui_globals.main_window.act_mn_project_project_settings.triggered.connect(lambda: midi())
# gui_globals.main_window.act_tb_mn_structure.triggered.connect(lambda: structure_dock())


def structure_dock():
	widget = QWidget()
	layout = QVBoxLayout()

	button_group = QHBoxLayout()
	first_button = QPushButton('Neu')
	second_button = QPushButton('Alt')
	button_group.addWidget(first_button)
	button_group.addWidget(second_button)

	layout.addLayout(button_group)

	widget.setLayout(layout)

	struct_dock = QDockWidget('Struktur', gui_globals.main_window)
	struct_dock.setWidget(widget)
	gui_globals.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, struct_dock)


def _load_project_data(dialog, source_element, target_elements):
	global _mdis
	element = getattr(_mdis[dialog], source_element)
	if element.currentData() is not None:
		results = mod_data.execute(f'SELECT name, path FROM projects WHERE id = {element.currentData()}')
		if isinstance(target_elements, list):
			if len(results[0]) == len(target_elements):
				for index, target_element in enumerate(target_elements):
					getattr(_mdis[dialog], target_element).setText(results[0][index])
		else:
			getattr(_mdis[dialog], target_elements).setText(results[0][0])


def project_settings():
	global _mdis

	path = Path(os.getcwd(), 'gui', 'mdis', 'projectmanagement', 'mdi.ui')
	_mdis['projects'] = uic.loadUi(str(path))
	_mdis['projects'].setMaximumSize(591, 187)
	_mdis['projects'].setFixedSize(591, 178)
	_mdis['projects'].cb_project_selection.currentIndexChanged.connect(
			lambda: _load_project_data('projects', 'cb_project_selection', ['le_project_name', 'le_scan_path']))
	project_settings_fill_chooser()
	_mdis['projects'].btn_scan_path.clicked.connect(lambda: btn_get_scan_path('projects', 'le_scan_path'))

	_mdis['projects'].btn_new_project.clicked.connect(btn_new_project)
	# _mdis['projects'].btn_new_project.btn_delete_project()
	_mdis['projects'].btn_save.clicked.connect(btn_save)
	gui_globals.main_window.mdi_area.addSubWindow(_mdis['projects'])
	_mdis['projects'].show()


def project_settings_fill_chooser():
	projects = mod_data.execute("SELECT * FROM projects WHERE active = 1", mod_data.RequestTypes.ReturnData)
	_mdis['projects'].cb_project_selection.clear()
	_mdis['projects'].cb_project_selection.insertItem(0, 'Bitte wählen')
	_mdis['projects'].cb_project_selection.setItemData(0, 0)
	for index, project in enumerate(projects):
		_mdis['projects'].cb_project_selection.insertItem(index + 1, project[1])
		_mdis['projects'].cb_project_selection.setItemData(index + 1, project[0])


def midi():
	path = Path(os.getcwd(), 'gui', 'mdis', 'projectmanagement', 'mdi.ui')
	dialog = uic.loadUi(str(path))
	gui_globals.main_window.mdi_area.addSubWindow(dialog)
	dialog.show()


# sub = QMdiSubWindow()
# sub.setWidget(QTextEdit())
# sub.setWindowTitle(f"subwindow{str(MainWindow.count)}")
# self.mdi.addSubWindow(sub)
# sub.show()


def act_mn_project_quit():
	exit(0)


def projects_test():
	path = Path(os.getcwd(), 'gui', 'windows', 'main_window', 'projects.ui')
	widget = uic.loadUi(str(path))
	gui_globals.main_window.setCentralWidget(widget)

def btn_save():
	pass

def btn_new_project():
	mod_data.execute(f'INSERT INTO projects (name, path, active) VALUES (\'New Project\', \'not set\', 1)', mod_data.RequestTypes.NoReturn)
	project_settings_fill_chooser()


def btn_get_scan_path(target_dialog, target_element):
	dlg = QFileDialog()
	dlg.setFileMode(QFileDialog.FileMode.Directory)

	if dlg.exec():
		getattr(_mdis[target_dialog], target_element).setText(dlg.selectedFiles()[0])
# f = open(filenames[0], 'r')
#
# with f:
#     data = f.read()
#     self.contents.setText(data)
