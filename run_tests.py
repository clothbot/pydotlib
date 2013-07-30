import pydotlib as dotlib
lib=dotlib.PLYPair()
lib.set_lexer(dotlib.create_lexer())
lib.set_parser(dotlib.create_parser())

print("Testing tests/library.lib")
lib.parse_file('tests/library.lib')
print(dir(lib))
print(lib.result)

print("Testing tests/attributes.lib")
lib.parse_file('tests/attributes.lib')
print(dir(lib))
print(lib.result)

print("Testing tests/hierarchy.lib")
lib.parse_file('tests/hierarchy.lib')
print(dir(lib))
print(lib.result)

