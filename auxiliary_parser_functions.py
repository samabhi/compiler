def check_int_real(data1,data2):
    if data1 == "TK_INTEGER" and data2 == "TK_REAL":
        return True
    else:
        return False

def check_real_int(data1,data2):
    if data1 == "TK_REAL" and data2 == "TK_INTEGER":
        return True
    else:
        return False
def check_real_real(data1,data2):
    if data1 == "TK_REAL" and data2 == "TK_REAL":
        return True
    else:
        return False
def check_int_int(data1,data2):
    if data1 == "TK_INTEGER" and data2 == "TK_INTEGER":
        return True
    else:
        return False
def check_data(data1,data2):
    if data1 == data2:
        return True
    else:
        return False
