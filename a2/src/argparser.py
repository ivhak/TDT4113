'''
Helper for parsing of arguments
'''

import re


def parse_args(arg):
    ''' Parse the arguments passes to the program'''
    types = {
        "rand": 0,
        "seq": 1,
        "hist": 2,
        "freq": 3,
        "otp": 4
    }

    hsize = 0
    pstyle = 0

    reg_match = re.match(r'hist\((\d*)\)', arg.lower())
    if reg_match is not None:
        hsize = int(reg_match.group(1))  # Get hsize captured in regex
        pstyle = types.get('hist')
    elif arg.lower() in types.keys():
        pstyle = types.get(arg.lower())

    return pstyle, hsize
