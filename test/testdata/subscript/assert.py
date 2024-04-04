import sys
data = sys.stdin.read()

# if this is false, it will throw an exception which will cause the test to fail
assert data == "key1=val1\nkey2=val2\n"
