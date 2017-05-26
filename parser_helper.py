def check_int_real(data1, data2):
    if data1 == "TK_INTEGER" and data2 == "TK_REAL":
        return True
    else:
        return False


def check_real_int(data1, data2):
    if data1 == "TK_REAL" and data2 == "TK_INTEGER":
        return True
    else:
        return False


def check_real_real(data1, data2):
    if data1 == "TK_REAL" and data2 == "TK_REAL":
        return True
    else:
        return False


def check_int_int(data1, data2):
    if data1 == "TK_INTEGER" and data2 == "TK_INTEGER":
        return True
    else:
        return False


def check_data(data1, data2):
    if data1 == data2:
        return True
    else:
        return False


def get_type(data_type):
    if data_type == "TK_INTEGER":
        return data_type
    elif data_type == "TK_BOOL":
        return data_type
    elif data_type == "TK_CHAR":
        return data_type
    elif data_type == "TK_STRING":
        return data_type
    elif data_type == "TK_REAL":
        return data_type
    elif data_type == "TK_ARRAY":
        return data_type
    else:
        raise TypeError("Invalid Type: " + Parser.curr_t[1])
