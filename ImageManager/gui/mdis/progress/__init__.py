import locale
import os
from pathlib import Path

from PyQt6 import uic

from ImageManager.gui import globals as gui_globals


_my_module = ''


def setup(module, topic, description):
	global _my_module
	locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
	_my_module = module
	path = Path(os.getcwd(), 'gui', 'mdis', 'progress', 'mdi.ui')
	gui_globals.active_mdis['progress'] = uic.loadUi(str(path))

	gui_globals.active_mdis['progress'].pgb_progress.setValue(0)
	gui_globals.active_mdis['progress'].pgb_progress_ii.setValue(0)
	gui_globals.active_mdis['progress'].lbl_topic.setText(topic)
	gui_globals.active_mdis['progress'].pte_log.setPlainText(description)
	_connect_actions()

	gui_globals.main_window.mdi_area.addSubWindow(gui_globals.active_mdis['progress'])
	gui_globals.active_mdis['progress'].show()


def _connect_actions():
	gui_globals.active_mdis['progress'].btn_start.clicked.connect(lambda: _actions_router('start_scan'))
	gui_globals.active_mdis['progress'].btn_stop.clicked.connect(lambda: _actions_router('stop_scan'))


def _actions_router(action, *args):
	try:
		func = globals()[f'_action_{action}']
		if len(args) > 0:
			func(args)
		else:
			func()
	except Exception as ex:
		print(ex)
		if action == '':
			pass


# ---------------------- Actions
def _action_start_scan():
	global _my_module
	if _my_module == 'read_files':
		from ImageManager.app import read as app_read
		app_read.find_files()
	if _my_module == 'clean_up':
		from ImageManager.app import checks as app_checks
		app_checks.clean_up()
	if _my_module == 'check_hashes':
		from ImageManager.app import checks as app_checks
		app_checks.check_hashes()
	if _my_module == 'check_dublettes':
		from ImageManager.app import checks as app_checks
		app_checks.check_doublets_files()

def _action_stop_scan():
	pass


if __name__ == '__main__':
	pass
