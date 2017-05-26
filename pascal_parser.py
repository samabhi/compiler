# -*- pascal_parser.py -*-
# Generates machine code from each of the user program instructions

from pascal_opcodes import Opcodes, compress_bytes, arth_op, comp_op
from symbol import Symbol
import parser_helper as Aux
from keywords import comparison_operators_list


class Parser(object):
    def __init__(self, tokens):

        self.t_lst = tokens
        self.t_index = 0
        self.instruction_indicator = 0
        self.data_indicator = 0
        self.bytes_list = bytearray(1000)
        self.symbol_table = []

        self.curr_t = self.t_lst[self.t_index]
        self.t_index += 1

    # ####################################################################################

    def begin(self):
        # Parameters : None

        # check for comments at the beginning of the file
        while self.curr_t[1] == "TK_COMMENT":
            self.match("TK_COMMENT")

        # check for basic pascal program syntax of 'begin' and 'end.'
        self.match("TK_BEGIN")
        self.statements()
        self.match("TK_END")
        self.match("TK_DOT")
        self.match("TK_EOF")
        self.gen_opcode(Opcodes.halt)

    def start_parser(self):
        # Parameters : None

        # Checks for the starting syntax of a pascal program
        self.match("TK_PROGRAM")
        self.match("TK_ID")
        self.match("TK_SEMICOLON")

        # if file has variable declarations then call declare_var
        if self.curr_t[1] == "TK_VAR":
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
        verification = self.curr_t
        exp_1 = self.expr()
        if exp_1 == "TK_REAL":
            raise TypeError('REAL not accepted here')
        self.match("TK_RIGHT_PAR")
        self.match("TK_OF")
        instruction_list = []
        while (self.curr_t[1] == "TK_INTEGER" or
                       self.curr_t[1] == "TK_CHAR" or
                       self.curr_t[1] == "TK_BOOL"):
            exp_2 = self.expr()
            self.emit("TK_EQUAL", exp_1, exp_2)
            self.match("TK_EQUAL")

            self.gen_opcode(Opcodes.jfalse)
            instruc = self.instruction_indicator
            self.gen_address(0)
            self.statements()

            self.gen_opcode(Opcodes.jump)
            instruction_list.append(self.instruction_indicator)
            self.gen_address(0)

            save = self.instruction_indicator
            self.instruction_indicator = instruc
            self.gen_address(save)
            self.instruction_indicator = save
            if self.curr_t[1] != "TK_END":
                symbol = self.find_name(verification[0])
                if symbol is not None:
                    self.gen_opcode(Opcodes.push)
                    self.gen_address(symbol.data_indicator)

        self.match("TK_END")
        self.match("TK_SEMICOLON")
        save = self.instruction_indicator
        for instruc in instruction_list:
            self.instruction_indicator = instruc
            self.gen_address(save)
        self.instruction_indicator = save

    def forloop_state(self):
        self.match("TK_FOR")
        value_of = self.curr_t[0]
        self.statements()
        target = self.instruction_indicator
        symbol = self.find_name(value_of)

        self.match("TK_TO")
        self.gen_opcode(Opcodes.push)
        self.gen_address(symbol.data_indicator)
        self.gen_opcode(Opcodes.pushi)
        self.gen_address(self.curr_t[0])
        self.gen_opcode(Opcodes.lte)
        self.match("TK_INTEGER")
        self.match("TK_DO")
        self.gen_opcode(Opcodes.jfalse)
        instruc = self.instruction_indicator
        self.gen_address(0)

        self.match("TK_BEGIN")
        self.statements()
        self.match("TK_END")
        self.match("TK_SEMICOLON")

        self.gen_opcode(Opcodes.push)
        self.gen_address(symbol.data_indicator)
        self.gen_opcode(Opcodes.pushi)
        self.gen_address(1)
        self.gen_opcode(Opcodes.add)
        self.gen_opcode(Opcodes.pop)
        self.gen_address(symbol.data_indicator)
        self.gen_opcode(Opcodes.jump)
        self.gen_address(target)
        save = self.instruction_indicator
        self.instruction_indicator = instruc
        self.gen_address(save)
        self.instruction_indicator = save

    def ifelse_state(self):
        self.match("TK_IF")
        self.condition()
        self.match("TK_THEN")
        self.gen_opcode(Opcodes.jfalse)
        iftrue_instruction = self.instruction_indicator
        self.gen_address(0)
        self.statements()
        if self.curr_t[1] == "TK_ELSE":
            self.gen_opcode(Opcodes.jump)
            else_instruction = self.instruction_indicator
            self.gen_address(0)
            save = self.instruction_indicator
            self.instruction_indicator = iftrue_instruction
            self.gen_address(save)
            self.instruction_indicator = save
            iftrue_instruction = else_instruction
            self.match("TK_ELSE")
            self.statements()
        save = self.instruction_indicator
        self.instruction_indicator = iftrue_instruction
        self.gen_address(save)
        self.instruction_indicator = save

    def whileloop_state(self):
        self.match("TK_WHILE")
        validation = self.instruction_indicator
        self.condition()
        self.match("TK_DO")

        self.match("TK_BEGIN")
        self.gen_opcode(Opcodes.jfalse)
        instruction = self.instruction_indicator
        self.gen_address(0)

        self.statements()

        self.gen_opcode(Opcodes.jump)
        self.gen_address(validation)

        after_loop_instruction = self.instruction_indicator
        self.instruction_indicator = instruction
        self.gen_address(after_loop_instruction)
        self.instruction_indicator = after_loop_instruction

        self.match("TK_END")
        self.match("TK_SEMICOLON")

    def controlrepeat_state(self):
        self.match("TK_REPEAT")
        target = self.instruction_indicator
        self.statements()
        self.match("TK_UNTIL")
        self.condition()
        self.gen_opcode(Opcodes.jfalse)
        self.gen_address(target)

    def write_line(self):
        self.match("TK_WRITELN")
        self.match("TK_LEFT_PAR")

        while True:
            if self.curr_t[1] == "TK_ID":
                symbol = self.find_name(self.curr_t[0])
                if hasattr(symbol, "assignment_type"):
                    self.match("TK_ID")
                    self.access_array(symbol)
                    self.gen_opcode(Opcodes.array_print)
                    continue
                else:
                    dt_1 = self.expr()
                if dt_1 == "TK_INTEGER":
                    self.gen_opcode(Opcodes.print_int)
                    self.gen_address(symbol.data_indicator)
                elif dt_1 == "TK_ARRAY":
                    self.gen_opcode(Opcodes.get)
                elif dt_1 == "TK_REAL":
                    self.gen_opcode(Opcodes.print_real)
                    self.gen_address(symbol.data_indicator)
                elif dt_1 == "TK_STRING":
                    self.gen_opcode(Opcodes.print_string)
                    self.gen_address(symbol.data_indicator)
                else:
                    raise TypeError("Not supported")
            if self.curr_t[1] == "TK_COMMA":
                self.match("TK_COMMA")
            elif self.curr_t[1] == "TK_RIGHT_PAR":
                self.match("TK_RIGHT_PAR")
                self.gen_opcode(Opcodes.newline)
                return
            else:
                raise SyntaxError("Right parentheses or comma expected.")

    def statements(self):
        while self.curr_t[1] != "TK_END":
            if self.curr_t[1] == "TK_ID":
                self.assign_state()
            elif self.curr_t[1] == "TK_SEMICOLON":
                self.match("TK_SEMICOLON")
            elif self.curr_t[1] == "TK_COMMENT":
                self.match("TK_COMMENT")
            elif self.curr_t[1] == "TK_WRITELN":
                self.write_line()
            elif self.curr_t[1] == "TK_REPEAT":
                self.controlrepeat_state()
            elif self.curr_t[1] == "TK_WHILE":
                self.whileloop_state()
            elif self.curr_t[1] == "TK_IF":
                self.ifelse_state()
            elif self.curr_t[1] == "TK_FOR":
                self.forloop_state()
            elif self.curr_t[1] == "TK_CASE":
                self.case_state()
            else:
                return

    # #######################################################################################

    # Variable Declaration Functions

    # #######################################################################################

    def declare_var(self):
        """
        Declare variables
        """
        self.match("TK_VAR")
        variables_initialized = []

        while self.curr_t[1] == "TK_ID":
            if self.curr_t not in variables_initialized:
                variables_initialized.append(self.curr_t)
                self.match("TK_ID")

                if self.curr_t[1] == "TK_COMMA":
                    self.match("TK_COMMA")
            else:
                raise NameError("Variable already declared" + self.curr_t[1])

        self.match("TK_COLON")

        data_type = Aux.get_type(self.curr_t[1])
        self.match(data_type)

        if data_type == "TK_ARRAY":
            self.match("TK_LEFT_BRACKET")
            access_type, lower_bound, upper_bound = self.range_array(self.curr_t)
            self.match("TK_RANGE")
            self.match("TK_RIGHT_BRACKET")
            self.match("TK_OF")

            if self.curr_t[1] == "TK_INTEGER":
                assignment_type = self.curr_t[1]
                self.match("TK_INTEGER")
            elif self.curr_t[1] == "TK_REAL":
                assignment_type = self.curr_t[1]
                self.match("TK_REAL")
            elif self.curr_t[1] == "TK_CHAR":
                assignment_type = self.curr_t[1]
                self.match("TK_CHAR")
            else:
                raise TypeError("Unsupported types: " + self.curr_t[1])
            self.match("TK_SEMICOLON")

            for variable in variables_initialized:
                array_symb = Symbol(variable[0], 'TK_ARRAY', 'ARRAY', self.data_indicator)
                array_symb.access_type = access_type
                array_symb.lower_bound = lower_bound
                array_symb.upper_bound = upper_bound
                array_symb.assignment_type = assignment_type
                self.symbol_table.append(array_symb)
                self.data_indicator += 4 * int(upper_bound) - int(lower_bound)

        else:
            self.match("TK_SEMICOLON")
            for variable in variables_initialized:
                variable_symb = Symbol(variable[0], data_type, "VARIABLE", self.data_indicator)
                self.data_indicator += 1
                self.symbol_table.append(variable_symb)
            self.data_indicator += 1

        if self.curr_t[1] == "TK_VAR":
            self.declare_var()
        else:
            self.begin()

    def range_array(self, token):
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
        token_type = self.curr_t[1]

        if token_type == "TK_INTEGER":
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(self.curr_t[0])
            self.match("TK_INTEGER")
            return "TK_INTEGER"
        elif token_type == "TK_ID":
            sym_object = self.find_name(self.curr_t[0])
            if sym_object.description == "VARIABLE":
                self.gen_opcode(Opcodes.push)
                self.gen_address(sym_object.data_indicator)
                self.match("TK_ID")
                return sym_object.data_type
            elif sym_object.description == "ARRAY":
                self.match("TK_ID")
                self.access_array(sym_object)
                self.gen_opcode(Opcodes.get)
                return sym_object.assignment_type
        elif token_type == "TK_STRING":
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(self.curr_t[0])
            self.match("TK_STRING")
            return "TK_BOOL"
        elif token_type == "TK_BOOL":
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(self.curr_t[0])
            self.match("TK_BOOL")
            return "TK_BOOL"
        elif token_type == "TK_CHAR":
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(self.curr_t[0])
            self.match("TK_CHAR")
            return "TK_CHAR"
        elif token_type == "TK_REAL":
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(self.curr_t[0])
            self.match("TK_REAL")
            return "TK_REAL"
        elif token_type == "TK_NOT":
            self.gen_opcode(Opcodes.logical_not)
            self.match("TK_NOT")
            return self.factor()
        elif token_type == "TK_LEFT_PAR":
            self.match("TK_LEFT_PAR")
            left_par = self.expr()
            self.match("TK_RIGHT_PAR")
            return left_par
        else:
            pass

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
            self.gen_opcode(op_Opcode.get(operation))
            if (operation == "division"):
                return datatype_1
            else:
                return "TK_INTEGER"
        elif Aux.check_int_real(datatype_1, datatype_2):
            self.gen_opcode(Opcodes.xchg,
                            Opcodes.cvr,
                            Opcodes.xchg,
                            op_Opcode.get(str("f" + operation)))
            return "TK_REAL"
        elif Aux.check_real_int(datatype_1, datatype_2):
            self.gen_opcode(Opcodes.cvr, op_Opcode.get(str("f" + operation)))
            return "TK_REAL"
        elif Aux.check_real_real(datatype_1, datatype_2):
            if (operation in {"subtraction", "multiplication"}):
                self.gen_opcode(op_Opcode.get(str("f" + operation)))
            elif operation == "addition":
                self.gen_opcode(op_Opcode.get(operation))
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
            self.gen_opcode(dict_op.get(operation))
        elif Aux.check_int_real(datatype_1, datatype_2):
            self.gen_opcode(Opcodes.xchg, Opcodes.cvr, Opcodes.xchg, dict_op.get(operation))
        elif Aux.check_real_int(datatype_1, datatype_2):
            self.gen_opcode(Opcodes.cvr, dict_op.get(operation))
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
                self.gen_opcode(Opcodes.divide)
                return "TK_INT"
        elif operation == "TK_MULTIPLY":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="multiplication")
        elif operation == "TK_OR":
            if datatype_1 == "TK_BOOL" and datatype_2 == "TK_BOOL":
                self.gen_opcode(Opcodes.logical_or)
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

    def gen_opcode(self, *ops):
        for op in ops:
            self.bytes_list[self.instruction_indicator] = op
            self.instruction_indicator += 1

    def gen_address(self, target):
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
        if tk_ == self.curr_t[1]:
            if self.curr_t[1] != "TK_EOF":
                self.curr_t = self.t_lst[self.t_index]
                self.t_index += 1
        else:
            raise IndexError("Doesn't Match" + " " + tk_ + " " + self.curr_t[1])

    def condition(self):
        expression = self.expr()

        if self.curr_t[1] in comparison_operators_list:
            data_type = self.curr_t[1]
            self.match(data_type)
            term2 = self.term()
            expression = self.emit(data_type, expression, term2)
            return expression

        else:
            raise TypeError("Expected condition, not: " + self.curr_t[1])

    def expr(self):
        dt_1 = self.term()
        while self.curr_t[1] == "TK_ADD" or self.curr_t[1] == "TK_SUBTRACT":
            token_op = self.curr_t[1]
            self.match(token_op)
            dt_1 = self.emit(token_op, dt_1, self.term())

        return dt_1

    def term(self):
        dt_1 = self.factor()
        while self.curr_t[1] == "TK_MULTIPLY" or self.curr_t[1] == "TK_DIVIDE":
            token_op = self.curr_t[1]
            self.match(token_op)
            dt_1 = self.emit(token_op, dt_1, self.factor())
        return dt_1

    def assign_state(self):
        sym_object = self.find_name(self.curr_t[0])
        if sym_object:
            left_side = sym_object.data_type

            self.match("TK_ID")

            if self.curr_t[1] == "TK_LEFT_BRACKET":
                self.access_array(sym_object)
                self.match("TK_ASSIGNMENT")
                exp_1 = self.expr()
                if exp_1 == sym_object.assignment_type:
                    self.gen_opcode(Opcodes.put)
                else:
                    raise TypeError('Mismatched types: ' + exp_1 + ' and ' + symbol.assignment_type)
                return

            self.match("TK_ASSIGNMENT")
            right_side = self.expr()

            if left_side == right_side:
                self.gen_opcode(Opcodes.pop)
                self.gen_address(sym_object.data_indicator)
            else:
                raise TypeError(left_side + ' != ' + right_side)
        else:
            raise NameError("Variable Not Declared: " + self.curr_t[0])

    def access_array(self, symbol):
        """
        Parameters:
                    * symbol - the array to be accessed
        :rtype:
        """
        self.match("TK_LEFT_BRACKET")
        sym_atindex = self.find_name(self.curr_t[0])
        self.gen_opcode(Opcodes.push)
        self.gen_address(sym_atindex.data_indicator)
        self.match("TK_ID")
        self.match("TK_RIGHT_BRACKET")

        self.gen_opcode(Opcodes.pushi)

        if sym_atindex.data_type == "TK_INTEGER":
            self.gen_address(symbol.lower_bound)
            self.gen_opcode(Opcodes.xchg)
            self.gen_opcode(Opcodes.sub)
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(4)
            self.gen_opcode(Opcodes.multiply)
            self.gen_opcode(Opcodes.pushi)
            self.gen_address(symbol.data_indicator)
            self.gen_opcode(Opcodes.add)

        else:
            raise TypeError('Unsupported type:' + sym_atindex.data_type)
