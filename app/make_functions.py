import re


def subst(arguments: str) -> str:
    original, substitute, text = arguments.split(',')
    return re.sub(original, substitute, text)


def patsubst(arguments: str):
    pattern, substitute, text = arguments.split(',')
    pass