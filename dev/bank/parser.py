from client.parser import parse_action
from bank.business import Directive

def parse_transaction(msg):
    try:
        obj = {}
        for key in ('fromAcc', 'toAcc', 'amount'):
            start = msg.index('[')
            end = msg.index(']')
            obj[key] = msg[start+1:end]
            msg = msg[end+1:]
        amt = obj['amount']
        obj['amount'] = float(amt)
    except:
        return None
    return obj

def parse_unit_operation(msg):
    try:
        obj = {}
        for key in ('fromAcc', 'amount'):
            start = msg.index('[')
            end = msg.index(']')
            obj[key] = msg[start + 1:end]
            msg = msg[end + 1:]
        amt = obj['amount']
        obj['amount'] = float(amt)
    except:
        return None
    return obj

def parse_directive(msg):
    obj = None
    msg = msg.strip()
    verb = msg[:3].lower()
    if verb == Directive.ADD:
        obj = parse_transaction(msg)
    elif verb == Directive.SUB:
        obj = parse_unit_operation(msg)
    else:
        return None
    if obj:
        obj['action'] = verb
    return obj

def is_normal_message(msg):
    return msg.startswith('[') and msg.endswith(']')

def is_valid_directive(msg):
    msg = msg.strip()
    verb = msg[:3].lower()
    repeat = 0
    if verb == Directive.ADD:
        repeat = 3
    elif verb == Directive.SUB:
        repeat = 2
    else: # not supported directive
        return False

    for _ in range(repeat):
        if '[' in msg and ']' in msg:
            start = msg.index('[')
            end = msg.index(']')
            if end > start:
                msg = msg[end+1:]
            else:
                return False
        else:
            return False
    if len(msg):
        return False
    return True

if __name__ == '__main__':
    action = parse_action("SEND [6398C613619E4DCA88220ACA49603D87] ADD [accounta] [accountb] [1003]")
    print(action)
    print(parse_directive(action['message']))
    action = parse_action("SEND [6398C613619E4DCA88220ACA49603D87] SUB [accounta] [1003]")
    print(action)
    print(parse_directive(action['message']))

