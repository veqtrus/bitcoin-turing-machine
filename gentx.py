import io, sys
from util import pack
from bitcoin import data as bitcoin_data
from script import *

def loadScript(filename):
    with io.open(filename, 'r') as f:
        return f.read().strip().decode('hex')

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'Usage:', sys.argv[0], '<compiledfile> <transaction> [<input0> [<inpout1> [...]]]'
        exit()
    script = loadScript(sys.argv[1])
    scriptsig = [pushToStack('' if i == '_' else i) for i in sys.argv[3:]] + [pushToStack(script)]
    scriptsig = ''.join(scriptsig).decode('hex')
    tx = dict(bitcoin_data.tx_type.unpack(sys.argv[2].decode('hex')))
    for input in tx['tx_ins']:
        input['script'] = scriptsig
    print bitcoin_data.tx_type.pack(tx).encode('hex')