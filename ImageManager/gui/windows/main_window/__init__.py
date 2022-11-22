from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QLabel

from ImageManager import data as mod_data

from ImageManager.gui import globals as gui_globals
from ImageManager.app import globals as app_globals

_toolbar = None
_mdis = {}


def setup():
    _connect_actions('menus')
    _get_projects()
    _statusbar()
    _enable_disable('disable')


def _connect_actions(which):
    # if which == 'menus':
    # 	actions = [{'name': 'act_mn_project_quit', 'router_value': 'quit'}, {'name': 'act_mn_app_projectmanager', 'router_value': 'mdi_projectmanagement'}]
    #
    # 	for action in actions:
    # 		getattr(gui_globals.main_window, action['name']).triggered.connect(lambda: _actions_router(action['router_value']))
    gui_globals.main_window.act_mn_project_quit.triggered.connect(lambda: _actions_router('quit'))
    gui_globals.main_window.act_mn_app_projectmanager.triggered.connect(lambda: _actions_router('mdi_projectmanagement'))
    gui_globals.main_window.act_mn_tb_ReadImages_di.triggered.connect(lambda: _actions_router('progress', 'read_files', 'Dateien einlesen', 'Liest alle Bild-/Audiodateien in einem Verzeichnis und den darinnen enthaltenten Unterverzeichnissen für die spätere Verarbeitung ein.'))
    gui_globals.main_window.act_mn_checks_clean_up_di.triggered.connect(lambda: _actions_router('progress', 'clean_up', 'Aufräumen', 'Überprüft, ob es bestimmte Dateien gibt, welche keine Bild-/Audiodateien sind und löscht diese.'))
    gui_globals.main_window.act_mn_checks_doublets_di.triggered.connect(lambda: _actions_router('progress', 'check_dublettes', 'Dubletten finden',
                                                                                                'Prüft anhand verschiedener Parameter, ob es Dubletten unter den Bild-/Videodateien gibt. Dieser Vorgang geschieht in zwei Operationen, welche hintereinander ausgeführt werden. Wird der Vorgang abgebrochen, wird er an derselben Stelle wieder fortgesetzt.'))
    gui_globals.main_window.act_mn_checks_hashes_di.triggered.connect(lambda: _actions_router('progress', 'check_hashes', 'Hashwerte vergleichen',
                                                                                              'Überprüft die Hashwerte eines jeden Bildes mit jedem anderen Bild und versucht so, Dublikate zu finden. Dieser Vorgang kann sehr lange dauern. Wird der Vorgang abgebrochen, kann er beim nächsten Mal an derselben Stelle fortgesetzt werden (automatisch)'))

    gui_globals.main_window.act_mn_processing_doublets.triggered.connect(lambda: _actions_router('show_doublets'))


def _get_projects():
    projects_menu = gui_globals.main_window.submn_app_projects
    projects = mod_data.execute("SELECT * FROM projects", mod_data.RequestTypes.ReturnData)
    for project in projects:
        new_action = QAction(project[1], gui_globals.main_window)
        new_action.triggered.connect(lambda: _actions_router('set_project', project[0]))
        projects_menu.addAction(new_action)


def _actions_router(action: str, *args):
    try:
        the_func = globals()[f'_action_{action}']
        if len(args) > 0:
            the_func(args)
        else:
            the_func()
    except Exception:
        if action == '':
            pass


def _statusbar():
    project_name = QLabel()

    project_name.setText('Kein Projekt gewählt')
    gui_globals.main_window.sb_statusbar.addPermanentWidget(project_name)


def _set_project_name(project_name):
    for child in gui_globals.main_window.sb_statusbar.children():
        if isinstance(child, QLabel):
            child.setText(project_name)
            return


def _enable_disable(what):
    for key in gui_globals.main_window.__dict__:
        if '_di' in key:
            getattr(gui_globals.main_window, key).setEnabled(False if what.lower() == 'disable' else True)


# -----------------------------------------------------------------------------------------------
def _action_progress(*args):
    from ImageManager.gui.mdis import progress as mdi_progress
    mdi_progress.setup(args[0][0], args[0][1], args[0][2])


def _action_show_doublets():
    from ImageManager.gui.mdis import doublets as mdi_duplette
    mdi_duplette.setup()


def _action_set_project(id):
    projects = mod_data.execute(f'SELECT id, name, path FROM projects WHERE id={id[0]}', mod_data.RequestTypes.ReturnData)
    app_globals.current_project['id'] = id
    app_globals.current_project['name'] = projects[0][1]
    app_globals.current_project['path'] = projects[0][2]
    _set_project_name(app_globals.current_project['name'])
    _enable_disable('enable')


def _action_quit():
    exit(0)


def _action_mdi_projectmanagement():
    from ImageManager.gui.mdis import projectmanagement
    projectmanagement.setup()
