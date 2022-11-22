import locale
import os
from pathlib import Path
import re

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QStandardItem, QStandardItemModel

from ImageManager.gui import globals as gui_globals
from ImageManager import data as mod_data

_images = []


def setup():
    path = Path(os.getcwd(), 'gui', 'mdis', 'doublets', 'mdi.ui')
    gui_globals.active_mdis['doublets'] = uic.loadUi(str(path))

    results = mod_data.execute('SELECT id FROM doublets_mapping', mod_data.RequestTypes.ReturnData)

    for index, result in enumerate(results):
        gui_globals.active_mdis['doublets'].lw_doublets.addItem(f'Fund {index + 1} ({result[0]})')

    _connect_actions()

    gui_globals.main_window.mdi_area.addSubWindow(gui_globals.active_mdis['doublets'])
    gui_globals.active_mdis['doublets'].show()


def _connect_actions():
    gui_globals.active_mdis['doublets'].lw_doublets.doubleClicked.connect(lambda: _actions_router('load_result'))
    gui_globals.active_mdis['doublets'].btn_confirm.clicked.connect(lambda: _actions_router('confirm'))
    gui_globals.active_mdis['doublets'].btn_discard.clicked.connect(lambda: _actions_router('no_doublet'))


def _load_image(image_path, image, suffix, destination=1):
    path = str(Path(image_path, image + '.' + suffix))
    img = QPixmap(path)
    img = img.scaled(512, 512, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)

    if destination == 1:
        gui_globals.active_mdis['doublets'].lbl_img_one_container.setPixmap(img)
    if destination == 2:
        gui_globals.active_mdis['doublets'].lbl_img_two_container.setPixmap(img)

    return path


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


def _remove_doublet(id):
    global _images
    query = f'DELETE FROM doublets_mapping WHERE id = {id}'
    mod_data.execute(query, mod_data.RequestTypes.NoReturn)
    gui_globals.active_mdis['doublets'].lw_doublets.takeItem(gui_globals.active_mdis['doublets'].lw_doublets.currentRow())
    gui_globals.active_mdis['doublets'].lbl_img_one_container.clear()
    gui_globals.active_mdis['doublets'].lbl_img_two_container.clear()
    gui_globals.active_mdis['doublets'].lbl_img_one_path_value.setText()
    gui_globals.active_mdis['doublets'].lbl_img_one_path_value.setText()


# ---------------------- Actions
def _action_confirm():
    global _images
    if gui_globals.active_mdis['doublets'].rb_img_one.isChecked():
        Path(_images[0]).unlink()
    if gui_globals.active_mdis['doublets'].rb_img_two.isChecked():
        Path(_images[1]).unlink()
    _remove_doublet(_images[2])


def _action_no_doublet():
    global _images
    _remove_doublet(_images[2])


def _action_load_result():
    global _images
    item = gui_globals.active_mdis['doublets'].lw_doublets.selectedItems()[0].text()
    id = re.search('([0-9])', item).group()

    query = f'SELECT source_id, destination_id FROM doublets_mapping WHERE id = {id}'
    results = mod_data.execute(query)[0]

    source_data = mod_data.execute(f'SELECT file_name, suffix, path, id FROM files WHERE id = {results[0]}')[0]
    dest_data = mod_data.execute(f'SELECT file_name, suffix, path, id FROM files WHERE id = {results[1]}')[0]

    _images.append(_load_image(source_data[2], source_data[0], source_data[1]))
    _images.append(_load_image(dest_data[2], dest_data[0], dest_data[1], 2))
    _images.append(id)

    gui_globals.active_mdis['doublets'].lbl_img_one_path_value.setText(_images[0])
    gui_globals.active_mdis['doublets'].lbl_img_one_path_value.setText(_images[1])


if __name__ == '__main__':
    pass
