# ECTweaker
ECTweaker Library for python allows users to read/write and control the EC of laptops, specially MSI!

# INSTALLATION
pip install ECTweaker

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
- ```ECT.byte_interpreter(NAME, VALUE)``` - Only for MSI Laptops where instead of BYTE you enter NAME and that NAME is hard coded to a BYTE of knows address. This was done to ensure no accidental write to wrong BYTE by mispelling them. Some of the examples are.
  - These are the variables denoting FAN SPEED at set temperatures
  -   NAME    - BYTE
  - CPU_FAN_1 - 0x72
  - CPU_FAN_2 - 0x73
  - CPU_FAN_3 - 0x74
  - CPU_FAN_4 - 0x75
  - CPU_FAN_5 - 0x76
  - CPU_FAN_6 - 0x77
  - CPU_FAN_7 - 0x78
  - GPU_FAN_1 - 0x8a
  - GPU_FAN_2 - 0x8b
  - GPU_FAN_3 - 0x8c
  - GPU_FAN_4 - 0x8d
  - GPU_FAN_5 - 0x8e
  - GPU_FAN_6 - 0x8f
  - GPU_FAN_7 - 0x90

# Future Road map
- Will add support of more BYTE in ```ECT.byte_interpreter(NAME, VALUE)``` and also more vendors
