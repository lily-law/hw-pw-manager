import keypad
from signal import pause

keypad.setup()

def cb(data):
  print(data)

while True:
  keypad.enable(cb, 'char')

