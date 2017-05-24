# assigns values to opcodes. Acts as a enumerator
from enum import IntEnum

class Opcodes(IntEnum):
    # various opcodes
    push = 1
    pushi = 2
    halt = 3
    pop = 4
    print_int = 5
    print_char = 6
    print_bool = 7
    print_real = 8
    newline = 9
    logical_not = 10
    add = 11
    xchg = 12
    cvr = 13
    fadd = 14
    sub = 15
    fsub = 16
    divide = 17
    multiply = 18
    fmultiply = 19
    logical_or = 20
    greater_than = 21
    less_than = 22
    equal = 23
    not_equal = 24
    gte = 25
    lte = 26
    jfalse = 27
    jump = 28
    put = 29
    get = 30
    array_print = 31


arth_op = {
    "addition": Opcodes.add,
    "faddition": Opcodes.fadd,
    "fsubtraction": Opcodes.fsub,
    "subtraction": Opcodes.sub,
    "multiplication": Opcodes.multiply,
    "fmultiplication": Opcodes.fmultiply,
    "division": Opcodes.divide,
    "fdivision": Opcodes.divide,
}

comp_op = {
    "equal": Opcodes.equal,
    "not_equal": Opcodes.not_equal,
    "less_than": Opcodes.less_than,
    "greater_than": Opcodes.greater_than,
    "lte": Opcodes.lte,
    "gte": Opcodes.gte
}


# ###############################################################################################################
# Takes a 4 byte value, and returns the actual value. Undoes what decompress_bytes() function does
# Returns the original value of a 4 byte value
def decompress_bytes(packed_vals):
    shift_one = packed_vals[0] << 24
    shift_two = packed_vals[1] << 16
    shift_three = packed_vals[2] << 8
    shift_four = packed_vals[3] << 0

    return shift_one | shift_two | shift_three | shift_four


# ###############################################################################################################
# Takes a value and stores it in 4 bytes
# Returns: A 4 byte version of a value
def compress_bytes(starting_value):
    "Extends intial_val to 4 bytes so that it can be stored in the byte array"
    starting_value = int(starting_value)

    shift_one = starting_value >> 24
    shift_two = starting_value >> 16
    shift_three = starting_value >> 8
    shift_four = starting_value >> 0

    f = 0xFF

    return shift_one & f, shift_two & f, shift_three & f, shift_four & f
