#!/usr/bin/env python3

# Takes a file of NTLMv1 hashes in mana format and spits out a
#  file of hashes in JtR or hashcat format.


import sys
import re

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

def print_usage():
    print("Usage:")
    print("exportlog.py <informat> <infile> <outformat> <outfile>")

def remove_colons(hexstr):
    return ''.join(hexstr.split(':'))

if __name__ == '__main__':
    if (len(sys.argv) != 5) or (sys.argv[1] not in ['john', 'hashcat', 'mana']) or (sys.argv[3] not in ['john', 'hashcat']):
        print_usage()
        quit()
    import_format = sys.argv[1]
    export_format = sys.argv[3]
    with open(sys.argv[2], 'r') as infile, open(sys.argv[4], 'w') as outfile:
        for line in infile:
            if import_format == 'john':
                d = JohnHash.parse(line)
            elif import_format == 'hashcat':
                d = HashcatHash.parse(line)
            elif import_format == 'mana':
                d = ManaHash.parse(line)
            if export_format == 'john':
                outline = JohnHash.format(d)
            elif export_format == 'hashcat':
                outline = HashcatHash.format(d)
            outfile.write(outline + "\n")
