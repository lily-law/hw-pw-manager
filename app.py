import math
import keypad
import display
import gen
import re
import os
from disk import Entries
import time
import output

state = {
    'service': '',
    'username': '',
    'password': '',
    'entries': [],
    'selected_entry_index': False,
    'selected_row': '',
    'view': 'lock',
    'page': 0,
    'page_entry_indexes': [],
    'n_pages': 0,
    'results_per_page': 2,
    'inputting': False,
    'pin': '',
    'user': '',
    'storage': False,
    'failed_login': False,
    'loading_message': '',
    'error_message': ''
}


def set_error(msg):
    state['error_message'] = msg
    set_view('error')


def load_entries():
    set_view('loading')
    # load data from file
    state['entries'] = state['storage'].load()
    # reset inputs, update states and return to browse view
    exit_editing()


def save_entries():
    set_view('saving')
    state['storage'].save(state['entries'])
    # reset inputs, update states and return to browse view
    exit_editing()


def render_view():
    display.views[state['view']](**state)


def set_view(to):
    state['view'] = to
    if to not in ['lock', 'loading', 'error'] and state['storage'] == False:
        set_view('lock')
    elif to == 'browse':
        if len(state['entries']) > 0:
            state['selected_entry_index'] = False
            set_page_entry_indexes()
        else:
            # New pin/user
            set_view('welcome') 
            render_view()
    else:
        if to == 'lock':
            state['storage'] = False
            state['inputting'] = True
            state['entries'] = []
            state['selected_row'] = ''
        if to == 'welcome' and len(state['entries']) > 0:
            set_view('browse')
        render_view()
    enable_key_input()


def set_page_entry_indexes():
    start = state['page'] * state['results_per_page']
    end = start + state['results_per_page']
    if end > len(state['entries']) - 1:
        end = len(state['entries']) - 1
    state['page_entry_indexes'] = range(start, end)
    render_view()


def prev_page():
    if state['page'] > 0:
        state['page'] = state['page'] - 1
        set_page_entry_indexes()


def next_page():
    if (len(state['entries']) / state['results_per_page']) > (state['page'] + 1): # is at least one entry for page
        state['page'] = state['page'] + 1
        set_page_entry_indexes()


def transmit(str):
    err = output.send(str)
    if err:
        set_error(err)
    return


def edit_entry(is_new = False):
    if is_new:
        # set states to plus 1 entry from last page 
        n_entries = len(state['entries'])
        state['n_pages'] = math.ceil((n_entries + 1) / state['results_per_page'])
        state['page'] = state['n_pages'] - 1
        state['selected_entry_index'] = n_entries
    else:
        entry = state['entries'][state['selected_entry_index']]
        state['service'] = entry['service']
        state['username'] = entry['username']
        state['password'] = entry['password']
    set_view('edit')


def exit_editing():
    state['service'] = ''
    state['username'] = ''
    state['password'] = ''
    state['inputting'] = False
    state['n_pages'] = math.ceil(len(state['entries']) / state['results_per_page'])
    state['selected_row'] = ''
    state['selected_entry_index'] = False
    set_view('browse')


def power_down():
    set_view('shutdown')
    os.system('sudo systemctl poweroff')
    return


def logout():
    state['user'] = ''
    state['pin'] = ''
    state['storage'] = False
    set_view('lock')

def backspace():
    if state['selected_row'] in state.keys() and len(state[state['selected_row']]) > 0: # Backspace on inputing pin or entries
        state[state['selected_row']] = state[state['selected_row']][:-1]


