import os

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton
from PyQt6 import uic, QtWidgets
from pathlib import Path
from ImageManager.gui import globals as gui_globals
from ImageManager.gui.dialogs.first_run import actions
from ImageManager.gui.dialogs.first_run import definitions
from ImageManager.gui.dialogs.first_run import globals


def show():
    path = Path(os.getcwd(), 'gui', 'dialogs', 'first_run', 'dialog.ui')
    globals.dialog = uic.loadUi(str(path))
    globals.dialog.exec()
    # _init()
    # _forward_button()
    # _base_layout()
    # _explaining_text()
    # _form()
    #
    # _finalize()
    #
    # globals.dialog['dialog'].exec()


def _finalize():
    globals.dialog['layout'].addLayout(globals.dialog['form'])
    globals.dialog['layout'].addWidget(globals.dialog['forward_button'])
    globals.dialog['dialog'].setLayout(globals.dialog['layout'])


def _init():
    globals.dialog = {'dialog': QDialog(gui_globals.window_reference)}
    globals.dialog['dialog'].setWindowTitle("WLH - Erster Start")


def _forward_button():
    globals.dialog['forward_button'] = QPushButton()
    globals.dialog['forward_button'].setText('Weiter')
    globals.dialog['forward_button'].setEnabled(False)
    globals.dialog['forward_button'].clicked.connect(lambda: actions.get_inputs())


def _base_layout():
    globals.dialog['layout'] = QVBoxLayout()


def _form():
    globals.dialog['form_content'] = {}
    globals.dialog['form'] = QFormLayout()
    for field in definitions.form_fields:
        globals.dialog['form_content'][field] = QLineEdit()
        globals.dialog['form_content'][field].setObjectName(definitions.form_fields[field]['object_name'])
        globals.dialog['form_content'][field].editingFinished.connect(lambda: actions.text_has_changed())
        if definitions.form_fields[field]['optional']:
            globals.dialog['form_content'][field].setPlaceholderText('Kein Pflichtfeld')

        globals.dialog['form'].addRow(definitions.form_fields[field]['text'], globals.dialog['form_content'][field])


def _explaining_text():
    lines = ["Es sieht so aus, als wenn Du WLH zum ersten Mal starten würdest.",
             "Deshalb müssen wir ein paar Dinge einstellen."]

    globals.dialog['layout'] = helper.labels(lines, globals.dialog['layout'])
