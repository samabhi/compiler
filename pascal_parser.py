# this code generates machine code from each of the user program instructions
from pascal_opcodes import Opcodes, compress_bytes, arth_op, comp_op
from Symbol import symbol
import auxiliary_parser_functions as Aux
from keywords import comparison_operators_list


class Parser(object):
    def __init__(self, clues):

        self.clues_list = clues
        self.clues_array_index = 0
        self.instruction_indicator = 0
        self.data_indicator = 0
        self.bytes_list = bytearray(1000)
        self.symbol_table = []

        self.current_token = self.clues_list[self.clues_array_index]
        self.clues_array_index += 1

# ####################################################################################
    def checkDataTypesForArth(self, datatype_1, datatype_2, operation):
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
        dict_op = comp_op

        if self.ifEqual(datatype_1, datatype_2):
            self.make_opcode(dict_op.get(operation))
        elif Aux.check_int_real(datatype_1, datatype_2):
            self.make_opcode(Opcodes.xchg, Opcodes.cvr, Opcodes.xchg, dict_op.get(operation))
        elif Aux.check_real_int(datatype_1, datatype_2):
            self.make_opcode(Opcodes.cvr, dict_op.get(operation))
        else:
            return None
        return "TK_BOOL"

# ##############################################################################
    # storing variables properly to the symbol table.
    def declarations(self):
        self.match("TK_VAR")

        var_list = []

        while self.current_token[1] == "TK_ID":
            # stops the program from declaring a same variable again
            if self.current_token in var_list:
                raise NameError("Variable already declared" + self.current_token[1])
            # saving the variable to symbol table if valid
            else:
                var_list.append(self.current_token)
                self.match("TK_ID")

                if self.current_token[1] == "TK_COMMA":
                    self.match("TK_COMMA")

        self.match("TK_COLON")

        # Checks for variables of different data types
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
            access_type, token, lower_bound, upper_bound = self.get_range(self.current_token)
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
                raise TypeError("Unsupported array types: " + self.current_token[1])
            self.match("TK_SEMICOLON")

            if access_type == "TK_INTEGER":
                for var in var_list:
                    s = symbol(var[0], 'TK_ARRAY', 'ARRAY', self.data_indicator)
                    s.access_type = access_type
                    s.lower_bound = lower_bound
                    s.upper_bound = upper_bound
                    s.assignment_type = assignment_type
                    self.symbol_table.append(s)
                    self.data_indicator += 4 * int(upper_bound) - int(lower_bound)
            else:
                raise TypeError("Array access type not allowed:" + access_type)

        else:
            self.match("TK_SEMICOLON")
            for var in var_list:
                var_symbol = symbol(var[0], data_type, "VARIABLE", self.data_indicator)
                self.data_indicator += 1
                self.symbol_table.append(var_symbol)
            self.data_indicator += 1
        # see if there are more variables
        if self.current_token[1] == "TK_VAR":
            self.declarations()
        else:
            # declaratiosn ended
            self.begin()
            # ####################################################################################

    # see if the current token is already stored in the symbol table
    # Returns: symbol object
    def find_name(self, label):

        for obj in self.symbol_table:
            if obj.label == label:
                return obj

        return None

    # ####################################################################################
    # see if the current token matches with input
    def match(self, tk_):

        if tk_ == self.current_token[1]:
            if self.current_token[1] != "TK_EOF":
                self.current_token = self.clues_list[self.clues_array_index]
                self.clues_array_index += 1
        else:
            raise IndexError("Doesn't Match" + " " + tk_ + " " + self.current_token[1])

            # #####################################################################################

    # starting the parser
    def start_parser(self):

        self.match("TK_PROGRAM")
        self.match("TK_ID")
        self.match("TK_SEMICOLON")

        if self.current_token[1] == "TK_VAR":
            self.declarations()
        else:
            self.begin()

        return self.bytes_list

    # #######################################################################################
    # Handles "Begin" begin keyword in pascal
    def begin(self):
        while self.current_token[1] == "TK_COMMENT":
            self.match("TK_COMMENT")
        self.match("TK_BEGIN")
        self.statements()
        self.match("TK_END")
        self.match("TK_DOT")
        self.match("TK_EOF")
        self.make_opcode(Opcodes.halt)

        # #######################################################################################

    # identifies the type of statement. Based on context free grammar
    def statements(self):
        while self.current_token[1] != "TK_END":
            if self.current_token[1] == "TK_ID":
                self.assignment_statement()
            elif self.current_token[1] == "TK_SEMICOLON":
                self.match("TK_SEMICOLON")
            elif self.current_token[1] == "TK_COMMENT":
                self.match("TK_COMMENT")
            elif self.current_token[1] == "TK_WRITELN":
                self.writeln()
            elif self.current_token[1] == "TK_REPEAT":
                self.repeat_statement()
            elif self.current_token[1] == "TK_WHILE":
                self.while_loops()
            elif self.current_token[1] == "TK_IF":
                self.if_statement()
            elif self.current_token[1] == "TK_FOR":
                self.for_statement()
            elif self.current_token[1] == "TK_CASE":
                self.case_statement()
            else:
                # print "statements function: Can't match current token ", self.current_token
                return

                # ###############################################################################################

    # generates one byte opcode using the instruction pointer and then increments the instruction pointer
    def make_opcode(self, *ops):
        for op in ops:
            self.bytes_list[self.instruction_indicator] = op
            self.instruction_indicator += 1

            # ################################################################################################

    # packs a target value into 4 bytes, using the instruction pointer and increments the instruction pointer
    def make_address(self, target):

        bytearray_list = compress_bytes(target)

        for byte in bytearray_list:
            self.bytes_list[self.instruction_indicator] = byte
            self.instruction_indicator += 1

            # #################################################################################################

    # handles expressions
    def expressions(self):

        data_type1 = self.term()

        while self.current_token[1] == "TK_ADD" or self.current_token[1] == "TK_SUBTRACT":
            token_op = self.current_token[1]

            self.match(token_op)

            data_type2 = self.term()
            data_type1 = self.emit(token_op, data_type1, data_type2)

        return data_type1

    # ##############################################################################################
    # handles terms
    def term(self):
        data_type1 = self.factor()
        while self.current_token[1] == "TK_MULTIPLY" or self.current_token[1] == "TK_DIVIDE":
            token_op = self.current_token[1]
            self.match(token_op)
            data_type2 = self.factor()
            data_type1 = self.emit(token_op, data_type1, data_type2)
        return data_type1

    # #############################################################################################
    def ifEqual(self, dat1, dat2):
        if dat1 == dat2:
            return True
        else:
            return False


            # ##############################################################################################

    # handles factor and creates machine instructions
    def factor(self):

        if self.current_token[1] == "TK_INTEGER":
            self.make_opcode(Opcodes.pushi)
            self.make_address(self.current_token[0])
            self.match("TK_INTEGER")
            return "TK_INTEGER"
        elif self.current_token[1] == "TK_ID":
            symbol = self.find_name(self.current_token[0])

            if symbol.description == "VARIABLE":
                self.make_opcode(Opcodes.push)
                self.make_address(symbol.data_indicator)
                self.match("TK_ID")
                return symbol.data_type
            elif symbol.description == "ARRAY":
                self.match("TK_ID")
                self.access_array(symbol)
                self.make_opcode(Opcodes.get)
                return symbol.assignment_type
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
            left_par = self.expressions()
            self.match("TK_RIGHT_PAR")
            return left_par
        else:
            pass

            # #########################################################################################

    # generates machine instructions to write to standard output
    def writeln(self):
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
                    datatype1 = self.expressions()
                if datatype1 == "TK_INTEGER":
                    self.make_opcode(Opcodes.print_int)
                    self.make_address(symbol.data_indicator)
                elif datatype1 == "TK_ARRAY":
                    self.make_opcode(Opcodes.get)
                elif datatype1 == "TK_REAL":
                    self.make_opcode(Opcodes.print_real)
                    self.make_address(symbol.data_indicator)
                else:
                    raise TypeError("Writeln does not support type: " + str(symbol))
            if self.current_token[1] == "TK_COMMA":
                self.match("TK_COMMA")
            elif self.current_token[1] == "TK_RIGHT_PAR":
                self.match("TK_RIGHT_PAR")
                self.make_opcode(Opcodes.newline)
                return
            else:
                raise SyntaxError("Expected right paren or comma. Found: " + self.current_token[1])

                # ###################################################################################################

    # handles while loops
    def while_loops(self):
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

    # #####################################################################################################
    # Handles if-else control statements
    def if_statement(self):
        self.match("TK_IF")
        self.condition()
        self.match("TK_THEN")
        self.make_opcode(Opcodes.jfalse)
        hole_one = self.instruction_indicator
        self.make_address(0)
        self.statements()
        if self.current_token[1] == "TK_ELSE":
            self.make_opcode(Opcodes.jump)
            hole_two = self.instruction_indicator
            self.make_address(0)
            save = self.instruction_indicator
            self.instruction_indicator = hole_one
            self.make_address(save)
            self.instruction_indicator = save
            hole_one = hole_two
            self.match("TK_ELSE")
            self.statements()
        save = self.instruction_indicator
        self.instruction_indicator = hole_one
        self.make_address(save)
        self.instruction_indicator = save

    # #########################################################################################
    # Handles for loops
    # Returns: Nothing
    def for_statement(self):

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

    # #########################################################################################33
    # Handles case statement
    def case_statement(self):

        self.match("TK_CASE")
        self.match("TK_LEFT_PAR")
        checker = self.current_token
        exp_1 = self.expressions()
        if exp_1 == "TK_REAL":
            raise TypeError('Real type not allowed for case: ' + exp_1)
        self.match("TK_RIGHT_PAR")
        self.match("TK_OF")
        hole_list = []
        while (self.current_token[1] == "TK_INTEGER" or
                       self.current_token[1] == "TK_CHAR" or
                       self.current_token[1] == "TK_BOOL"):
            exp_2 = self.expressions()
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

    # #####################################################################################################
    # Gets range of access for an array
    # Returns types consisting of access type, the token, lower bound of the range, and the upper bound
    def get_range(self, token):

        split = token[0].split('..')
        if len(split) != 2:
            raise SyntaxError('Range token needs to be in the form of  0..2, got ' + self.current_token)
        lower_bound, upper_bound = split[0], split[1]

        access_type = "TK_INTEGER"

        # assume int
        lower_bound = int(lower_bound)
        upper_bound = int(upper_bound)

        return access_type, token, lower_bound, upper_bound

    # ######################################################################################################
    # Accesses the array for the range specified by program
    def access_array(self, symbol):
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
            raise TypeError('Array does not support type:' + current_symbol.data_type)

            # ####################################################################################################

    # Handles array assignments
    def array_assignment(self, symbol):
        self.access_array(symbol)
        self.match("TK_ASSIGNMENT")
        exp_1 = self.expressions()
        if exp_1 == symbol.assignment_type:
            self.make_opcode(Opcodes.put)
        else:
            raise TypeError('Array assignment mismatched types: ' + exp_1 + ' and ' + symbol.assignment_type)

            #   ####################################################################################################

    #  based on lookup tables. Creates appropriate machine instructions depending on operation and
    # the combination of datatype of the variables
    # Returns: Data type of result
    def emit(self, operation, datatype_1, datatype_2):
        # addition
        if operation == "TK_ADD":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="addition")
        # subtraction
        elif operation == "TK_SUBTRACT":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="subtraction")
        # division
        elif operation == "TK_DIVIDE":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="division")
        elif operation == "TK_DIV":
            if datatype_1 == "TK_INTEGER" and datatype_2 == "TK_INTEGER":
                self.make_opcode(Opcodes.divide)
                return "TK_INT"
        # multiplication
        elif operation == "TK_MULTIPLY":
            return self.checkDataTypesForArth(datatype_1, datatype_2, operation="multiplication")
        # or operator
        elif operation == "TK_OR":
            if datatype_1 == "TK_BOOL" and datatype_2 == "TK_BOOL":
                self.make_opcode(Opcodes.logical_or)
                return "TK_BOOL"
        # equal operator
        elif operation == "TK_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "equal")
            # not equal
        elif operation == "TK_NOT_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "not_equal")
            # less than
        elif operation == "TK_LESS_THAN":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "less_than")
            # less than or equal to
        elif operation == "TK_LESS_THAN_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "lte")
            # greater than
        elif operation == "TK_GREATER_THAN":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "greater_than")
            # greater than or equal to
        elif operation == "TK_GREATER_THAN_EQUAL":
            return self.checkDataTypesForLogical(datatype_1, datatype_2, "gte")
        else:
            raise TypeError("Emit cannot match datatype. Datatypes found: " + datatype_1 + " , " + datatype_2)

            # #############################################################################################################

    # handles variable assignment
    def assignment_statement(self):
        symbol = self.find_name(self.current_token[0])
        if symbol:
            left_side = symbol.data_type

            self.match("TK_ID")

            if self.current_token[1] == "TK_LEFT_BRACKET":
                self.array_assignment(symbol)
                return

            self.match("TK_ASSIGNMENT")

            right_side = self.expressions()

            if left_side == right_side:
                self.make_opcode(Opcodes.pop)
                self.make_address(symbol.data_indicator)

            else:
                raise TypeError(left_side + ' != ' + right_side)

        else:
            raise NameError("Variable Not Declared: " + self.current_token[0])

            # #######################################################################################

    # Handles various condition types
    # Returns: Data type
    def condition(self):
        term1 = self.expressions()

        # value = self.current_token[0]

        # Equal '==' Condition
        if self.current_token[1] in comparison_operators_list:
            data_type = self.current_token[1]
            self.match(data_type)
            term2 = self.term()
            term1 = self.emit(data_type, term1, term2)
            return term1

        # Else it raises an error
        else:
            raise TypeError("Expected condition, but instead received: " + self.current_token[1])

            # ################################################################################################

    # handles repeat-until loops
    def repeat_statement(self):
        self.match("TK_REPEAT")
        target = self.instruction_indicator
        self.statements()
        self.match("TK_UNTIL")
        self.condition()
        self.make_opcode(Opcodes.jfalse)
        self.make_address(target)