def handle_fn_keys(keys):
    if len(keys) > 0:
        if 'FN1' in keys: #A
            if state['view'] == 'browse' or state['view'] == 'welcome': # add new entry
                edit_entry(True)
            elif state['view'] == 'view' and '#' in keys: # edit selected entry
                edit_entry()
            elif state['view'] == 'edit' and state['selected_row']: # generate input
                if state['selected_row'] == 'password':
                    state[state['selected_row']] = gen.password()
                elif state['selected_row'] == 'service':
                    state[state['selected_row']] = gen.service()
                else:
                    state[state['selected_row']] = gen.username()
        elif 'FN2' in keys: #B
            if state['inputting']:
                backspace()
            elif state['view'] == 'view': # Back to browse view 
                set_view('browse')
            elif state['view'] == 'browse' and 'longpress' in keys and '*' in keys: # lock device if has been held for 1 second
                logout()
        elif 'FN3' in keys: #C
            if state['view'] == 'lock' and 'longpress' in keys and '*' in keys: # power down if has been held for 1 second
               power_down()
            elif state['view'] == 'view' and '#' in keys and state['selected_row']: # send entry to pico 
                transmit(state['entries'][state['selected_entry_index']][state['selected_row']])
            elif state['view'] == 'edit' and not state['selected_row']: # cancel entry/edit
                # reset inputs, update states and return to browse view
                exit_editing()
            elif state['view'] == 'error': # continue 
                # reset inputs, update states and return to browse view
                exit_editing()
        elif 'FN4' in keys: #D
            if state['view'] == 'lock': 
                if not state['inputting'] and state['user'] and state['pin']: # submit pin
                    state['loading_message'] = 'Logging in'
                    set_view('loading')
                    state['storage'] = Entries(state['pin'], state['user'], set_error)
                    if state['storage'].valid == False:
                        state['storage'] = False
                        state['pin'] = ''
                        state['failed_login'] = True
                        set_view('lock')
                    else:
                        load_entries()
                else: # done editing row
                    select_input_row([], False)
            elif state['view'] == 'edit':
                if not state['selected_row']: # save entry
                    if len(state['entries']) <= state['selected_entry_index']: # Make place for new entry
                        state['entries'].append({})
                    # update selected_entry
                    entry = state['entries'][state['selected_entry_index']]
                    entry['service'] = state['service']
                    entry['username'] = state['username']
                    entry['password'] = state['password']
                    # Save entries state to disk
                    save_entries()
                else: # done editing row
                    select_input_row([], False)
            elif state['view'] == 'view' and 'longpress' in keys and '*' in keys: # delete entry if * has been held for 1 second
                # Remove entry from state
                state['entries'].pop(state['selected_entry_index'])
                # Save entries state to disk
                save_entries()
            elif state['view'] == 'welcome':
                set_view('lock')


def select_input_row(keys, is_editing=True):
    state['inputting'] = is_editing
    sr = state['selected_row']
    if state['view'] == 'edit' or state['view'] == 'view':
        if sr != 'service' and '1' in keys: 
            state['selected_row'] = 'service'
        elif sr != 'username' and '2' in keys: 
            state['selected_row'] = 'username'
        elif sr != 'password' and '3' in keys: 
            state['selected_row'] = 'password'
        else:
            state['selected_row'] = False
            state['inputting'] = False
    elif state['view'] == 'lock':
        if sr != 'user' and '1' in keys:
            state['selected_row'] = 'user'
        elif sr != 'pin' and '2' in keys:
            state['selected_row'] = 'pin'
        else:
            state['selected_row'] = False
            state['inputting'] = False
    enable_key_input()


# URL regex pattern from https://stackoverflow.com/questions/22038142/regex-for-valid-url-characters
valid_url_char = re.compile(r"^[-\]_.~!*'();:@&=+$,/?%#[A-z0-9]{1}$", re.IGNORECASE)
valid_pin = re.compile(r"^[0-9#*]{1}$")
def set_state_input(keys, valid_reg): 
    valid_chars = list(filter(lambda key : valid_reg.search(key), keys))
    if len(valid_chars) > 0:
        if 'val_toggle' in keys:
            backspace()
        state[state['selected_row']] = f"{ state[state['selected_row']] }{ ''.join(valid_chars) }"


def handle_keys(keys): 
    if len(keys) > 0: 
        if state['view'] == 'lock': # add input to pin state
            if state['selected_row'] == 'pin':
                set_state_input(keys, valid_pin)
            elif state['selected_row'] == 'user':
                set_state_input(keys, valid_url_char)
            else: 
                select_input_row(keys)
            if len(state['pin']) > 0: # Reset failed login indicator if active
                state['failed_login'] = False
        elif state['view'] == 'browse':
            if not state['inputting']:
                valid_row_keys = list(filter(lambda key : re.match(rf"[1-{state['results_per_page']}]", key) and len(state['page_entry_indexes']) >= int(key), keys))
                if len(valid_row_keys) > 0: # select entry
                    state['selected_entry_index'] = (int(valid_row_keys[0]) - 1) + (state['page'] * state['results_per_page'])
                    set_view('view')
                elif '*' in keys:
                    prev_page()
                elif '#' in keys:
                    next_page()
        elif state['view'] == 'view':
            valid_row_keys = list(filter(lambda key : re.match(r"[1-3]", key), keys))
            if len(valid_row_keys) > 0: # select entry
                select_input_row(keys, False)
        elif state['view'] == 'edit':
            if state['inputting']: 
                set_state_input(keys, valid_url_char)
            else:
                select_input_row(keys)               


def on_keypress(keys):
    for k in keys.keys():
        if k == 'released':   
            handle_keys(keys[k])
        elif k == 'longpress':
            keys[k].append('longpress')
            handle_keys(keys[k])
            handle_fn_keys(keys[k])
        else:
            handle_fn_keys(keys[k])


def enable_key_input():
    if state['inputting'] and state['selected_row'] != 'pin':
        layer = 'char'
    else:
        layer = 'num'
    keypad.enable(on_keypress, layer)

if __name__ == "__main__":
  keypad.setup()
  enable_key_input()
  while True:
    # TODO check if powered else power_down()
    render_view()
    time.sleep(0.2)
