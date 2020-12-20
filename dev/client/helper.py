import json
def parse_action(action):
    try:
        verb = action.split(' ')[0].strip()
        if verb.lower() == 'send':
            start = action.index('[')
            end = action.index(']')
            nameorid = action[start+1:end].lower()
            action = action[end+1:]
            start = action.index('[')
            end = action.index(']')
            msg = action[start+1:end]
            if ',' in nameorid:
                [firstname, lastname] = nameorid.split(',')
                firstname = firstname.strip()
                lastname = lastname.strip()
                return {'type':'send', 'firstname': firstname, 'lastname': lastname, 'message': msg}
            else:
                return {'type': 'send', 'id':  nameorid, 'message': msg}
    except:
        return None
