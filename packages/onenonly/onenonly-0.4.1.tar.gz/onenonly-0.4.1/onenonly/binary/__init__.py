def int2bin(integer_value):
    if integer_value == 0:
        return ""
    binary_str = ""
    while integer_value > 0:
        remainder = integer_value % 2
        binary_str = str(remainder) + binary_str
        integer_value //= 2
    return binary_str

def bin2int(binary_str):
    result = 0
    for digit in binary_str:
        if digit == "1":
            result = result*2+1
        elif digit == "0":
            result = result*2
        else:
            raise ValueError("Input is not a binary string")
    return result

def str2bin(text):
    binary = ""
    for char in text:
        ascii_value = ord(char)
        binary_char = bin(ascii_value)[2:].zfill(8)
        binary += binary_char+" "
    return binary

def bin2str(binary_str):
    binary_str = binary_str.replace(" ","")
    binary_segments = [binary_str[i:i+8] for i in range(0,len(binary_str),8)]
    decimal_values = [int(segment,2) for segment in binary_segments]
    result = "".join([chr(value) for value in decimal_values])
    return result

def bin2oct(binary_str):
    while len(binary_str) % 3 != 0:
        binary_str = "0" + binary_str
    binary_to_octal_dict = {
        "000": "0",
        "001": "1",
        "010": "2",
        "011": "3",
        "100": "4",
        "101": "5",
        "110": "6",
        "111": "7"
    }
    octal = ""
    i = 0
    while i < len(binary_str):
        octal += binary_to_octal_dict[binary_str[i:i+3]]
        i += 3
    return octal

def bin2hex(binary_str):
    while len(binary_str) % 4 != 0:
        binary_str = "0" + binary_str
    binary_to_hex_dict = {
        "0000": "0",
        "0001": "1",
        "0010": "2",
        "0011": "3",
        "0100": "4",
        "0101": "5",
        "0110": "6",
        "0111": "7",
        "1000": "8",
        "1001": "9",
        "1010": "A",
        "1011": "B",
        "1100": "C",
        "1101": "D",
        "1110": "E",
        "1111": "F"
    }
    hexadecimal = ""
    i = 0
    while i < len(binary_str):
        hexadecimal += binary_to_hex_dict[binary_str[i:i+4]]
        i += 4
    return hexadecimal
