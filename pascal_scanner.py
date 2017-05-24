# The scanner is the first part of the compiler that reads a pascal file.
# Returns: clues which consist of the value, the data type, row_number number and column number
import keywords
from tokens import Token

class Scanner(object):

    # constructor
    def __init__(self, fileName):
        self.defined_keywods_list = keywords.defined_keywords_list
        self.supported_operators = keywords.supported_operators
        self.array_index = 0
        self.token = Token()
        self.clues = []
        self.reserved_prefix = 'TK_'
        self.operators_KeyValue_list = keywords.operators_KeyValue_list

        # read in pascal file
        with open(fileName, 'r') as pascFile:
            self.pascal = pascFile.read().lower()
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def tokenBuilder(self,tempWord,keyValue):
        return self.token.buildToken(tempWord, keywords.defined_keywords_list.get(keyValue).upper())
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def opTokenBuilder(self,tempOperator):
        return self.token.buildToken(tempOperator, self.reserved_prefix + self.operators_KeyValue_list.get(tempOperator))
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   #all the helper finctions for completing the working of the main functions of the program
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #  Goes through cases involving alpha - string literal or keyword
    # Returns: A built word that is a string literal or a keyword
    def help_caseLetter(self,tempWord):
        self.token.set_colNumber(self.token.get_colNumber() + len(tempWord))
        self.array_index += len(tempWord)
        
        # check if the string is a string literal
        if self.defined_keywods_list.get(tempWord) is None:
            return self.tokenBuilder(tempWord,"id")
            # or a reserved keyword
        else:
            return self.tokenBuilder(tempWord, tempWord)

#----------------------
# Reading in Numbers
    # Returns: Either an integer, a real, or a range or an error

    def help_caseNum(self,tempDigit):
        # have to convert the string literal of digits to the correct data type
                if "." in tempDigit:

                    temp_index = tempDigit.find(".")

                    # if there was a '.' in the middle of a number, we have to identify what it implies
                    # if it is a float
                    if tempDigit.count('.') == 1:
                        number = float(tempDigit)
                        return self.tokenBuilder(number,"real")
                    # or if it is a range for an array
                    elif tempDigit.count('.') == 2:
                        return self.tokenBuilder(tempDigit,"range")
                    # else it is invalid
                    else:
                        return "ERROR: Invalid string lit"
                # Checking for special condition, if there is an "e" in the middle of a number
                elif "e" in tempDigit:
                    temp_index = tempDigit.find("e")

                    # if there was a 'e' in the middle of a number, we have to make sure its under the right conditions
                    if self.pascal[temp_index - 1].isdigit():
                        if self.pascal[temp_index + 1].isdigit() or self.pascal[temp_index + 1] == "+" or self.pascal[
                                    temp_index + 1] == "-":
                            number = float(tempDigit)
                            return self.tokenBuilder(number,"real")
                        else:
                            return "ERROR: invalid string lit"
                    else:
                        return "ERROR: invalid string lit"
                else:
                    number = int(tempDigit)
                    return self.tokenBuilder(number,"integer")

# ##########################################################################################################################################

    # Handles various operators_KeyValue_list, as well as checking for special condition (Ex: Operators involving multple characters such as
    # assignment ':=' )
    # Returns the operator token
    def help_one_caseOperator(self,tempOperator):
        if self.pascal[self.array_index + 1] == "=":
            tempOperator += self.pascal[self.array_index + 1]
            self.array_index += 2
            self.token.set_colNumber(self.token.get_colNumber() + 2)
            return self.opTokenBuilder(tempOperator)
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)
# ##########################################################################################################################################

    def help_two_caseOperator(self,tempOperator):
        if self.pascal[self.array_index + 1] == ">":
            tempOperator += self.pascal[self.array_index + 1]
            self.array_index += 2
            self.token.set_colNumber(self.token.get_colNumber() + 2)
            return self.opTokenBuilder(tempOperator)
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)
# ##########################################################################################################################################

    def help_three_caseOperator(self,tempOperator):
        if self.pascal[self.array_index + 1] == "*":
            return self.caseComment()
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)
# ##########################################################################################################################################

    def help_four_caseOperator(self,tempOperator):
        if self.pascal[self.array_index + 1] == "/":
            return self.caseComment()
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)
#-------------------------------------------
# Keeps tracks of quotes, and ensures that they are being used properly in the file
    # Returns: String token or an error if quotes are improperly handled
    def help_caseQuote(self,tempString):
        # Check if it is the closing '
            if self.pascal[self.array_index] == "\'" and self.pascal[self.array_index + 1] != "\'":
                tempString += self.pascal[self.array_index]
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
                return self.tokenBuilder(tempString, "string")
            # else check if it is a quote within a quote
            elif self.pascal[self.array_index] == "\'" and self.pascal[self.array_index + 1] == "\'":
                tempString += self.pascal[self.array_index] + self.pascal[self.array_index + 1]
                self.array_index += 2
                self.token.set_colNumber(self.token.get_colNumber() + 2)
            # else it is just another char
            else:
                tempString += self.pascal[self.array_index]

                if self.pascal[self.array_index] == "\n":
                    self.token.set_colNumber(0)
                    self.token.set_rowNumber(self.token.get_rowNumber() + 1)
                    
                else:
                    self.token.set_colNumber(self.token.get_colNumber() + 1)

                self.array_index += 1

