# -*- pascal_simulator.py -*-

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

    # #########################################################################
    def pascal_print_int(self):
        self.orders_indicator += 1
        val = self.unpacker()
        print (self.data_series[val])

    def pascal_print_string(self):
        self.orders_indicator += 1
        val = self.unpacker()
        print (self.data_series[val])

    def pascal_array_print(self):
        self.orders_indicator += 1
        self.data_indicator = self.store.pop()
        print (self.data_series[self.data_indicator])

    def pascal_print_real(self):
        self.orders_indicator += 1
        dp = self.unpacker()
        print (self.store.pop())

    def pascal_newline(self):
        self.orders_indicator += 1

    # #########################################################################

    # Arithmetic Operations

    # #########################################################################

    def pascal_add(self):
        self.orders_indicator += 1
        sum = self.store.pop() + self.store.pop()
        self.store.append(sum)

    def pascal_subtract(self):
        self.orders_indicator += 1
        var1 = self.store.pop()
        var2 = self.store.pop()
        difference = var2 - var1
        self.store.append(difference)

    def pascal_multiply(self):
        self.orders_indicator += 1
        multiplied = self.store.pop() * self.store.pop()
        self.store.append(multiplied)

    def pascal_divide(self):
        self.orders_indicator += 1
        var1 = float(self.store.pop())
        var2 = self.store.pop()
        divided = var2 / var1
        self.store.append(divided)

    # #########################################################################
    
    # Logic Operations
    
    # #########################################################################

    def pascal_less_than(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() > self.store.pop())

    def pascal_greater_than(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() < self.store.pop())

    def pascal_lte(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() >= self.store.pop())

    def pascal_gte(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() <= self.store.pop())

    def pascal_equal(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() == self.store.pop())

    def pascal_not_equal(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop() != self.store.pop())

    # ######################################################################

    # Simulator and helper functions

    # ######################################################################

    def simulator(self):
        opcode = self.bytes_series[self.orders_indicator]
        if opcode == Opcodes.pushi:
            self.pascal_pushi()
        elif opcode == Opcodes.halt:
            return
        elif opcode == Opcodes.push:
            self.pascal_push()
        elif opcode == Opcodes.pop:
            self.pascal_pop()
        elif opcode == Opcodes.print_int:
            self.pascal_print_int()
        elif opcode == Opcodes.newline:
            self.pascal_newline()
        elif opcode == Opcodes.add:
            self.pascal_add()
        elif opcode == Opcodes.sub:
            self.pascal_subtract()
        elif opcode == Opcodes.multiply:
            self.pascal_multiply()
        elif opcode == Opcodes.divide:
            self.pascal_divide()
        elif opcode == Opcodes.less_than:
            self.pascal_less_than()
        elif opcode == Opcodes.greater_than:
            self.pascal_greater_than()
        elif opcode == Opcodes.xchg:
            self.pascal_xchg()
        elif opcode == Opcodes.lte:
            self.pascal_lte()
        elif opcode == Opcodes.gte:
            self.pascal_gte()
        elif opcode == Opcodes.equal:
            self.pascal_equal()
        elif opcode == Opcodes.not_equal:
            self.pascal_not_equal()
        elif opcode == Opcodes.jfalse:
            self.pascal_jump_false()
        elif opcode == Opcodes.jump:
            self.pascal_jump()
        elif opcode == Opcodes.put:
            self.pascal_put()
        elif opcode == Opcodes.get:
            self.pascal_get()
        elif opcode == Opcodes.array_print:
            self.pascal_array_print()
        elif opcode == Opcodes.print_real:
            self.pascal_print_real()
        elif opcode == Opcodes.cvr:
            self.pascal_cvr()
        else:
            print ("Does not currently support", opcode)
            return

        self.simulator()

    def unpacker(self):
        packed_bytes = bytearray()
        for x in range(4):
            packed_bytes.append(self.bytes_series[self.orders_indicator])
            self.orders_indicator += 1
        return decompress_bytes(packed_bytes)

    def get_data(self):
        data_indicator = self.unpacker()
        return self.data_series[data_indicator]

    # #########################################################################

    # Stack Operations

    # #########################################################################

    def pascal_pushi(self):
        self.orders_indicator += 1
        val = self.unpacker()
        self.store.append(val)

    def pascal_push(self):
        self.orders_indicator += 1
        dp = self.unpacker()
        self.store.append(self.data_series[dp])

    def pascal_pop(self):
        self.orders_indicator += 1
        top_element = self.store.pop()
        self.data_indicator = self.unpacker()
        self.data_series[self.data_indicator] = top_element
        self.data_indicator += 1
        return top_element

    def pascal_put(self):
        self.orders_indicator += 1
        assignment = self.store.pop()
        self.data_indicator = self.store.pop()
        self.data_series[self.data_indicator] = assignment
        self.data_indicator += 1

    def pascal_jump(self):
        self.orders_indicator += 1
        val = self.unpacker()
        self.orders_indicator = val

    def pascal_get(self):
        self.orders_indicator += 1
        self.data_indicator = self.store.pop()
        self.store.append(self.data_series[self.data_indicator])

    def pascal_xchg(self):
        self.orders_indicator += 1
        self.store.append(self.store.pop())
        self.store.append(self.store.pop())

    def pascal_jump_false(self):
        self.orders_indicator += 1

        if self.store.pop():
            self.unpacker()
        else:
            val = self.unpacker()
            self.orders_indicator = val

    def pascal_cvr(self):
        self.orders_indicator += 1
        self.store.append(float(self.store.pop()))
