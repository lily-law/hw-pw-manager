# Hardware Password Manager

#### Video Demo: https://youtu.be/S4_pITpOw2c
#### Description: Hardware password manager with isolated (output only) HID USB interface. 
- Store, index, and generate secure passwords and usernames for services
- More secure and convenient then writing login details down
- Plug in to a USB port, paste entries out through the keyboard emulation hardware
- Portable across systems and at boot time (BIOS passwords, hdd decryption...)
- More secure then online password managers

The keyboard emulator has only a receiving link to the password manager hardware. This ensures your stash of passwords and the password manager OS remain secure even when used on a compromised system (this doesn't prevent a threat from logging passwords that you paste out to the keyboard emulator on compromised systems).

Entries are encrypted on the device by a lock pin. You can create multiple logins. Optionally it allows creation of dummy users which adds some hardening to weaker pins. An adversary would have to break multiple pins as well as knowing which services to look for.

## Why use this 
- To setup access across multiple systems conveniently
- Be in direct control of your stash of credentials
 
## This does not
- Prevent key logging of credentials on comprised systems

## Documentation
- [Build](./documentation/build.md)	
- [Install](./documentation/install.md)	
<!-- - [User Guide](./documentation/user-guide.md)	
    - [Setup](./documentation/user-guide.md/#setup)
    - [GUI](./documentation/user-guide.md/#gui)	
    - [Issues](./documentation/user-guide.md/#issues) -->
- [Development](./documentation/development.md)	

## Dependencies 
- Python3
- PIP3
- cryptography (python built in library)
- [xkcdpass](https://pypi.org/project/xkcdpass/) for passphrase generation

## Summery of files
<details>
    <summary>app.py</summary>
    <ul>
        <li>Controller and state holders</li>
        <li>Handles output from keypad</li>
        <li>Set views on the display via display.py</li>
    </ul>
</details>
<details>
    <summary>disk.py</summary>
    <ul>
        <li>Handles saving data</li>
        <li>Creates and retrieves files for each user using hashing</li>
        <li>Decrypts/encrypts data</li>
    </ul>
</details>
<details>
    <summary>display.py</summary>
    <ul>
        <li>UI views</li>
        <li>Displays output to OLED display</li>
</details>
<details>
    <summary>gen.py</summary>
    <ul>
        <li>Service name generation</li>
        <li>User name generation</li>
        <li>Password generation</li>
    </ul>
</details>
<details>
    <summary>keypad.py</summary>
    <ul>
        <li>Scans keypad matrix for key presses and releases</li>
    </ul>
</details>
<details>
    <summary>output.py</summary>
    <ul>
        <li>Sends strings out through serial port</li>
    </ul>
</details>

