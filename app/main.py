from parser import Parser
from target import BuildTarget

file = 'concurrent_makefile'


def main():
    lines = open(file, 'r').readlines()
    p = Parser(lines)
    p.parse()
    print(p.get_build_targets())


if __name__ == "__main__":
    main()
