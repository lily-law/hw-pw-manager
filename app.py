import math
import keypad
import display
import gen

data = {
    'entries': []
}

state = {
    'service': '',
    'username': gen_username(),
    'password': gen_password(),
    'entries': [],
    'selected_entry': False,
    'selected_row': 'service',
    'view': 'browse',
    'page': 0,
    'inputting': False,
    'pin': '',
    'key_layer': 'num',
    'key_buffer': ''
}

def set_view(to):
    state['view'] = to 
    display.views[view](**state)

def prev_page():
    if state['page'] > 0:
        state['page'] = state['page'] - 1
    return

def next_page():
    if data['entries'] > (state['page'] + 1) * 6:
        state['page'] = state['page'] + 1
    return

def handle_fn_keys(keys):
    if len(keys) > 0:
        if 'FN1' in keys: #A
            if state['view'] == 'browse':
                # add new entry
                set_view('edit')
            elif state['view'] == 'view' and '#' in keys and state['selected_entry']:
                # selected edit entry
                set_view('edit')
            elif state['view'] == 'edit':
                # start inputing text
                state['inputting'] = True

        elif 'FN2' in keys: #B
            return
        elif 'FN3' in keys: #C
            return
        elif 'FN4' in keys: #D
            if state['inputting']: 
                state['inputting'] = False
                # todo save inputs
                # append/update selected_entry to entries
                # reset inputs
            return

def handle_keys(keys): 
    if len(keys) > 0: 
        if state['view'] == 'browse':
            if keys[0] in range(1, 7) and keys[0] < len(entries):
                state['selected_entry'] = keys[0]
            elif keys[0] == '*':
                prev_page()
            elif keys[0] == '#':
                next_page()
        elif state['view'] == 'view':
            if keys[0] == 1: 
                state['selected_row'] = 'service'
            elif keys[0] == 2: 
                state['selected_row'] = 'username'
            elif keys[0] == 3: 
                state['selected_row'] = 'password'
        elif state['view'] == 'edit':
            if state['inputting']: 
                # if done
                if keys[0] == 'D':
                    state['inputting'] = False
                    # todo save inputs
                    # append/update selected_entry to entries
                    # reset inputs
                else:
                    # append to input
                    if not state['key_buffer'] or keys[0] in state['key_buffer']:
                        state['key_buffer'] += keys[0]
                    else:
                        value = get_key_value(state['key_buffer'])
                        state[state['inputting']] += value
                    
        else: 
            set_view('browse')

keypad.setup()

while True:
    # check for keypress
    keys = keypad.scan()
    handle_fn_keys(keys.pressed)
    handle_keys(keys.released)

keypad.cleanup()
