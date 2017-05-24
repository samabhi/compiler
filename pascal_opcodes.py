# assigns values to opcodes. Acts as a enumerator
class Opcodes(object):

    #various opcodes
    push, pushi, halt, pop, print_int, print_char, print_bool, print_real, newline, logical_not,\
        add, xchg, cvr, fadd, sub, fsub, divide, multiply, fmultiply, logical_or, greater_than, less_than,\
        equal, not_equal, gte, lte, jfalse, jump, put, get, array_print = range(31)


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