# ##########################################################################################################################################
    def  help_one_caseComment(self,tempComment):
            if self.pascal[self.array_index] == "\n":
                self.token.set_colNumber(0)
                self.token.set_rowNumber(self.token.get_rowNumber() + 1)
            else:
                self.token.set_colNumber(self.token.get_colNumber() + 1)
                self.array_index += 1

# ##########################################################################################################################################

    def  help_two_caseComment(self,tempComment):
        if self.pascal[self.array_index] == "}":
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.tokenBuilder(tempComment, "comment")
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
# ##########################################################################################################################################

    def  help_three_caseComment(self,tempComment):
        if self.pascal[self.array_index] == "\n":
            self.array_index += 1
            self.token.set_rowNumber(self.token.get_rowNumber() + 1)
            self.token.set_colNumber(0)
            return self.tokenBuilder(tempComment, "comment")
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
# ##########################################################################################################################################

    def  help_four_caseComment(self,tempComment):
        if self.pascal[self.array_index] == "\n":
            self.token.set_colNumber(self.token.get_colNumber() + 0)
            self.token.set_rowNumber(self.token.get_rowNumber() + 1)
        else:
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            self.array_index += 1

# ##########################################################################################################################################
    #  Goes through cases involving alpha - string literal or keyword
    # Returns: A built word that is a string literal or a keyword
    def caseLetter(self):
        tempWord = ""
        #Loop through each char
        for char in self.pascal[self.array_index:]:
            # create string
            if char.isalpha() or char.isdigit():
                tempWord += char
            else:
                return self.help_caseLetter(tempWord)

# ##########################################################################################################################################
#   # Reading in Numbers
    # Returns: Either an integer, a real, or a range or an error

    def caseNum(self):
        tempDigit = ""

        while self.array_index < len(self.pascal):
            # create string of numbers
            if self.pascal[self.array_index].isdigit() or self.pascal[self.array_index] == '.' or self.pascal[self.array_index] == 'e':
                tempDigit += self.pascal[self.array_index]
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
            else:
                return self.help_caseNum(tempDigit)

# ##########################################################################################################################################
    # Keeps tracks of quotes, and ensures that they are being used properly in the file
    # Returns: String token or an error if quotes are improperly handled
    def caseQuote(self):

        tempString = ""

        tempString += self.pascal[self.array_index]
        self.array_index += 1
        self.token.set_colNumber(self.token.get_colNumber() + 1)

        while self.array_index < len(self.pascal):
            self.help_caseQuote(tempString)

        # throw an error if the file ends before the string is completed
        if self.array_index >= len(self.pascal):
            return "ERROR: End of file before string completed"

# ##########################################################################################################################################
    # Handles various operators_KeyValue_list, as well as checking for special condition (Ex: Operators involving multple characters such as
    # assignment ':=' )
    # Returns the operator token
    def caseOperator(self):

        tempOperator = ""

        while self.array_index < len(self.pascal):

            tempOperator += self.pascal[self.array_index]

            # the assignment operators_KeyValue_list has to be checked specifically since both of its chars can also be operators_KeyValue_list on their own
            if self.pascal[self.array_index] == ":":
                return self.help_one_caseOperator(tempOperator)

            # the not equal has to be checked specifically since both of its chars can also be operators_KeyValue_list on their own
            elif self.pascal[self.array_index] == "<":
                return self.help_two_caseOperator(tempOperator)

            # the less than or equal to operator has to be checked specifically since both of its chars can also be operators_KeyValue_list on their own
            elif self.pascal[self.array_index] == "<":
                return self.help_one_caseOperator(tempOperator)

            # the greater than or equal to operator has to be checked specifically since both of its chars can also be operators_KeyValue_list on their own
            elif self.pascal[self.array_index] == ">":
                return self.help_one_caseOperator(tempOperator)


            elif self.pascal[self.array_index] == "(":
                # check if ( is an operator in this case or the beginning of a comment
                return self.help_three_caseOperator(tempOperator)

            elif self.pascal[self.array_index] == "/":
                # Check if / is an operator in this case of the beginning of a comment
                return self.help_four_caseOperator(tempOperator)

            # the rest are just normal operators_KeyValue_list
            else:
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)

                return self.opTokenBuilder(tempOperator)

