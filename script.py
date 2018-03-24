OP_0 = '00'
OP_FALSE = OP_0 # or 0100
OP_1 = '51'
OP_TRUE = OP_1

OP_IF = '63'
OP_NOTIF = '64'
OP_ELSE = '67'
OP_ENDIF = '68'
OP_VERIFY = '69'

OP_TOALTSTACK = '6b'
OP_FROMALTSTACK = '6c'
OP_DEPTH = '74'
OP_DROP = '75'
OP_DUP = '76'
OP_NIP = '77'
OP_OVER = '78'
OP_SWAP = '7c'
OP_2DUP = '6e'

OP_EQUAL = '87'
OP_EQUALVERIFY = '88'

OP_1ADD = '8b'
OP_1SUB = '8c'
OP_NOT = '91'
OP_0NOTEQUAL = '92'
OP_BOOLAND = '9a'
OP_BOOLOR = '9b'
OP_NUMEQUAL = '9c'
OP_NUMEQUALVERIFY = '9d'
OP_NUMNOTEQUAL = '9e'

def pushNum(num):
    if num == 0:
        return OP_0 # or 0100
    elif 0 < num <= 16:
        return chr(81 + num).encode('hex')
    elif num < 128:
        return '01' + chr(num).encode('hex')
    else:
        return None

def pushToStack(s):
    l = len(s)
    if l == 0:
        return OP_0
    elif l < 76:
        return (chr(l) + s).encode('hex')
    elif l < 256:
        return '4c' + (chr(l) + s).encode('hex')
    else:
        return None