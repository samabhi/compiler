# -*- pascal_scanner.py -*-
# Reads a pascal files and returns a list of token objects

#----------------------------------------
#  TODO
#----------------------------------------

# - [done] Scan pascal file
# - [done] Tokenize program
# - - [done] Handle alphanumerics
# - - [done] Handle operators
# - - [done] Handle quotes
# - - [] Handle comments

import keywords
from tokens import Token


class Scanner(object):
    # constructor
    def __init__(self, fileName):
        # Parameters
        #   * filename
        #       - Pascal file to be read and tokenized

        self.defined_keywords_list = keywords.defined_keywords_list
        self.supported_operators = keywords.supported_operators
        self.array_index = 0
        self.token = Token()
        self.token_lst = []
        self.reserved_prefix = 'TK_'
        self.operators_KeyValue_list = keywords.operators_KeyValue_list

        # read in pascal file
        with open(fileName, 'r') as pascFile:
            self.pascal = pascFile.read().lower()

    # #############################################################################

    def tokenBuilder(self, tempWord, keyValue):
        # Parameters
        #   * tempword
        #       - value of token
        #   * keyValue
        #       - data type of token
        return self.token.buildToken(tempWord, keywords.defined_keywords_list.get(keyValue).upper())

    # #############################################################################

    def opTokenBuilder(self, tempOperator):
        # Parameters
        #   * tempword
        #       - value of token
        #   * keyValue
        #       - data type of token

        return self.token.buildToken(tempOperator,
                                     self.reserved_prefix + self.operators_KeyValue_list.get(tempOperator))

    # #############################################################################

    # Helper functions follow

    # #############################################################################

    def help_caseLetter(self, tempWord):
        # Parameters
        #   * tempWord
        #       - a value that is only alphabetical
        # Returns: A token with tempword as the value and either 'id' or a keyword as the data type

        self.token.set_colNumber(self.token.get_colNumber() + len(tempWord))
        self.array_index += len(tempWord)

        # check if the string is a reserved keyword
        if tempWord in self.defined_keywords_list:
            return self.tokenBuilder(tempWord, tempWord)
        # if not then it's a string literal
        else:
            return self.tokenBuilder(tempWord, "id")


    def help_caseNum(self, tempDigit):
        # Parameters
        #   * tempDigit
        #       - a numerical value
        # Returns: A token with tempdigit as the value and integer/real/range as the data type

        # we need to know if there is a '.' in the stringlit to know what type of data type the number is
        if "." in tempDigit:

            temp_index = tempDigit.find(".")

            if tempDigit.count('.') == 1:
                number = float(tempDigit)
                return self.tokenBuilder(number, "real")

            elif tempDigit.count('.') == 2:
                return self.tokenBuilder(tempDigit, "range")

            else:
                return "ERROR: Invalid string lit"
        # check for an e in the middle of the number for exponentiation
        elif "e" in tempDigit:
            temp_index = tempDigit.find("e")

            # even if there is an e we have to see if it's used correctly
            if self.pascal[temp_index - 1].isdigit():
                if self.pascal[temp_index + 1].isdigit() or self.pascal[temp_index + 1] == "+" or self.pascal[
                            temp_index + 1] == "-":
                    number = float(tempDigit)
                    return self.tokenBuilder(number, "real")
                else:
                    return "ERROR: invalid string lit"
            else:
                return "ERROR: invalid string lit"
        # if not a real number or a range then it has to be an integer
        else:
            number = int(tempDigit)
            return self.tokenBuilder(number, "integer")

    def help_one_caseOperator(self, tempOperator):
        # Parameters
        #   * tempOperator
        #       - a value that is an operator
        # Returns: A token with an operator as the value and it's corresponding data type from keywords.py

        if self.pascal[self.array_index + 1] == "=":
            tempOperator += self.pascal[self.array_index + 1]
            self.array_index += 2
            self.token.set_colNumber(self.token.get_colNumber() + 2)
            return self.opTokenBuilder(tempOperator)
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)

    def help_two_caseOperator(self, tempOperator):
        # Parameters
        #   * tempOperator
        #       - a value that is an operator
        # Returns: A token with an operator as the value and it's corresponding data type from keywords.py

        if self.pascal[self.array_index + 1] == ">":
            tempOperator += self.pascal[self.array_index + 1]
            self.array_index += 2
            self.token.set_colNumber(self.token.get_colNumber() + 2)
            return self.opTokenBuilder(tempOperator)
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)

    def help_three_caseOperator(self, tempOperator):
        # Parameters
        #   * tempOperator
        #       - a value that is an operator
        # Returns: A token with an operator as the value and it's corresponding data type from keywords.py

        if self.pascal[self.array_index + 1] == "*":
            return self.caseComment()
        else:
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.opTokenBuilder(tempOperator)

    def help_caseQuote(self, tempString):
        # Parameters
        #   * tempString
        #       - a value that is an string
        # Returns: A token with a string data type

        # Check if it is the closing '
        if self.pascal[self.array_index] == "\'" and self.pascal[self.array_index + 1] != "\'":
            tempString += self.pascal[self.array_index]
            self.array_index += 1
            self.token.set_colNumber(self.token.get_colNumber() + 1)
            return self.tokenBuilder(tempString, "string")

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

    def help_caseComment(self, tempComment):
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
        # Loop through each char
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
            if self.pascal[self.array_index].isdigit() or self.pascal[self.array_index] == '.' or self.pascal[
                self.array_index] == 'e':
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
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
                return self.opTokenBuilder(tempOperator)

            # the rest are just normal operators_KeyValue_list
            else:
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)

                return self.opTokenBuilder(tempOperator)

                # ##########################################################################################################################################

    # Goes through the file, and checks for each possible case that the chars it is encountering can fall under
    # Returns token_lst which consist of value, datatype, row_number number and column number or
    # an error if it cannot identify the character
    def scan(self):
        while self.array_index < len(self.pascal):

            if self.pascal[self.array_index].isalpha():
                self.token_lst.append(self.caseLetter())
            elif self.pascal[self.array_index].isdigit():
                self.token_lst.append(self.caseNum())
            elif self.pascal[self.array_index] == " ":
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
            elif self.pascal[self.array_index] == "\n":
                self.array_index += 1
                self.token.set_rowNumber(self.token.get_rowNumber() + 1)
                self.token.set_colNumber(0)
            elif self.pascal[self.array_index] in self.supported_operators:
                self.token_lst.append(self.caseOperator())
            elif self.pascal[self.array_index] == "{":
                self.token_lst.append(self.caseComment())
            elif self.pascal[self.array_index] == "\'":
                self.token_lst.append(self.caseQuote())
            else:
                raise TypeError("Can't identify char: " + self.pascal[self.array_index])

        self.token_lst.append(self.token.buildToken("EOF", keywords.defined_keywords_list.get("eof").upper()))

        return self.token_lst

    # ##########################################################################################################################################

    # Handles the various formats of commenting allowed in Pascal
    # Returns comment token or an error if file is improperly commented
    def caseComment(self):

        tempComment = ""

        # comment type (*...*)
        if self.pascal[self.array_index] == "(" and self.pascal[self.array_index + 1] == "*":

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
                    self.help_caseComment(tempComment)

            # throw error if file ends before comment ends
            if self.array_index >= len(self.pascal):
                return "ERROR: End of file before comment completed"
