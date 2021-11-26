# Hardware Password Manager
Hardware password manager with isolated (output only) HID USB interface. 
- Store, index, and generate secure passwords and usernames for services
- More secure and convenient then writing login details down
- Plug in to a USB port, paste entries out through keyboard emulation hardware
- Portable across systems and at boot time (BIOS passwords, hdd decryption...)
- More secure then online password managers

The keyboard emulator has only a receiving link to the password manager hardware. This ensures your stash of passwords and the password manager OS remain secure even when used on a compromised system (this doesn't prevent a threat from logging passwords that you paste out to the keyboard emulator on compromised systems).

Entries are encrypted on the device by a lock pin. You can create multiple logins. Optionally it allows creation of dummy users which adds some hardening to weaker pins. An adversary would have to break multiple pins as well as knowing which services to look for.


## Documentation
- Build	
- Install	
- User Guide		
    - Setup		
    - GUI		
    - Issues	
- Dev


## Development 
### Work in progress
- A system for creating backups. 
    - Plug in another OS image SD card and you get a duplicate for storing somewhere secure or to use on a second device
- Script for automating dummy user creation
    - Plus script to update modified date on user files at random times while device is on (so real users don't always have latest modified date!) 
- Local web interface that can be run in OS. With this users can plug in HDMI display and peripherals to access logins
- UI improvements for oled display 
    - A search filter on browse view
- Configs in one file
- Quick start guide
    - Setup script
    - Brief hardware reference diagram 

### Future development 
- V2 Device hardware
    - Bigger touch screen LCD display 
    - Touch input in place of keypad 
    - More compact 
    - PIC as HID. This would make make it harder for an adversary (who had physical access to the device) setting up a key logger. The arduino can be programmed via USB by simply pulling the programing pin down



<!-- 
TODO

- Bug fixes
    - Format drive script no good, messes up fstab
    - Send capslock state off to computer on transmit? as if it's set on the target computer caps will be inverted
    - add indication on send
    - Short press fn key combos rarely works
    - passphrase gen has 1st and last chars missing
    - 'shutting down...' no longer displays (maybe shutdown starts before view has time to render)
    - user and pin not cleared on logout
    - Crash: delete entry, select row of deleted entry



- GUI improvements
    - Make selected view
    - Suggest words while typing to the right
    - Display toggle keys below
    - Remap keypad for chars, 1 is still caps, * symbols, 0 delimiters, # num toggle
    - Set filter in browse
    - Make remove confirmation view

- Backup system
    - GUI, backup/restore key combo, check disk, error no disk/full/corrupt, entries date compare (restore) select/unselect/all, progress
    - Hardware
    - Look into how to prevent rubberducking, format before read?
    - two part failsafe pass phrase, unlocks backed up zips incase system won't work
    - Battery power down watch dog
    - Dead battery warning
    - Obscure with dummy users
    - Files need to have dates modified so wont standout
    - Date system

- Write documentation
    - About device
    - Note keypad uses an extended E.161 ITU-T layout
    - Build
    - Install
    - User Guide
    - Setup
    - GUI
    - Issues
    - Dev
    - Display
    - Highlight selected row
    - toggle, when row already selected, clear
    - Decouple content from implementation -->


<!-- 
browse, * prev, A add, # next, C+*(hold) lock

view, A+# edit, B back to browse, if selected row C+# transmit, else D+*(hold) delete

edit, if selected row, A gen, B backspace, D done, else, C cancel, D save



readme

setup
- make raspberry pi lite card
    - Download
    - Unzip
    - Make image
- sudo raspi-config
    - Interface Options: I2C, enable
    - interface options: Serial, no to shell access, enable
    - System Options: Boot / Auto Login, B2 Console Autologin
- sudo apt install python3-pip
- pip3 install -r requirements.txt
-   Upgrade cryptography version sudo pip3 install cryptography --upgrade
- follow setup on https://luma-oled.readthedocs.io
    - If you get ImportError: libopenjp2.so.7...
        - sudo apt install libopenjp2-7-dev
        - w



- config uart
 -->
