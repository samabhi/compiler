# -*- pascal_scanner.py -*-
# Reads a pascal_file files and returns a list of token objects

import keywords
import scanner_helper as psh
from tokens import Token


class Scanner(object):
    # constructor
    def __init__(self, file):
        """
        Parameters:
                    * file - the pascal file to be read and tokenized
        :rtype:
        """
        self.defined_keywords_list = keywords.defined_keywords_list
        self.supported_operators = keywords.supported_operators
        self.operators_KeyValue_list = keywords.operators_KeyValue_list

        self.array_index = 0
        self.token = Token()
        self.token_lst = []

        # read in pascal_file file
        with open(file, 'r') as pascal_testfile:
            self.pascal_file = pascal_testfile.read().lower()

    # #############################################################################

    def tokenBuilder(self, tempWord, keyValue):
        """
        Parameters:
                    * tempWord - the value of the token
                    * keyValue  - the data type of the token
        :rtype: a token with a value of tempWord and a data type of keyValue
        """
        return Token.buildToken(self.token, tempWord, keywords.defined_keywords_list.get(keyValue).upper())

    def opTokenBuilder(self, tempOperator):
        """
        Parameters:
                    * tempOperator - 
        :rtype: a token with a value of tempOperator
        """
        return Token.buildToken(self.token, tempOperator,
                                     'TK_' + self.operators_KeyValue_list.get(tempOperator))

    # #############################################################################

    # Scanner

    # #############################################################################

    def scan(self):
        while len(self.pascal_file) > self.array_index:

            if self.pascal_file[self.array_index].isalpha():
                self.token_lst.append(self.if_letter())
            elif self.pascal_file[self.array_index].isdigit():
                self.token_lst.append(self.if_number())
            elif self.pascal_file[self.array_index] in self.supported_operators:
                self.token_lst.append(self.if_operator())
            elif self.pascal_file[self.array_index] == " ":
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
            elif self.pascal_file[self.array_index] == "\n":
                self.array_index += 1
                self.token.set_rowNumber(self.token.get_rowNumber() + 1)
                self.token.set_colNumber(0)
            elif self.pascal_file[self.array_index] == "\'":
                self.token_lst.append(self.if_quote())
            else:
                raise TypeError("Can't identify char: " + self.pascal_file[self.array_index])

        eof = self.token.buildToken("EOF", keywords.defined_keywords_list.get("eof").upper())
        self.token_lst.append(eof)

        return self.token_lst

    # #############################################################################

    # Case functions follow

    # #############################################################################

    def if_letter(self):
        # Parameters
        # Returns: A token which was returned by the helper function

        word_infile = ""
        # Loop through each character
        for character in self.pascal_file[self.array_index:]:
            # create string
            if character.isalpha() or character.isdigit():
                word_infile += character
            else:
                return psh.help_caseLetter(self, word_infile)

    def if_number(self):
        # Parameters
        # Returns: A token which was returned by the helper function

        digit_infile = ""

        while self.array_index < len(self.pascal_file):
            # create string of numbers
            if self.pascal_file[self.array_index].isdigit() or \
                            self.pascal_file[self.array_index] == '.':
                digit_infile += self.pascal_file[self.array_index]
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)
            else:
                return psh.help_caseNum(self, digit_infile)

    def if_operator(self):
        # Parameters
        # Returns: A token which was returned by one of the helper functions

        tempOperator = ""

        while self.array_index < len(self.pascal_file):

            tempOperator += self.pascal_file[self.array_index]

            # check if single colon or assignment
            if self.pascal_file[self.array_index] == ":":
                return psh.help_caseOperator(self, tempOperator, self.pascal_file[self.array_index + 1])

            # check if <, <=, or !=
            elif self.pascal_file[self.array_index] == "<":
                return psh.check_lte_notequal(self, tempOperator, self.pascal_file[self.array_index + 1])

            # if greater than or gte
            elif self.pascal_file[self.array_index] == ">":
                return psh.help_caseOperator(self, tempOperator, self.pascal_file[self.array_index + 1])

            # check if a comment
            elif self.pascal_file[self.array_index] == "(":
                return psh.check_comment(self, tempOperator, self.pascal_file[self.array_index + 1])
            else:
                self.array_index += 1
                self.token.set_colNumber(self.token.get_colNumber() + 1)

                return self.opTokenBuilder(tempOperator)

    def if_comment(self, current, next):
        # Parameters
        # Returns: A comment token

        curr_comment = ""
        curr_comment += current + next
        self.array_index += 2
        self.token.set_colNumber(self.token.get_colNumber() + 2)

        while self.array_index < len(self.pascal_file) and \
                        self.pascal_file[self.array_index] != "*" and self.pascal_file[self.array_index + 1] != ")":

            curr_comment += self.pascal_file[self.array_index]
            psh.help_caseComment(self)

        if self.array_index >= len(self.pascal_file):
            return "Comment never completed"

        curr_comment += self.pascal_file[self.array_index] + self.pascal_file[self.array_index + 1]
        self.array_index += 2
        self.token.set_colNumber(self.token.get_colNumber() + 2)
        return self.token.buildToken(curr_comment, keywords.defined_keywords_list.get("comment").upper())

    def if_quote(self):
        # Parameters
        # Returns: A token of type string which was returned by the helper function

        built_string = ""

        built_string += self.pascal_file[self.array_index]
        self.array_index += 1
        self.token.set_colNumber(self.token.get_colNumber() + 1)

        while self.array_index < len(self.pascal_file):
            psh.help_caseQuote(self, built_string, self.pascal_file[self.array_index])

        # throw an error if the file ends before the string is completed
        if self.array_index >= len(self.pascal_file):
            return "String never completed"
