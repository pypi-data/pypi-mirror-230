import os
import struct


def is_debuggable_binary(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        print(f"File '{filepath}' does not exist.")
        return False

    # Read the first 4 bytes of the file to check for the Mach-O magic number
    with open(filepath, 'rb') as file:
        magic_number = file.read(4)
    
    if magic_number != b'\xFE\xED\xFA\xCE' and magic_number != b'\xCE\xFA\xED\xFE':
        print(f"File '{filepath}' is not a Mach-O binary.")
        return False

    # Extract the number of load commands
    with open(filepath, 'rb') as file:
        file.seek(16)
        num_load_commands = struct.unpack('I', file.read(4))[0]

    # Read the load commands to find the LC_DYSYMTAB
    with open(filepath, 'rb') as file:
        file.seek(32)
        for _ in range(num_load_commands):
            cmd = struct.unpack('I', file.read(4))[0]
            cmdsize = struct.unpack('I', file.read(4))[0]

            if cmd == 0xb:  # LC_DYSYMTAB
                file.seek(12, 1)  # Skip the indirect symbol table offset, number of indirect symbol table entries, and other fields
                flags = struct.unpack('I', file.read(4))[0]

                if flags & 0x2:  # Check if the flag for stripped symbols is not set
                    return True  # Debug info section found
                else:
                    return False  # Debug info section not found

    return False  # Debug info section not found


# Usage example
executable_path = 'a.out' # /path/to/executable'  # Replace with the actual path to the executable
is_debuggable = is_debuggable_binary(executable_path)
print(f"Is the executable debuggable? {is_debuggable}")
