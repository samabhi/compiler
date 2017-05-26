# #############################################################################

# Helper functions for Scanner cases follow

# #############################################################################


def help_caseLetter(Scanner, tempWord):
    # Parameters
    #   * tempWord
    #       - a value that is only alphabetical
    # Returns: A token with tempword as the value and either 'id' or a keyword as the data type

    Scanner.token.set_colNumber(Scanner.token.get_colNumber() + len(tempWord))
    Scanner.array_index += len(tempWord)

    # check if the string is a reserved keyword
    if tempWord in Scanner.defined_keywords_list:
        return Scanner.tokenBuilder(tempWord, tempWord)
    # if not then it's a string literal
    else:
        return Scanner.tokenBuilder(tempWord, "id")


def help_caseNum(Scanner, digit):
    # Parameters
    #   * digit
    #       - a numerical value
    # Returns: A token with digit as the value and integer/real/range as the data type

    if "." in digit:
        temp_index = digit.find(".")

        if digit.count('.') == 1:
            real_number = float(digit)
            return Scanner.tokenBuilder(real_number, "real")
        elif digit.count('.') == 2:
            return Scanner.tokenBuilder(digit, "range")
        else:
            return "Invalid number format"
    # if not a real number or a range then it has to be an integer
    else:
        real_number = int(digit)
        return Scanner.tokenBuilder(real_number, "integer")


def help_caseOperator(Scanner, tempOperator, nextOperator):
    # Parameters
    #   * tempOperator
    #       - a value that is an operator
    # Returns: A token with an operator as the value and it's corresponding data type from keywords.py

    if nextOperator == "=":
        tempOperator += nextOperator
        Scanner.array_index += 2
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 2)
        return Scanner.opTokenBuilder(tempOperator)
    else:
        Scanner.array_index += 1
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 1)
        return Scanner.opTokenBuilder(tempOperator)


def check_lte_notequal(Scanner, tempOperator, nextOperator):
    # Parameters
    #   * tempOperator
    #       - a value that is an operator
    # Returns: A token with an operator as the value and it's corresponding data type from keywords.py

    if nextOperator == ">":
        tempOperator += nextOperator
        Scanner.array_index += 2
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 2)
        return Scanner.opTokenBuilder(tempOperator)
    elif nextOperator == "=":
        tempOperator += nextOperator
        Scanner.array_index += 2
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 2)
        return Scanner.opTokenBuilder(tempOperator)
    else:
        Scanner.array_index += 1
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 1)
        return Scanner.opTokenBuilder(tempOperator)


def check_comment(Scanner, tempOperator, nextChar):
    # Parameters
    #   * tempOperator
    #       - a value that is an operator
    # Returns: A token with an operator as the value and it's corresponding data type from keywords.py

    if nextChar == "*":
        return Scanner.if_comment(tempOperator, nextChar)
    else:
        Scanner.array_index += 1
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 1)
        return Scanner.opTokenBuilder(tempOperator)


def help_caseQuote(Scanner, tempString, current):
    # Parameters
    #   * tempString
    #       - a value that is a string
    # Returns: A token with a string data type

    # Check if it is the closing '
    if current == "\'":
        tempString += current
        Scanner.array_index += 1
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 1)
        return Scanner.tokenBuilder(tempString, "string")
    # else it is just another char
    else:
        tempString += current
        if current == "\n":
            Scanner.token.set_colNumber(0)
            Scanner.token.set_rowNumber(Scanner.token.get_rowNumber() + 1)
        else:
            Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 1)

        Scanner.array_index += 1


def help_caseComment(Scanner):
    # Parameters

    if Scanner.pascal_file[Scanner.array_index] == "\n":
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 0)
        Scanner.token.set_rowNumber(Scanner.token.get_rowNumber() + 1)
    else:
        Scanner.token.set_colNumber(Scanner.token.get_colNumber() + 1)

    Scanner.array_index += 1