import serial

def transmit(txt):
    error = False
    with serial.Serial() as ser:
        ser.baudrate = 19200
        ser.port = 'COM1' # '/dev/ttyS0', # ttyAM0 on < PI 3   
    try:
        ser.open()
        ser.write(bytes(txt, 'utf-8'))
    except:
        error = 'Unable to transmit'
    finally:
        if ser.is_open:
            ser.close()
        return error