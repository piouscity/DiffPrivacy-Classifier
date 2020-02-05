from exceptions import BaseException

try:
    pass
except BaseException as e:
    print("{}: {}".format(e.code, e.detail))
except:
    print("Uncatched exeption")

