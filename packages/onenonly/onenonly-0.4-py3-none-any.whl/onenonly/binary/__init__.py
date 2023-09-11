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
