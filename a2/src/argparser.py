import re

_RAND = 0
_SEQ = 1
_HIST = 2
_FREQ = 3
_OTP = 4


def parse_args(arg):
    types = {
        "rand": _RAND,
        "seq": _SEQ,
        "freq": _FREQ,
        "otp": _OTP
    }

    hsize = 0
    pstyle = _RAND

    x = re.match(r'hist\((\d*)\)', arg.lower())
    if x is not None:
        hsize = int(x.group(1))  # Get hsize captured in regex
        pstyle = _HIST
    elif arg.lower() in types.keys():
        pstyle = types.get(arg.lower())

    return pstyle, hsize
