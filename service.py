def get_inline_button_text_callback(keyboard):
    buttons_info = []
    for buttons in keyboard.to_dict()['inline_keyboard']:
        for button in buttons:
            buttons_info.append(button)

    return buttons_info
