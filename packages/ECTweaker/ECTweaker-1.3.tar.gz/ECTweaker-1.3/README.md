# ECTweaker
ECTweaker Library for python allows users to read/write and control the EC of laptops, specially MSI!

# INSTALLATION
- pip install ectweaker
  - If the above method doesn't work please install in a virtual environment and call it in scripts from the virtual environments only!

# Preparing the EC to be read/write friendly
- Disable secure boot
- Check weather your Linux Kernal has ```ec_sys``` support
  - If ```no``` then copy the file ```modprobe.d/ec_sys.conf``` and ```modules-lode.d/ec_sys.conf``` to [SYSTEM]```etc/modprobe.d/``` and ```etc/modules-load.d/```, then restart
  - If ```yes``` then add ```ec_sys write_support = 1``` line in file ```/etc/default/grub```, save and in terminal run command ```update-grub``` then reboot

# Updating 
- pip install ECTweaker --upgrade

# How it works
- While using this library, Please run the script with sudo privileges.
- ```import ECTweaker as ECT```
- ```ECT.write(BYTE ADDRESS, VALUE)``` - This will allow you to write any INTEGER value to BYTE ADDRESS.
- ```VALUE = ECT.read(BYTE ADDRESS)``` - This will allow you to read INTEGER value from BYTE ADDRESS.
- ```ECT.fan_profile(PROFILE, VALUES)``` - This allows for MSI laptops with intel CPU to set Fan profiles.
- ```ECT.speed_writer(VALUES)``` - Internal function used by ```fan_profile``` function.

# Future Road map
- Will add support of more BYTE in ```ECT.byte_interpreter(NAME, VALUE)``` and also more vendors
