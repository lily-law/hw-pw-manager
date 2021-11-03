import serial

def send(txt):
    error = False
    with serial.Serial() as ser:
        ser.baudrate = 19200
        ser.port = '/dev/ttyAMA0' # '/dev/ttyS0', # ttyAMA0 on < PI 3
    try:
        ser.open()
        ser.write(bytes(txt, 'utf-8'))
    except:
        error = 'Unable to send. Is serial port correct? Is serial is enabled in raspi-config? Try disabling and re enabling it.'
    finally:
        if ser.is_open:
            ser.close()
        return error
