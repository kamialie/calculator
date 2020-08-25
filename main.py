from collections import deque
from enum import Enum

help_message = """The program calculates the sum of number
Valid format is includes addition and subtraction of multiple numbers as follows:
    8 + 1 or 1 - 9 + 111
Or single number:
    1 or -33
Also supports variable assignment:
    b = 1 + 10
And variable resolution(if they were defined before):
    a = b - 11
enter /help to see this message
enter /exit to exit the program"""


def command_handler(command):
    """Handle user commands"""
    if command == 'exit':
        print('Bye!')
        exit()
    elif command == 'help':
        print(help_message)
    else:
        raise ValueError('Unknown command')


class Precedence(Enum):
    HIGHER = 0
    SAME = 1
    LOWER = 2


class Operators:
    valid_operators = '+-*/'

    """True - target has higher precedence, False - target has same or lower precedence"""
    @staticmethod
    def check_precedence(target, base):
        if base == '+' or base == '-':
            if target == '*' or target == '/':
                return Precedence.HIGHER
            return Precedence.SAME
        if target == '*' or target == '/':
            return Precedence.SAME
        return Precedence.LOWER

    @staticmethod
    def get_plus_or_minus(arg):
        sign = 1
        for c in arg:
            if c == '-':
                sign *= -1
            elif c != '+':
                raise ValueError('Operator error')
        if sign:
            return '+'
        return '-'

    @staticmethod
    def is_operator(symbol):
        if symbol in Operators.valid_operators:
            return True
        return False

    @staticmethod
    def calculate(a, b, operator):
        if operator == '+':
            return a + b
        elif operator == '-':
            return a - b
        elif operator == '*':
            return a * b
        elif operator == '/':
            return a // b
        else:
            raise ValueError('Invalid operator')


class Variables:
    valid_symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    __store = {}

    @classmethod
    def add(cls, identifier, value):
        cls.__store[identifier] = value

    @classmethod
    def get(cls, identifier):
        if identifier not in cls.__store:
            raise ValueError('Unknown variable')
        return cls.__store[identifier]

    @classmethod
    def validate_identifier(cls, identifier):
        for ch in identifier:
            if ch not in cls.valid_symbols:
                raise ValueError('Invalid identifier')


class Expression:
    def __init__(self, line):
        self.__infix = deque()
        self.__postfix = deque()
        self._convert_to_infix(line)
        self._convert_to_postfix()

    def _add_operator(self, arg):
        if len(arg) != 1:
            self.__infix.append(Operators.get_plus_or_minus(arg))
        else:
            self.__infix.append(arg)

    def _add_operand(self, number):
        if len(self.__infix) != 0 and self.__infix[-1] == '-':
            if len(self.__infix) == 1:
                self.__infix[-1] = number * -1
            else:
                self.__infix[-1] = '+'
                self.__infix.append(number * -1)
        else:
            self.__infix.append(number)

    def _add_variable(self, var):
        try:
            Variables.validate_identifier(var)
        except Exception:
            raise Exception('Invalid assignment')
        number = Variables.get(var)
        self._add_operand(number)

    def _convert_to_infix(self, line):
        i = 0
        while i < len(line):
            if line[i] == '(' or line[i] == ')':
                self.__infix.append(line[i])
                i += 1
            elif line[i].isdigit():
                start = i
                while i < len(line) and line[i].isdigit():
                    i += 1
                self._add_operand(int(line[start:i]))
            elif line[i].isalpha():
                start = i
                while i < len(line) and line[i].isalpha():
                    i += 1
                self._add_variable(line[start:i])
            elif Operators.is_operator(line[i]):
                start = i
                while i < len(line) and Operators.is_operator(line[i]):
                    i += 1
                try:
                    self._add_operator(line[start:i])
                except Exception:
                    raise Exception('Invalid expression')
            else:
                i += 1

    def _convert_to_postfix(self):
        parenthesis = 0
        operators = deque()
        for element in self.__infix:
            if isinstance(element, int):
                self.__postfix.append(element)
            elif element == '(':
                parenthesis += 1
                operators.append(element)
            elif element == ')':
                parenthesis -= 1
                while len(operators) and operators[-1] != '(':
                    self.__postfix.append(operators.pop())
                if len(operators) != 0:
                    operators.pop()
            elif Operators.is_operator(element):
                if len(operators) == 0 or operators[-1] == '(':
                    operators.append(element)
                elif Operators.check_precedence(element, operators[-1]) == Precedence.HIGHER:
                    operators.append(element)
                else:
                    self.__postfix.append(operators.pop())
                    while len(operators) and Operators.check_precedence(element, operators[-1]) != Precedence.LOWER:
                        self.__postfix.append(operators.pop())
                    operators.append(element)
        while len(operators):
            self.__postfix.append(operators.pop())
        if parenthesis:
            raise Exception('Invalid expression')

    def get_result(self):
        result = deque()
        for element in self.__postfix:
            if isinstance(element, int):
                result.append(element)
            elif Operators.is_operator(element):
                b = result.pop()
                a = result.pop()
                result.append(Operators.calculate(a, b, element))
            else:
                raise Exception('Undefined element in postfix stack')
        return result.pop()

    def print_result(self):
        print(self.get_result())


while True:
    data = input().replace(' ', '')
    try:
        if data == '':
            continue
        elif data[0] == '/':
            command_handler(data[1:])
        else:
            if '=' in data:
                data = data.split('=')
                if len(data) != 2:
                    raise Exception('Invalid assignment')
                else:
                    expression = Expression(data[1])
                    Variables.validate_identifier(data[0])
                    Variables.add(data[0], expression.get_result())
            else:
                expression = Expression(data)
                # print(expression.__infix)
                # print(expression.__postfix)
                expression.print_result()
    except Exception as e:
        print(e.args[0])
