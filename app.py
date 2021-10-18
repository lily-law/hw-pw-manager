import math
import keypad
import display
import gen
import re


state = {
    'service': '',
    'username': '',
    'password': '',
    'entries': [],
    'selected_entry_index': False,
    'selected_row': 'pin',
    'view': 'browse',
    'page': 0,
    'page_entry_indexes': [],
    'n_pages': 0,
    'results_per_page': 5,
    'inputting': False,
    'pin': '',
    'key_layer': 'num',
    'key_buffer': ''
}


def load_entries():
    set_view('loading')
    # TODO load data from file
    # decrypt data
    # JSON parse data
    # set entries into state
    # set n_pages state
    return

def save_entries():
    set_view('saving')
    # TODO JSON stringify state['entries']
    # encrypt data
    # save data to new file
    # rename old file
    # rename new file
    # delete old file
    return


def render_view():
    display.views[state['view']](**state)

def set_view(to):
    state['view'] = to 
    if to == 'browse':
        set_page_entry_indexes()
    else:
        if to == 'lock':
            state['pin'] = ''
            state['inputting'] = True
            state['entries'] = []
        render_view()

def set_page_entry_indexes():
    start = state['page'] * state['results_per_page']
    state['page_entry_indexes'] = range(start, start + state['results_per_page'])
    render_view()

def prev_page():
    if state['page'] > 0:
        state['page'] = state['page'] - 1
        set_page_entry_indexes()

def next_page():
    if state['n_pages'] > state['page']: # is at least one entry for page
        state['page'] = state['page'] + 1
        set_page_entry_indexes()

def transmit(str):
    return

def exit_editing():
    state['service'] = ''
    state['username'] = ''
    state['password'] = ''
    state['inputting'] = False
    state['n_pages'] = math.ceil(state['entries'] / state['results_per_page'])
    state['selected_entry_index'] = False
    set_view('browse')

def power_down():
    set_view('shutdown')
    keypad.cleanup()
    # TODO
    return

def handle_fn_keys(keys):
    if len(keys) > 0:
        if 'FN1' in keys: #A
            if state['view'] == 'browse': # add new entry
                # set states to plus 1 entry from last page 
                n_entries = len(state['entries'])
                state['n_pages'] = math.ceil((n_entries + 1) / state['results_per_page'])
                state['page'] = state['n_pages']
                state['selected_entry_index'] = n_entries
                set_view('edit')
            elif state['view'] == 'view' and '#' in keys and state['selected_entry_index']: # edit selected entry
                set_view('edit')
            elif state['view'] == 'edit': # generate input
                if state['selected_row'] == 'username':
                    state['username'] = gen.username()
                elif state['selected_row'] == 'password':
                    state['password'] = gen.password()
        elif 'FN2' in keys: #B
            if state['inputting'] and len(state[state['selected_row']]) > 0: # Backspace on inputing pin or entries
                state[state['selected_row']] = state[state['selected_row']][:-1]
            elif state['view'] == 'view' and not state['inputting']: # Back to browse view 
                set_view('browse')
        elif 'FN3' in keys: #C
            if state['view'] == 'lock' and keys.count('*') > 9: # power down if * has been held for 1 second
               power_down()
            elif state['view'] == 'browse' and keys.count('*') > 9: # lock device if * has been held for 1 second
                set_view('lock')
            elif state['view'] == 'view' and '#' in keys and state['selected_row']: # send entry to pico 
                transmit(state['entries'][state['selected_entry_index']][state['selected_row']])
            elif state['view'] == 'edit': # cancel entry/edit
                # reset inputs, update states and return to browse view
                exit_editing()
        elif 'FN4' in keys: #D
            if state['view'] == 'lock': # submit pin
                load_entries()
                set_view('browse')
            elif state['view'] == 'edit' and state['inputting']: # save entry
                # update selected_entry
                entry = state['entries'][state['selected_entry_index']]
                entry['service'] = state['service']
                entry['username'] = state['username']
                entry['password'] = state['password']
                # Save entries state to disk
                save_entries()
                # reset inputs, update states and return to browse view
                exit_editing()
            elif state['view'] == 'view' and keys.count('*') > 9: # delete entry if * has been held for 1 second
                # Remove entry from state
                state['entries'].remove(state['selected_entry_index'])
                # Save entries state to disk
                save_entries()
                # reset inputs, update states and return to browse view
                exit_editing()

def select_entry_row(keys):
    if '1' in keys: 
        state['selected_row'] = 'service'
    elif '2' in keys: 
        state['selected_row'] = 'username'
    elif '3' in keys: 
        state['selected_row'] = 'password'


# URL regex pattern from https://stackoverflow.com/questions/22038142/regex-for-valid-url-characters
valid_url_chars = re.compile(r"[-\]_.~!*'();:@&=+$,/?%#[A-z0-9]", re.IGNORECASE)
valid_pin = re.compile(r"[0-9#*]")
def set_state_input(keys, valid_reg): 
    valid_chars = list(filter(lambda key : valid_reg.search(key), keys))
    state[state['selected_row']] = f"{ state[state['selected_row']] }{ ''.join(valid_chars) }"

def handle_keys(keys): 
    if len(keys) > 0: 
        if state['view'] == 'lock': # add input to pin state
            set_state_input(keys, valid_pin)
        elif state['view'] == 'browse':
            valid_row_keys = list(filter(lambda key : re.search(rf"[1-{state['results_per_page']}]", key) and len(state['page_entry_indexes'] > int(key)), keys))
            if len(valid_row_keys) > 0: # select entry
                state['selected_entry_index'] = (int(valid_row_keys[0]) - 1) + (state['page'] * state['results_per_page'])
                set_view('view')
            elif '*' in keys:
                prev_page()
            elif '#' in keys:
                next_page()
        elif state['view'] == 'view':
            select_entry_row(keys)
        elif state['view'] == 'edit':
            if state['inputting']: 
                set_state_input(keys, valid_url_chars)
            else:
                select_entry_row(keys)               
        else: 
            set_view('browse')

keypad.setup()

if __name__ == "__main__":
    while True:
        # TODO check if powered else power_down()

        # check for keypress
        if state['inputting'] and state['selected_row'] != 'pin':
            keys = keypad.scan(layer = 'char')
        else:
            keys = keypad.scan(layer = 'num')
        handle_fn_keys(keys.pressed)
        handle_keys(keys.released)

