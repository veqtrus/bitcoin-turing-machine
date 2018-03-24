import io, sys
from util import pack
from bitcoin import data as bitcoin_data
from script import *

INF_TAPE = False

class Network:
    ADDRESS_VERSION = 0

    def __init__(self, testnet=True):
        if testnet:
            self.ADDRESS_VERSION = 196
        else:
            self.ADDRESS_VERSION = 5
        
class TuringMachine:
    name = ''
    init = 0
    accept = []
    transitions = []

def write(val):
    return OP_NIP + pushToStack(val) + OP_SWAP

def move(direction):
    if direction < 0:
        if INF_TAPE:
            res = [
                OP_FROMALTSTACK,
                OP_DUP, OP_0, OP_NUMEQUAL, OP_IF,
                    OP_0,
                OP_ELSE,
                    OP_1SUB,
                    OP_FROMALTSTACK,
                OP_ENDIF,
                OP_SWAP,
                OP_TOALTSTACK,
                OP_SWAP
            ]
        else:
            res = [OP_FROMALTSTACK, OP_SWAP]
    elif direction > 0:
        if INF_TAPE:
            res = [
                OP_SWAP,
                OP_FROMALTSTACK, OP_1ADD,
                OP_TOALTSTACK, OP_TOALTSTACK,
                OP_DEPTH, OP_1, OP_NUMEQUAL, OP_IF,
                    OP_0, OP_SWAP,
                OP_ENDIF
            ]
        else:
            res = [OP_SWAP, OP_TOALTSTACK]
    else:
        res = []
    return ''.join(res)

def execute(curState, input, nextState, output, movement):
    return ''.join([
        OP_2DUP,
        pushNum(curState), OP_NUMEQUAL,
        OP_SWAP,
        pushToStack(input), OP_EQUAL,
        OP_BOOLAND, OP_IF,
            write(output), 
            move(movement),
            OP_DROP, pushNum(nextState),
        OP_ENDIF
    ])

def checkAccept(state):
    return OP_OVER + pushNum(state) + OP_NUMEQUAL + OP_BOOLOR

def clean():
    return OP_DEPTH + OP_0NOTEQUAL + OP_IF + OP_DROP + OP_ENDIF

def main(tm, loopcount, cleancount):
    exe = ''.join(execute(*tr) for tr in tm.transitions)
    return ''.join([
        OP_0, OP_TOALTSTACK, pushNum(tm.init)
    ] + [exe for _ in range(loopcount)] + [
        OP_FALSE
    ] + [checkAccept(st) for st in tm.accept] + [
        OP_VERIFY
    ] + [clean() for _ in range(cleancount)] + [
        OP_TRUE
    ])

def tmFromFile(filename):
    tm = TuringMachine()
    with io.open(filename, 'r') as f:
        states = []
        tr = []
        for ln in f:
            line = ln.split('//')[0].strip()
            if len(line) > 0:
                spl = [p.strip() for p in line.split(',')]
                conf = [p.strip() for p in line.split(':')]
                if len(conf) > 1:
                    if conf[0] == 'name':
                        tm.name = conf[1]
                    elif conf[0] == 'init':
                        tm.init = conf[1]
                    elif conf[0] == 'accept':
                        tm.accept = [p.strip() for p in conf[1].split(',')]
                else:
                    if len(tr) == 0:
                        tr = spl
                    else:
                        tr += spl
                        if len(tr) != 5:
                            print 'error: ' + line
                            exit()
                        if tr[0] not in states:
                            states.append(tr[0])
                        if tr[2] not in states:
                            states.append(tr[2])
                        tr[0] = states.index(tr[0])
                        tr[2] = states.index(tr[2])
                        if tr[4] == '<':
                            tr[4] = -1
                        elif tr[4] == '>':
                            tr[4] = 1
                        elif tr[4] == '-':
                            tr[4] = 0
                        else:
                            print 'error: ' + line
                            exit()
                        if tr[1] == '_':
                            tr[1] = ''
                        if tr[3] == '_':
                            tr[3] = ''
                        tm.transitions.append(tr)
                        tr = []
        tm.init = states.index(tm.init)
        tm.accept = [states.index(a) for a in tm.accept]
        return tm

def toFundingAddress(script, testnet=True):
    hsh = bitcoin_data.hash160(script.decode('hex'))
    return bitcoin_data.pubkey_hash_to_address(hsh, Network(testnet))

if __name__ == '__main__':
    loopcount = 10
    cleancount = 10
    if len(sys.argv) <= 3:
        print 'Usage:', sys.argv[0], '<sourcefile> <loopcount> <cleancount>'
        exit()
    if len(sys.argv) > 3:
        loopcount = int(sys.argv[2])
        cleancount = int(sys.argv[3])
        tm = tmFromFile(sys.argv[1])
        print 'tm.name:'
        print tm.name
        print 'tm.init:'
        print tm.init
        print 'tm.accept:'
        print tm.accept
        print 'tm.transitions:', str(len(tm.transitions))
        print tm.transitions
        print
        script = main(tm, loopcount, cleancount)
        print 'script:', str(len(script) / 2)
        print
        print script
        print
        print 'address:'
        print toFundingAddress(script, '--mainnet' not in sys.argv)