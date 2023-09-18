# ECTweaker
ECTweaker Library for python allows users to read/write and control the EC of laptops, specially MSI!

# INSTALLATION
- pip install ectweaker
  - If the above method doesn't work please install in a virtual environment and call it in scripts from the virtual environments only!

# Preparing the EC to be read/write friendly
- Disable secure boot
- in your script which you create after importing this library, add the below code to check weather EC read/write is enable properly
```
import os
CHECK = ECT.check()
if CHECK != 1:
    your_script
else:
    os.system("shutdown -r +1")
    print("Rebooting system within 1 min!\nPlease save all work before it happens!")
```
- Remember to initiate your script EC read/write after this code has done the checks!
 - To check one of the example to use this code properly, visit https://github.com/YoCodingMonster/OpenFreezeCenter-Lite/tree/main and check ```OpenFreezeCenter-Lite.py``` file

# Updating 
- pip install ECTweaker --upgrade

# How it works
- While using this library, Please run the script with sudo privileges and remember to ```disable secure boot``` from bios for this lib to work!
- ```import ECTweaker as ECT```
- ```ECT.check()``` - This prepare the OS for EC read/write functionality and reboots the system for the first time only!
- ```ECT.write(BYTE ADDRESS, VALUE)``` - This will allow you to write any INTEGER value to BYTE ADDRESS.
- ```VALUE = ECT.read(BYTE ADDRESS)``` - This will allow you to read INTEGER value from BYTE ADDRESS.
- ```ECT.fan_profile(PROFILE, VALUES)``` - This allows for MSI laptops with intel CPU to set Fan profiles.
- ```ECT.speed_writer(VALUES)``` - Internal function used by ```fan_profile``` function.

# Future Road map
- Will add support of more BYTE in ```ECT.byte_interpreter(NAME, VALUE)``` and also more vendors
