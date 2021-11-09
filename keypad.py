from gpiozero import Button, OutputDevice
import time

# define pin numbers (BCM)
row_pin_numbers = [5, 6, 13, 19]
col_pin_numbers = [4, 17, 27, 22]
key_code_layers = {
  'num': [
    [['1'],['2'],['3'],['FN1']],
    [['4'],['5'],['6'],['FN2']],
    [['7'],['8'],['9'],['FN3']],
    [['*'],['0'],['#'],['FN4']]
  ],
  'char': [
    [['toggleCaps'], ['a','b','c'], ['d','e','f'], ['FN1']],
    [['g','h','i'], ['j','k','l'],['m','n','o'], ['FN2']],
    [['p','q','r','s'],['t','u','v'],['w','x','y','z'], ['FN3']],
    [['.', '-', '_', '~', '\'', ','], ['@','!','&','$','?','%'], ['/',';',':','(',')','[',']','=','+'], ['FN4']]   
  ],
}

state = {
    'caps_lock': False,
    'repeat_press_count': 0,
    'active_row_cols': [],
    'last_pressed': False,
    'last_press_time': 0,
    'longpress_row_cols': []
}


def get_val(r, c, layer, is_longpress):
  # lookup keycode
  if is_longpress: # if key was long pressed
    key_code = key_code_layers['num'][r][c] # default to num layer
  else:
    key_code = key_code_layers[layer][r][c]

  # find val of key
  val = key_code[state['repeat_press_count'] % len(key_code)]
  if state['caps_lock']:
    val = val.upper()
  return val


row_pins = []
col_pins = []
def setup():
  # Make all row pins inputs with pulldowns
  for pin in row_pin_numbers:
    row_pins.append(Button(pin, pull_up=False, hold_time=1, bounce_time=0.02))

  # Make all col pins outputs
  for pin in col_pin_numbers:
    col_pins.append(OutputDevice(pin, initial_value=True))


def set_all_outputs(on):
  for output in col_pins:
    if on:
      output.on()
    else:
      output.off()

def output_scan(cb, input_pin, layer, event_type):
  key_vals = []
  r = row_pins.index(input_pin)
  if event_type == 'released':
    for row_col in list(filter(lambda rc: rc[0] == r, state['active_row_cols'])): 
      # Release all columns on r row
      c = row_col[1]
      state['active_row_cols'].remove([r, c])
      val = get_val(r, c, layer, False)
      if val == 'toggleCaps' or val == 'TOGGLECAPS': # internal state, not for char output
        state['caps_lock'] = not state['caps_lock']
      elif val:
        key_vals.append(val)
        if state['repeat_press_count'] > 0 and len(key_code_layers[layer][r][c]) > 1: # val toggled send message to remove last inserted val
          key_vals.append('val_toggle')
  else:
    if event_type == 'pressed':
      set_all_outputs(False) # set all outputs low
      for c, col_pin in enumerate(col_pins): # check each output to input in turn
        col_pin.on()
        if input_pin.is_pressed:  # found active col for row if pin is still pressed
          if [r, c] not in state['active_row_cols']: 
            state['active_row_cols'].append([r, c])
            if state['last_pressed'] and state['last_pressed'] == [r, c] and time.time() - state['last_press_time'] < 1:
              state['repeat_press_count'] += 1
            else: 
              state['repeat_press_count'] = 0
            state['last_pressed'] = [r, c]
            state['last_press_time'] = time.time()
            val = get_val(r, c, layer, False)
            if val:
              key_vals.append(val)
        col_pin.off()
      set_all_outputs(True) # set all outputs back to high
    elif event_type == 'longpress':
      # Dump all active_row_cols as longpress vals
      for active in state['active_row_cols']:
        val = get_val(active[0], active[1], layer, True)
        key_vals.append(val)
      state['active_row_cols'] = []
  if len(key_vals) > 0:
    cb({
      event_type: key_vals
    })
 
def on_change(cb, input_pin, layer, event_type):
  repeat_scan_count = [0]
  def find_change():
    output_scan(cb, input_pin, layer, event_type)
    time.sleep(0.01)
    if event_type == 'pressed' and input_pin.is_pressed and repeat_scan_count[0] < 50: # repeat scan to find any keys on same row
      repeat_scan_count[0] += 1
      find_change()
    else:
      repeat_scan_count[0] = 0
  return find_change

def on_hold(cb, input_pin, layer):
  def callback():
    if input_pin.held_time and input_pin.held_time >= 0.9:
      find_change = on_change(cb, input_pin, layer, 'longpress')
      find_change()
  return callback

def enable(cb, layer = 'num'):
  for input_pin in row_pins:
    input_pin.when_pressed = on_change(cb, input_pin, layer, 'pressed')
    input_pin.when_released = on_change(cb, input_pin, layer, 'released')
    input_pin.when_held = on_change(cb, input_pin, layer, 'longpress')