# ##########################################################################################################################################

    # Goes through the file, and checks for each possible case that the chars it is encountering can fall under
    # Returns clues which consist of value, datatype, row_number number and column number or
    # an error if it cannot identify the character
    def scan(self):
        while self.array_index < len(self.pascal):

            if self.pascal[self.array_index].isalpha():
                self.clues.append(self.caseLetter())
            elif self.pascal[self.array_index].isdigit():
                self.clues.append(self.caseNum())
            elif self.pascal[self.array_index] == " ":
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
            elif self.pascal[self.array_index] == "\n":
                self.array_index += 1
                self.token.set_rowNumber(self.token.get_rowNumber() + 1)
                self.token.set_colNumber(0)
            elif self.pascal[self.array_index] in self.supported_operators:
                self.clues.append(self.caseOperator())
            elif self.pascal[self.array_index] == "{":
                self.clues.append(self.caseComment())
            elif self.pascal[self.array_index] == "\'":
                self.clues.append(self.caseQuote())
            else:
                raise TypeError("Can't identify char: " + self.pascal[self.array_index])

        self.clues.append(self.token.buildToken("EOF", keywords.defined_keywords_list.get("eof").upper()))

        return self.clues

# ##########################################################################################################################################

    # Handles the various formats of commenting allowed in Pascal
    # Returns comment token or an error if file is improperly commented
    def caseComment(self):

        tempComment = ""

        # comment type {...} if single line or {*...*} if multiline
        if self.pascal[self.array_index] == '{' and self.pascal[self.array_index + 1] == "*":

            tempComment += self.pascal[self.array_index] + self.pascal[self.array_index + 1]
            self.array_index += 2
            self.token.set_colNumber(self.token.get_colNumber() + 2)

            while self.array_index < len(self.pascal):

                # check if comment is ending
                if self.pascal[self.array_index] == "*" and self.pascal[self.array_index + 1] == "}":
                    tempComment += self.pascal[self.array_index] + self.pascal[self.array_index + 1]
                    self.array_index += 2
                    self.token.set_colNumber(self.token.get_colNumber() + 2)
                    return self.tokenBuilder(tempComment,"comment")
                else:
                    tempComment += self.pascal[self.array_index]
                    self.help_one_caseComment(tempComment)

                # throw error if file ends before comment ends
                if self.array_index >= len(self.pascal):
                    return "ERROR: End of file before comment completed"
        # if it is a single line { comment
        elif self.pascal[self.array_index] == '{' and self.pascal[self.array_index + 1] != "*":
            while self.array_index < len(self.pascal):
                tempComment += self.pascal[self.array_index]

                # check if comment is ending
                self.help_two_caseComment(tempComment)

            # throw error if file ends before comment ends
            if self.array_index >= len(self.pascal):
                return "ERROR: End of file before comment completed"

        # comment type //....
        elif self.pascal[self.array_index] == "/":

            while self.array_index < len(self.pascal):
                tempComment += self.pascal[self.array_index]

                # check if comment is ending
                self.help_three_caseComment(tempComment)

            # throw error if file ends before comment ends
            if self.array_index >= len(self.pascal):
                return "ERROR: End of file before comment completed"

        # comment type (*...*)
        elif self.pascal[self.array_index] == "(" and self.pascal[self.array_index + 1] == "*":

            tempComment += self.pascal[self.array_index] + self.pascal[self.array_index + 1]
            self.array_index += 2
            self.token.set_colNumber(self.token.get_colNumber() + 2)

            while self.array_index < len(self.pascal):

                # check if comment is ending
                if self.pascal[self.array_index] == "*" and self.pascal[self.array_index + 1] == ")":
                    tempComment += self.pascal[self.array_index] + self.pascal[self.array_index + 1]
                    self.array_index += 2
                    self.token.set_colNumber(self.token.get_colNumber() + 2)
                    return self.token.buildToken(tempComment, self.reserved_prefix + "COMMENT")
                else:
                    tempComment += self.pascal[self.array_index]
                    self.help_four_caseComment(tempComment)

            # throw error if file ends before comment ends
            if self.array_index >= len(self.pascal):
                return "ERROR: End of file before comment completed"
