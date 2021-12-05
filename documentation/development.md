[< TOC/README](../README.md)
# Hardware Password Manager: Development 

## Next release V0.1.1
- *improvement*: (**breaking change**) Replace folder hash naming with faster (non bcrypt) lookup hashing 
- *fix*: Newly added entries hidden until another entry added
- *feature*: Add indication on send
- *feature*: Setting to auto enter on send
- *fix*: Short press key combos (on press) won't work, need to change method for handling fn keys/onPress events
- *fix*: 'shutting down...' no longer displays (maybe shutdown starts before view has time to render)
- *feature*: Configs: 
    - One file 
    - Add: 
        - Password: length, legal chars
        - Passphrase: word count, max word length
        - Username: word count, max word length
        - Auto enter on send

## Future development 
- Create and store public/private key pairs
- GUI interface for HDMI display (Possibly just using tkinter)
- UI improvements for oled display 
    - A search filter on browse view
    - Selected view
    - Display current toggle key chars ([a,**b**,c])
    - Delete/Update confirmation vie
- Send capslock state off to computer on transmit? as if it's set on the target computer caps will be inverted
- A system for creating backups. 
    - Plug in another OS image SD card and you get a duplicate for storing somewhere secure or to use on a second device
- Script for automating dummy user creation
    - Plus script to update modified date on user files at random times while device is on (so real users don't always have latest modified date!) 
- Change password feature: retains old password, while allowing generation/entering of new password
- Optional usernames words file
- Quick start guide
    - Setup script
    - Brief hardware reference diagram 
- V2 Device hardware
    - Bigger touch screen LCD display 
    - Touch input in place of keypad 
    - More compact 
    - PIC as HID. This would make make it harder for an adversary (who had physical access to the device) setting up a key logger. The arduino can be programmed via USB by simply pulling the programing pin down

