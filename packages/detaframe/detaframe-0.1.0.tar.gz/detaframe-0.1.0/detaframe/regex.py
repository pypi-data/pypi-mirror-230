import re
from collections import UserString


NUMBER_PATTERN = re.compile(r'\d+[.,]\d+|\d+')
DIGIT_PATTERN = re.compile(r'\d')
WORD_PATTERN = re.compile(r'\w+[-\d]\w+|\w+')
LETTER_PATTERN = re.compile(r'\w')

def findall_numbers(value: str) -> list[str]:
    return NUMBER_PATTERN.findall(value)


def findall_digits(value: str) -> list[str]:
    return DIGIT_PATTERN.findall(value)

def find_words(value: str) -> list[str]:
    return WORD_PATTERN.findall(value)

def find_letters(value: str) -> list[str]:
    return LETTER_PATTERN.findall(value)


def groupdict(pattern: re.Pattern, string: str):
    if match:= pattern.search(string):
        return match.groupdict()
    return {}

class Regex(UserString):
    
    @classmethod
    def groups(cls, string: str):
        if match:= cls.pattern().search(string):
            return match.groupdict()
        return {}
    
    @classmethod
    def pattern(cls) -> re.Pattern:
        return NotImplemented
    
    
    def asjson(self):
        return self.data
    
    
    
if __name__ == '__main__':
    print(find_letters('beija-flor saudade vilão a'))