"""This is just a quick script that helped me automate translating the information about structure and characteristics
of MIB tables into Python (now stored in :obj:`mib_generator.data.longdata`).
"""
a = '    {"name": "'
b = '", "type": ["'
c = '"], '
c = '", '
d = '], "mandatory": '
e = "},\n"
file = "out.txt"


def gen_data():
    """This method is an endless loop that asks the user to input various information which are then formatted into a string
    which is a literal representation of a Python dictionary and this string is then appended to a text file ``out.txt``.
    """
    while True:
        A = ""
        x = input("name: ")
        y = input("1/0=c/n: ")
        z = input("no: ")
        o = input("1/0=True/False: ")
        om = str(bool(int(o)))
        if y == "1":
            ym = "c"
        else:
            ym = "n"
        A = A + a + x + b + ym + c + z + d + om + e
        fil = open(file, "a")
        fil.write(A)
        fil.close()
