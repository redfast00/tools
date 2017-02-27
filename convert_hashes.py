#!/usr/bin/env python3

# Takes a file of NTLMv1 hashes in mana format and spits out a
#  file of hashes in JtR or hashcat format.


import re
import argparse

class Hash():
    pass

class HashcatHash(Hash):
    @staticmethod
    def parse(line):
        m = re.match("(.*?)::::([0-9a-f]{48}):([0-9a-f]{16})", line)
        if m:
            return {"username": m.group(1), "response": m.group(2), "challenge": m.group(3)}
        else:
            raise ValueError("Couldn't find hash in line")

    @staticmethod
    def format(d):
        return "{username}::::{response}:{challenge}".format(
            username=d["username"],
            response=d["response"],
            challenge=d["challenge"])

class JohnHash(Hash):
    @staticmethod
    def parse(line):
        m = re.match("(.*?):\$NETNTLM\$([0-9a-f]{16})\$([0-9a-f]{48})", line)
        if m:
            return {"username": m.group(1), "response": m.group(3), "challenge": m.group(2)}
        else:
            raise ValueError("Couldn't find hash in line")

    @staticmethod
    def format(d):
        return "{username}:$NETNTLM${challenge}${response}".format(
            username=d["username"],
            response=d["response"],
            challenge=d["challenge"])

class ManaHash(Hash):
    @staticmethod
    def parse(line):
        m = re.match("CHAP\|(.*?)\|([0-9a-f:]{23})\|([0-9a-f:]{71})", line)
        if m:
            return {"username": m.group(1), "response": remove_colons(m.group(3)), "challenge": remove_colons(m.group(2))}
        else:
            raise ValueError("Couldn't find hash in line")

    @staticmethod
    def format(d):
        raise NotImplementedError

HASH_FORMATS = {
    'john': JohnHash,
    'hashcat': HashcatHash,
    'mana': ManaHash
}

def remove_colons(hexstr):
    """Removes colons from a string"""
    return ''.join(hexstr.split(':'))

def parse_args():
    """Parses command-line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('informat', action='store', choices=HASH_FORMATS)
    parser.add_argument('outfile', type=argparse.FileType('w'))
    parser.add_argument('outformat', action='store', choices=HASH_FORMATS)

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    input_hash_class = HASH_FORMATS[args.informat]
    output_hash_class = HASH_FORMATS[args.outformat]

    for line in args.infile:
        parsed_line = input_hash_class.parse(line)
        converted_line = output_hash_class.format(parsed_line)
        args.outfile.write(converted_line + '\n')
