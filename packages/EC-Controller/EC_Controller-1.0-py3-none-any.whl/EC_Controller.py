#! /usr/bin/python3

EC_IO_FILE = '/sys/kernel/debug/ec/ec0/io'

# Universal EC Byte writing

def write(BYTE, VALUE):
    with open(EC_IO_FILE,'w+b') as file:
        file.seek(BYTE)
        file.write(bytes((VALUE,)))

# Universal EC Byte reading

def read(BYTE):
    with open(EC_IO_FILE,'r+b') as file:
        file.seek(BYTE)
        VALUE = int(file.read(1).hex(),16)
    return VALUE

# Specific for known MSI laptops only!

def byte_interpretter(BYTE, VALUE):
    if VALUE < 0:
        VALUE = 0
    if VALUE > 150:
        VALUE = 150
    
    # Setting up fan profiles
    
    if BYTE == "auto":
        write(0xf4, 12)
        write(0x98, 0)
    if BYTE == "basic" | BYTE == "advanced":
        write(0xf4, 140)
        write(0x98, 0)
    if BYTE == "cooler booster":
        VALUE = read(0x98)
        if VALUE == 128:
            write(0x98, 0)
        else:
            write(0x98, 128)
            
    # Setting up indivisual bytes
        # Setting up indivisual CPU FAN SPEED bytes

    if BYTE == "CPU_FAN_1":
        write(0x72, VALUE)
    if BYTE == "CPU_FAN_2":
        write(0x73, VALUE)
    if BYTE == "CPU_FAN_3":
        write(0x74, VALUE)
    if BYTE == "CPU_FAN_4":
        write(0x75, VALUE)
    if BYTE == "CPU_FAN_5":
        write(0x76, VALUE)
    if BYTE == "CPU_FAN_6":
        write(0x77, VALUE)
    if BYTE == "CPU_FAN_7":
        write(0x78, VALUE)

        # Setting up indivisual GPU FAN SPEED bytes

    if BYTE == "GPU_FAN_1":
        write(0x8a, VALUE)
    if BYTE == "GPU_FAN_2":
        write(0x8b, VALUE)
    if BYTE == "GPU_FAN_3":
        write(0x8c, VALUE)
    if BYTE == "GPU_FAN_4":
        write(0x8d, VALUE)
    if BYTE == "GPU_FAN_5":
        write(0x8e, VALUE)
    if BYTE == "GPU_FAN_6":
        write(0x8f, VALUE)
    if BYTE == "GPU_FAN_7":
        write(0x90, VALUE)