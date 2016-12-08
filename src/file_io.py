def read(filename):
    with open(filename) as f:
        to_return = f.read()

    return to_return

def write(filename, contents):
    with open(filename, 'w') as f:
        f.write(contents)