import time
import RPi.GPIO as GPIO

row_pins = []
col_pins = []
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
caps_lock = False

def setup():
  # Use "GPIO" pin numbering
  GPIO.setmode(GPIO.BCM)

  # Make all row pins inputs with pulldowns
  for pin in row_pins:
    GPIO.setup(pin, GPIO.IN)

  # Make all col pins outputs
  for pin in col_pins:
    GPIO.setup(pin, GPIO.OUT)

active_row_cols = []
last_released = 'none'
repeat_press_count = 0
keys_pressed = []

def reset_repeat_pressed():
  last_released = 'none'
  repeat_press_count = 0

def scan(layer = 'num'):
  keys_released = []
  for col_pin in range(4):
    GPIO.output(col_pin, GPIO.HIGH)
    for row_pin in range(4):
      key_code = key_code_layers[layer][row_pin][col_pin]
      if GPIO.input(row_pin): # on keydown
        active_row_cols.append([row_pin, col_pin])
        keys_pressed.append(key_code)
      else:
        if [row_pin, col_pin] in active_row_cols: # on keyup
          # count repeated key presses
          if last_released == [row_pin, col_pin]:
            repeat_press_count = repeat_press_count + 1
          else:
            repeat_press_count = 0

          if key_code == 'toggleCap':
            caps_lock = not caps_lock
          else:
            if keys_pressed.count(key_code) > 9: # if key was long pressed default to num layer
              key_code = key_code_layers['num'][row_pin][col_pin]
            # add key value to keys released
            val = key_code[repeat_press_count % len(key_code)]
            if caps_lock:
              key_code = val.upper()
            keys_released.append(val)
          active_row_cols.remove([row_pin, col_pin])
        while key_code in keys_pressed:
          keys_pressed.remove(key_code)
    GPIO.output(col_pin, GPIO.LOW)
  time.sleep(0.1) # number of duplicate codes in keys_pressed * 1/10 second give length of press
  return {
    'pressed': keys_pressed,
    'released': keys_released
  }


def cleanup(): 
  GPIO.cleanup()