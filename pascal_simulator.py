# Simulator reads the machine instruction in the byte array and executes it
from pascal_opcodes import Opcodes, decompress_bytes


class Simulator(object):
    # Constructor
    def __init__(self, bytes):
        self.data_indicator = 0
        self.orders_indicator = 0
        self.store = []
        self.bytes_series = bytes
        self.standard_result = []
        self.data_series = {}
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  prints an integer
    # Returns: Nothing
    def pascal_print_int(self):
        self.orders_indicator += 1
        val = self.unpacker()
        print (self.data_series[val]),

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  prints a new line character
    # Returns: Nothing
    def pascal_newline(self):
        self.orders_indicator += 1
        #print ("\n"),

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_add(self):
        self.orders_indicator += 1
        sum = self.store.pop() + self.store.pop()
        self.store.append(sum)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_subtract(self):
        self.orders_indicator += 1
        var1 = self.store.pop()
        var2 = self.store.pop()
        difference = var2 - var1
        self.store.append(difference)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_multiply(self):
        self.orders_indicator += 1
        multiplied = self.store.pop() * self.store.pop()
        self.store.append(multiplied)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_divide(self):
        self.orders_indicator += 1
        var1 = float(self.store.pop())
        var2 = self.store.pop()
        divided = var2 / var1
        self.store.append(divided)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_less_than(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() < self.store.pop())

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_greator_than(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() > self.store.pop())

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_lte(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() >= self.store.pop())

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_gte(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() <= self.store.pop())

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_equal(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() == self.store.pop())

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_not_equal(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() != self.store.pop())

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_jump_false(self):
        self.orders_indicator += 1

        if self.store.pop():
            self.unpacker()
        else:
            val = self.unpacker()
            self.orders_indicator = val

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Returns: Nothing
    def pascal_jump(self):
        self.orders_indicator += 1
        val = self.unpacker()
        self.orders_indicator = val

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_put(self):

        self.orders_indicator += 1
        assignment = self.store.pop()
        self.data_indicator = self.store.pop()
        self.data_series[self.data_indicator] = assignment
        self.data_indicator += 1

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_get(self):

        self.orders_indicator += 1
        self.data_indicator = self.store.pop()
        self.store.append(self.data_series[self.data_indicator])

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_array_print(self):
        self.orders_indicator += 1
        self.data_indicator = self.store.pop()
        print (self.data_series[self.data_indicator]),

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Returns: Nothing
    def pascal_xchg(self):
        self.orders_indicator += 1
        top = self.store.pop()
        bottom = self.store.pop()
        self.store.append(top)
        self.store.append(bottom)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Returns: Nothing
    def pascal_print_real(self):
        self.orders_indicator += 1
        dp = self.unpacker()
        print (self.store.pop()),

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Returns: Nothing
    def pascal_cvr(self):
        self.orders_indicator += 1
        self.store.append(float(self.store.pop()))


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  starts the simulator. Checks for type of opcode and calls the appropriate method

    def start_simulator(self):
        opcode = self.bytes_series[self.orders_indicator]
        if opcode == Opcodes.pushi:
            self.pascal_pushi()
            self.start_simulator()
        elif opcode == Opcodes.halt:
            return
        elif opcode == Opcodes.push:
            self.pascal_push()
            self.start_simulator()
        elif opcode == Opcodes.pop:
            self.pascal_pop()
            self.start_simulator()
        elif opcode == Opcodes.print_int:
            self.pascal_print_int()
            self.start_simulator()
        elif opcode == Opcodes.newline:
            self.pascal_newline()
            self.start_simulator()
        elif opcode == Opcodes.add:
            self.pascal_add()
            self.start_simulator()
        elif opcode == Opcodes.sub:
            self.pascal_subtract()
            self.start_simulator()
        elif opcode == Opcodes.multiply:
            self.pascal_multiply()
            self.start_simulator()
        elif opcode == Opcodes.divide:
            self.pascal_divide()
            self.start_simulator()
        elif opcode == Opcodes.less_than:
            self.pascal_less_than()
            self.start_simulator()
        elif opcode == Opcodes.greater_than:
            self.pascal_greator_than()
            self.start_simulator()
        elif opcode == Opcodes.xchg:
            self.pascal_xchg()
            self.start_simulator()
        elif opcode == Opcodes.lte:
            self.pascal_lte()
            self.start_simulator()
        elif opcode == Opcodes.gte:
            self.pascal_gte()
            self.start_simulator()
        elif opcode == Opcodes.equal:
            self.pascal_equal()
            self.start_simulator()
        elif opcode == Opcodes.not_equal:
            self.pascal_not_equal()
            self.start_simulator()
        elif opcode == Opcodes.jfalse:
            self.pascal_jump_false()
            self.start_simulator()
        elif opcode == Opcodes.jump:
            self.pascal_jump()
            self.start_simulator()
        elif opcode == Opcodes.put:
            self.pascal_put()
            self.start_simulator()
        elif opcode == Opcodes.get:
            self.pascal_get()
            self.start_simulator()
        elif opcode == Opcodes.array_print:
            self.pascal_array_print()
            self.start_simulator()
        elif opcode == Opcodes.print_real:
            self.pascal_print_real()
            self.start_simulator()
        elif opcode == Opcodes.cvr:
            self.pascal_cvr()
            self.start_simulator()
        else:
            print ("Does not currently support", opcode),
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  will take the 4 bytes from the instruction and convert it into one number
    # Return: the integer
    def unpacker(self):
        packed_bytes = bytearray()
        for x in range(4):
            packed_bytes.append(self.bytes_series[self.orders_indicator])
            self.orders_indicator += 1
        return decompress_bytes(packed_bytes)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  gets the immediate, and accesses the data_series to get the value of a identifier
    # Returns: a value from the data array
    def get_data(self):
        data_indicator = self.unpacker()
        return self.data_series[data_indicator]

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  pushes the immediate value onto the store
    # Returns: Nothing
    def pascal_pushi(self):
        self.orders_indicator += 1
        val = self.unpacker()
        self.store.append(val)

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  takes the immediate address and pushes the value from the data array onto the store
    # Returns: Nothing
    def pascal_push(self):
        self.orders_indicator += 1
        dp = self.unpacker()
        self.store.append(self.data_series[dp])

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Assign the top element to the address specified by self.unpacker()
    # Returns: Nothing
    def pascal_pop(self):
        self.orders_indicator += 1

        top_element = self.store.pop()

        self.data_indicator = self.unpacker()

        self.data_series[self.data_indicator] = top_element

        self.data_indicator += 1

        return top_element
