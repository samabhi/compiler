# -*- pascal_opcodes.py -*-
# Assigns values to opcodes
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
def decompress_bytes(compressed_version):
    """
    Parameters:
                * compressed_version - a four byte number
    :rtype: The initial value of the four bit op
    """
    shift_one = compressed_version[0] << 24
    shift_two = compressed_version[1] << 16
    shift_three = compressed_version[2] << 8
    shift_four = compressed_version[3] << 0

    return shift_one | shift_two | shift_three | shift_four


# ###############################################################################################################
def compress_bytes(initial):
    """
    Parameters:
                * packed_vals - a four byte number
    :rtype: A compress 4 bit value of the initial
    """
    shift_one = int(initial) >> 24
    shift_two = int(initial) >> 16
    shift_three = int(initial) >> 8
    shift_four = int(initial) >> 0

    f = 0xFF

    return shift_one & f, shift_two & f, shift_three & f, shift_four & f
