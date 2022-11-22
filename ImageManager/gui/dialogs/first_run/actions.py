from ImageManager.gui.dialogs.first_run import globals


def text_has_changed():
    enable_button = False
    for field in globals.dialog['form_content']:
        if globals.dialog['form_content'][field].text() != '' and not globals.dialog['form_content'][field]['optional']:
            enable_button = True

    if enable_button:
        globals.dialog['forward_button'].setEnabled(True)


def get_inputs():
    values = [{field: globals.dialog['form_content'][field].text()} for field in globals.dialog['form_content']]
    print(values)
