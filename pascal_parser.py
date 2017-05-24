# -*- pascal_parser.py -*-
# Generates machine code from each of the user program instructions

from pascal_opcodes import Opcodes, compress_bytes, arth_op, comp_op
from symbol import Symbol
import auxiliary_parser_functions as Aux
from keywords import comparison_operators_list


class Parser(object):
    def __init__(self, tokens):

        self.clues_list = tokens
        self.clues_array_index = 0
        self.instruction_indicator = 0
        self.data_indicator = 0
        self.bytes_list = bytearray(1000)
        self.symbol_table = []

        self.current_token = self.clues_list[self.clues_array_index]
        self.clues_array_index += 1

    # ####################################################################################

    def begin(self):
        # Parameters : None

        # check for comments at the beginning of the file
        while self.current_token[1] == "TK_COMMENT":
            self.match("TK_COMMENT")

        # check for basic pascal program syntax of 'begin' and 'end.'
        self.match("TK_BEGIN")
        self.statements()
        self.match("TK_END")
        self.match("TK_DOT")
        self.match("TK_EOF")
        self.make_opcode(Opcodes.halt)

    def start_parser(self):
        # Parameters : None

        # Checks for the starting syntax of a pascal program
        self.match("TK_PROGRAM")
        self.match("TK_ID")
        self.match("TK_SEMICOLON")

        # if file has variable declarations then call declare_var
        if self.current_token[1] == "TK_VAR":
            self.declare_var()
        else:
            self.begin()

        return self.bytes_list

    # ################################################################################################

    # Statement Handler Functions

    # ################################################################################################

    def case_state(self):
        self.match("TK_CASE")
        self.match("TK_LEFT_PAR")
        checker = self.current_token
        exp_1 = self.expr()
        if exp_1 == "TK_REAL":
            raise TypeError('REAL not accepted here')
        self.match("TK_RIGHT_PAR")
        self.match("TK_OF")
        hole_list = []
        while (self.current_token[1] == "TK_INTEGER" or
                       self.current_token[1] == "TK_CHAR" or
                       self.current_token[1] == "TK_BOOL"):
            exp_2 = self.expr()
            self.emit("TK_EQUAL", exp_1, exp_2)
            self.match("TK_COLON")

            self.make_opcode(Opcodes.jfalse)
            hole = self.instruction_indicator
            self.make_address(0)
            self.statements()

            self.make_opcode(Opcodes.jump)
            hole_list.append(self.instruction_indicator)
            self.make_address(0)

            save = self.instruction_indicator
            self.instruction_indicator = hole
            self.make_address(save)
            self.instruction_indicator = save
            if self.current_token[1] != "TK_END":
                symbol = self.find_name(checker[0])
                if symbol is not None:
                    self.make_opcode(Opcodes.push)
                    self.make_address(symbol.data_indicator)

        self.match("TK_END")
        self.match("TK_SEMICOLON")
        save = self.instruction_indicator
        for hole in hole_list:
            self.instruction_indicator = hole
            self.make_address(save)
        self.instruction_indicator = save

    def forloop_state(self):
        self.match("TK_FOR")
        value_of = self.current_token[0]
        self.statements()
        target = self.instruction_indicator
        symbol = self.find_name(value_of)

        self.match("TK_TO")
        self.make_opcode(Opcodes.push)
        self.make_address(symbol.data_indicator)
        self.make_opcode(Opcodes.pushi)
        self.make_address(self.current_token[0])
        self.make_opcode(Opcodes.lte)
        self.match("TK_INTEGER")
        self.match("TK_DO")
        self.make_opcode(Opcodes.jfalse)
        hole = self.instruction_indicator
        self.make_address(0)

        self.match("TK_BEGIN")
        self.statements()
        self.match("TK_END")
        self.match("TK_SEMICOLON")

        self.make_opcode(Opcodes.push)
        self.make_address(symbol.data_indicator)
        self.make_opcode(Opcodes.pushi)
        self.make_address(1)
        self.make_opcode(Opcodes.add)
        self.make_opcode(Opcodes.pop)
        self.make_address(symbol.data_indicator)
        self.make_opcode(Opcodes.jump)
        self.make_address(target)
        save = self.instruction_indicator
        self.instruction_indicator = hole
        self.make_address(save)
        self.instruction_indicator = save

    def ifelse_state(self):
        self.match("TK_IF")
        self.condition()
        self.match("TK_THEN")
        self.make_opcode(Opcodes.jfalse)
        h_one = self.instruction_indicator
        self.make_address(0)
        self.statements()
        if self.current_token[1] == "TK_ELSE":
            self.make_opcode(Opcodes.jump)
            h_two = self.instruction_indicator
            self.make_address(0)
            save = self.instruction_indicator
            self.instruction_indicator = h_one
            self.make_address(save)
            self.instruction_indicator = save
            h_one = h_two
            self.match("TK_ELSE")
            self.statements()
        save = self.instruction_indicator
        self.instruction_indicator = h_one
        self.make_address(save)
        self.instruction_indicator = save

    def whileloop_state(self):
        self.match("TK_WHILE")
        target = self.instruction_indicator
        self.condition()
        self.match("TK_DO")

        self.match("TK_BEGIN")
        self.make_opcode(Opcodes.jfalse)
        hole = self.instruction_indicator
        self.make_address(0)

        self.statements()

        self.make_opcode(Opcodes.jump)
        self.make_address(target)

        save = self.instruction_indicator
        self.instruction_indicator = hole
        self.make_address(save)
        self.instruction_indicator = save

        self.match("TK_END")
        self.match("TK_SEMICOLON")

    def controlrepeat_state(self):
        self.match("TK_REPEAT")
        target = self.instruction_indicator
        self.statements()
        self.match("TK_UNTIL")
        self.condition()
        self.make_opcode(Opcodes.jfalse)
        self.make_address(target)

    def write_line(self):
        self.match("TK_WRITELN")
        self.match("TK_LEFT_PAR")

        while True:
            if self.current_token[1] == "TK_ID":
                symbol = self.find_name(self.current_token[0])
                if hasattr(symbol, "assignment_type"):
                    self.match("TK_ID")
                    self.access_array(symbol)
                    self.make_opcode(Opcodes.array_print)
                    continue
                else:
                    dt_1 = self.expr()
                if dt_1 == "TK_INTEGER":
                    self.make_opcode(Opcodes.print_int)
                    self.make_address(symbol.data_indicator)
                elif dt_1 == "TK_ARRAY":
                    self.make_opcode(Opcodes.get)
                elif dt_1 == "TK_REAL":
                    self.make_opcode(Opcodes.print_real)
                    self.make_address(symbol.data_indicator)
                else:
                    raise TypeError("Not supported")
            if self.current_token[1] == "TK_COMMA":
                self.match("TK_COMMA")
            elif self.current_token[1] == "TK_RIGHT_PAR":
                self.match("TK_RIGHT_PAR")
                self.make_opcode(Opcodes.newline)
                return
            else:
                raise SyntaxError("Right parentheses or comma expected.")

    def statements(self):
        while self.current_token[1] != "TK_END":
            if self.current_token[1] == "TK_ID":
                self.assignment_statement()
            elif self.current_token[1] == "TK_SEMICOLON":
                self.match("TK_SEMICOLON")
            elif self.current_token[1] == "TK_COMMENT":
                self.match("TK_COMMENT")
            elif self.current_token[1] == "TK_WRITELN":
                self.write_line()
            elif self.current_token[1] == "TK_REPEAT":
                self.controlrepeat_state()
            elif self.current_token[1] == "TK_WHILE":
                self.whileloop_state()
            elif self.current_token[1] == "TK_IF":
                self.ifelse_state()
            elif self.current_token[1] == "TK_FOR":
                self.forloop_state()
            elif self.current_token[1] == "TK_CASE":
                self.case_state()
            else:
                return

    # #######################################################################################

    # Variable Declaration Functions

    # #######################################################################################

    def declare_var(self):
        self.match("TK_VAR")
        var_list = []

        while self.current_token[1] == "TK_ID":
            if self.current_token not in var_list:
                var_list.append(self.current_token)
                self.match("TK_ID")

                if self.current_token[1] == "TK_COMMA":
                    self.match("TK_COMMA")
            else:
                raise NameError("Variable already declared" + self.current_token[1])

        self.match("TK_COLON")

        if self.current_token[1] == "TK_INTEGER":
            data_type = self.current_token[1]
            self.match("TK_INTEGER")
        elif self.current_token[1] == "TK_BOOL":
            data_type = self.current_token[1]
            self.match("TK_BOOL")
        elif self.current_token[1] == "TK_CHAR":
            data_type = self.current_token[1]
            self.match("TK_CHAR")
        elif self.current_token[1] == "TK_REAL":
            data_type = self.current_token[1]
            self.match("TK_REAL")
        elif self.current_token[1] == "TK_ARRAY":
            data_type = self.current_token[1]
            self.match("TK_ARRAY")
        else:
            raise TypeError("Invalid Type: " + self.current_token[1])

        if data_type == "TK_ARRAY":
            self.match("TK_LEFT_BRACKET")
            access_type, lower_bound, upper_bound = self.get_range_array(self.current_token)
            self.match("TK_RANGE")
            self.match("TK_RIGHT_BRACKET")
            self.match("TK_OF")

            if self.current_token[1] == "TK_INTEGER":
                assignment_type = self.current_token[1]
                self.match("TK_INTEGER")
            elif self.current_token[1] == "TK_REAL":
                assignment_type = self.current_token[1]
                self.match("TK_REAL")
            elif self.current_token[1] == "TK_CHAR":
                assignment_type = self.current_token[1]
                self.match("TK_CHAR")
            elif self.current_token[1] == "TK_BOOL":
                assignment_type = self.current_token[1]
                self.match("TK_BOOL")
            else:
                raise TypeError("Unsupported types: " + self.current_token[1])
            self.match("TK_SEMICOLON")

            for var in var_list:
                s = Symbol(var[0], 'TK_ARRAY', 'ARRAY', self.data_indicator)
                s.access_type = access_type
                s.lower_bound = lower_bound
                s.upper_bound = upper_bound
                s.assignment_type = assignment_type
                self.symbol_table.append(s)
                self.data_indicator += 4 * int(upper_bound) - int(lower_bound)

        else:
            self.match("TK_SEMICOLON")
            for var in var_list:
                var_symbol = Symbol(var[0], data_type, "VARIABLE", self.data_indicator)
                self.data_indicator += 1
                self.symbol_table.append(var_symbol)
            self.data_indicator += 1

        if self.current_token[1] == "TK_VAR":
            self.declare_var()
        else:
            self.begin()

    def get_range_array(self, token):
        """
        Parameters:
                    * token - a token of type array
        :rtype: the access_type, lower bound of the array, upper bound of the array
        """
        if len(token[0].split('..')) != 2:
            raise SyntaxError('Range needs to be like  0..2')
        lower = int(token[0].split('..')[0])
        upper = int(token[0].split('..')[1])
        access_type = "TK_INTEGER"

        return access_type, lower, upper

    # ##############################################################################################

    def factor(self):
        if self.current_token[1] == "TK_INTEGER":
            self.make_opcode(Opcodes.pushi)
            self.make_address(self.current_token[0])
            self.match("TK_INTEGER")
            return "TK_INTEGER"
        elif self.current_token[1] == "TK_ID":
            sym_object = self.find_name(self.current_token[0])

            if sym_object.description == "VARIABLE":
                self.make_opcode(Opcodes.push)
                self.make_address(sym_object.data_indicator)
                self.match("TK_ID")
                return sym_object.data_type
            elif sym_object.description == "ARRAY":
                self.match("TK_ID")
                self.access_array(sym_object)
                self.make_opcode(Opcodes.get)
                return sym_object.assignment_type
        elif self.current_token[1] == "TK_BOOL":
            self.make_opcode(Opcodes.pushi)
            self.make_address(self.current_token[0])
            self.match("TK_BOOL")
            return "TK_BOOL"
        elif self.current_token[1] == "TK_CHAR":
            self.make_opcode(Opcodes.pushi)
            self.make_address(self.current_token[0])
            self.match("TK_CHAR")
            return "TK_CHAR"
        elif self.current_token[1] == "TK_REAL":
            self.make_opcode(Opcodes.pushi)
            self.make_address(self.current_token[0])
            self.match("TK_REAL")
            return "TK_REAL"
        elif self.current_token[1] == "TK_NOT":
            self.make_opcode(Opcodes.logical_not)
            self.match("TK_NOT")
            return self.factor()
        elif self.current_token[1] == "TK_LEFT_PAR":
            self.match("TK_LEFT_PAR")
            left_par = self.expr()
            self.match("TK_RIGHT_PAR")
            return left_par
        else:
            pass

    # #####################################################################################################

    def array_assignment(self, symbol):
        """
        Parameters:
                    * symbol - an array
        :rtype:
        """
        self.access_array(symbol)
        self.match("TK_ASSIGNMENT")
        exp_1 = self.expr()
        if exp_1 == symbol.assignment_type:
            self.make_opcode(Opcodes.put)
        else:
            raise TypeError('Mismatched types: ' + exp_1 + ' and ' + symbol.assignment_type)

    #  ####################################################################################################
    def checkDataTypesForArth(self, datatype_1, datatype_2, operation):
        """
        Parameters:
                    * datatype_1 - the data type of the first operand
                    * datatype_2 - the data type of the second operand
                    * operation - the operation to be evaluated
        :rtype: data type of the result of an operation between datatype_1 and datatype_2
        """
        op_Opcode = arth_op
        if Aux.check_int_int(datatype_1, datatype_2):
            self.make_opcode(op_Opcode.get(operation))
            if (operation == "division"):
                return datatype_1
            else:
                return "TK_INTEGER"
        elif Aux.check_int_real(datatype_1, datatype_2):
            self.make_opcode(Opcodes.xchg,
                             Opcodes.cvr,
                             Opcodes.xchg,
                             op_Opcode.get(str("f" + operation)))
            return "TK_REAL"
        elif Aux.check_real_int(datatype_1, datatype_2):
            self.make_opcode(Opcodes.cvr, op_Opcode.get(str("f" + operation)))
            return "TK_REAL"
        elif Aux.check_real_real(datatype_1, datatype_2):
            if (operation in {"subtraction", "multiplication"}):
                self.make_opcode(op_Opcode.get(str("f" + operation)))
            elif operation == "addition":
                self.make_opcode(op_Opcode.get(operation))
            elif operation == "division":
                raise TypeError(
                    "Error in Divide Operation. Invalid datatypes. Found:" + datatype_1 + " , " + datatype_2)
            return "TK_REAL"

    def checkDataTypesForLogical(self, datatype_1, datatype_2, operation):
        """
        Parameters:
                    * datatype_1 - the data type of the first operand
                    * datatype_2 - the data type of the second operand
                    * operation - the operation to be evaluated
        :rtype: data type of the result of an operation between datatype_1 and datatype_2
        """
        dict_op = comp_op

        if Aux.check_data(datatype_1, datatype_2):
            self.make_opcode(dict_op.get(operation))
        elif Aux.check_int_real(datatype_1, datatype_2):
            self.make_opcode(Opcodes.xchg, Opcodes.cvr, Opcodes.xchg, dict_op.get(operation))
        elif Aux.check_real_int(datatype_1, datatype_2):
            self.make_opcode(Opcodes.cvr, dict_op.get(operation))
        else:
            return None
        return "TK_BOOL"

    def emit(self, operation, datatype_1, datatype_2):
        """
        Parameters:
                    * operation - the operation to be evaluated
                    * datatype_1 - the data type of the first operand
                    * datatype_2 - the data type of the second operand
        :rtype: data type of the result of an operation between datatype_1 and datatype_2
        """
        if operation == "TK_ADD":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="addition")
        elif operation == "TK_SUBTRACT":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="subtraction")
        elif operation == "TK_DIVIDE":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="division")
        elif operation == "TK_DIV":
            if datatype_1 == "TK_INTEGER" and datatype_2 == "TK_INTEGER":
                self.make_opcode(Opcodes.divide)
                return "TK_INT"
        elif operation == "TK_MULTIPLY":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="multiplication")
        elif operation == "TK_OR":
            if datatype_1 == "TK_BOOL" and datatype_2 == "TK_BOOL":
                self.make_opcode(Opcodes.logical_or)
                return "TK_BOOL"
        elif operation == "TK_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "equal")
        elif operation == "TK_NOT_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "not_equal")
        elif operation == "TK_LESS_THAN":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "less_than")
        elif operation == "TK_LESS_THAN_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "lte")
        elif operation == "TK_GREATER_THAN":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "greater_than")
        elif operation == "TK_GREATER_THAN_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "gte")
        else:
            raise TypeError("Emit cannot match datatype. Datatypes found: " + datatype_1 + " , " + datatype_2)

    # ####################################################################################

    # Helper functions

    # ####################################################################################

    def make_opcode(self, *ops):
        for op in ops:
            self.bytes_list[self.instruction_indicator] = op
            self.instruction_indicator += 1

    def make_address(self, target):
        """
        Parameters:
                    * target - something to be stored in 4 bytes
        :rtype:
        """
        bytearray_list = compress_bytes(target)

        for byte in bytearray_list:
            self.bytes_list[self.instruction_indicator] = byte
            self.instruction_indicator += 1

    def find_name(self, label):
        """
        Parameters:
                    * label
        :rtype: a symbol object
        """
        for obj in self.symbol_table:
            if obj.label == label:
                return obj

        return None

    def match(self, tk_):
        """
        Parameters:
                    * tk_ - token type
        :rtype:
        """
        if tk_ == self.current_token[1]:
            if self.current_token[1] != "TK_EOF":
                self.current_token = self.clues_list[self.clues_array_index]
                self.clues_array_index += 1
        else:
            raise IndexError("Doesn't Match" + " " + tk_ + " " + self.current_token[1])

    def condition(self):
        expression = self.expr()

        if self.current_token[1] in comparison_operators_list:
            data_type = self.current_token[1]
            self.match(data_type)
            term2 = self.term()
            expression = self.emit(data_type, expression, term2)
            return expression

        else:
            raise TypeError("Expected condition, not: " + self.current_token[1])

    def expr(self):
        dt_1 = self.term()
        while self.current_token[1] == "TK_ADD" or self.current_token[1] == "TK_SUBTRACT":
            token_op = self.current_token[1]
            self.match(token_op)
            dt_1 = self.emit(token_op, dt_1, self.term())

        return dt_1

    def term(self):
        dt_1 = self.factor()
        while self.current_token[1] == "TK_MULTIPLY" or self.current_token[1] == "TK_DIVIDE":
            token_op = self.current_token[1]
            self.match(token_op)
            dt_1 = self.emit(token_op, dt_1, self.factor())
        return dt_1

    def assignment_statement(self):
        sym_object = self.find_name(self.current_token[0])
        if sym_object:
            left_side = sym_object.data_type

            self.match("TK_ID")

            if self.current_token[1] == "TK_LEFT_BRACKET":
                self.array_assignment(sym_object)
                return

            self.match("TK_ASSIGNMENT")
            right_side = self.expr()

            if left_side == right_side:
                self.make_opcode(Opcodes.pop)
                self.make_address(sym_object.data_indicator)
            else:
                raise TypeError(left_side + ' != ' + right_side)
        else:
            raise NameError("Variable Not Declared: " + self.current_token[0])

    def access_array(self, symbol):
        """
        Parameters:
                    * symbol - the array to be accessed
        :rtype:
        """
        self.match("TK_LEFT_BRACKET")
        current_symbol = self.find_name(self.current_token[0])
        self.make_opcode(Opcodes.push)
        self.make_address(current_symbol.data_indicator)
        self.match("TK_ID")
        self.match("TK_RIGHT_BRACKET")

        self.make_opcode(Opcodes.pushi)

        if current_symbol.data_type == "TK_INTEGER":
            self.make_address(symbol.lower_bound)
            self.make_opcode(Opcodes.xchg)
            self.make_opcode(Opcodes.sub)
            self.make_opcode(Opcodes.pushi)
            self.make_address(4)
            self.make_opcode(Opcodes.multiply)
            self.make_opcode(Opcodes.pushi)
            self.make_address(symbol.data_indicator)
            self.make_opcode(Opcodes.add)

        else:
            raise TypeError('Array does not support:' + current_symbol.data_type)