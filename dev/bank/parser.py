from client.parser import parse_action


def parse_transaction(obj, msg):
    for key in ('fromAcc', 'toAcc', 'amount'):
        start = msg.index('[')
        end = msg.index(']')
        obj[key] = msg[start+1:end]
        msg = msg[end+1:]
    amt = obj['amount']
    if amt.isdecimal():
        obj['amount'] = int(amt)
    else:
        obj = None
    return obj

def parse_unit_operation(obj, msg):
    for key in ('fromAcc', 'amount'):
        start = msg.index('[')
        end = msg.index(']')
        obj[key] = msg[start + 1:end]
        msg = msg[end + 1:]
    amt = obj['amount']
    if amt.isdecimal():
        obj['amount'] = int(amt)
    else:
        obj = None
    return obj

def parse_directive(msg):
    obj = {}
    msg = msg.strip()
    verb = msg[:3].lower()
    obj['action'] = verb
    repeat = 0
    if verb == 'add':
        parse_transaction(obj, msg)
    elif verb == 'sub':
        parse_unit_operation(obj, msg)
    return obj

def check_directive_format(msg):
    msg = msg.strip()
    verb = msg[:3].lower()
    repeat = 0
    if verb == 'add':
        repeat = 3
    elif verb == 'sub':
        repeat = 2
    else: # not supported directive
        return False

    for _ in range(repeat):
        start = msg.index('[')
        end = msg.index(']')
        if end > start:
            msg = msg[end+1:]
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

