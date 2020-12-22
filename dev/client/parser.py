import re
import MessageType.Request
r = re.compile('\W+')

#four types of message
# SEND [ID] ADD [FROM ACCOUNT] [TO ACCOUNT] [AMOUNT]
# SEND [ID] SUB [FROM ACCOUNT] [AMOUNT]
# SEND [EIFERT, THOMAS] [HELLO THOMAS]
# SEND [6398C613619E4DCA88220ACA49603D87] [HELLO THOMAS 2]
def parse_action(action):
    """ parse send message into request obj, the send message is left as it is, i.e., also includes brackets in order to avoid meta information added to the request obj
    :param action: user input string
    :return: request obj
    """
    req = None
    try:
        verb = action.split(' ')[0].strip()
        if verb.lower() == 'send':
            start = action.index('[')
            end = action.index(']')
            nameorid = action[start+1:end]
            action = action[end+1:]

            if ',' in nameorid:
                [firstname, lastname] = nameorid.split(',')
                firstname = firstname.strip().lower()
                lastname = lastname.strip().lower()
                req = {'firstname': firstname, 'lastname': lastname}
            else:
                req = {'id':  nameorid}
            action = action.strip()
            req['type'] = MessageType.Request.MES
            req['message'] = action
            # if action.index('[') == 0: # a dialogue message, strip the brackets
            #     end = action.index(']')
            #     msg = action[1:end]
            #     req['message'] = msg

            # else: # we have messages for transaction, leave the message as it is to be processed by the bank
                # if check_directive_format(action): #to avoid wrong message transfer
                # req['message'] = action
                # req['message_type'] = MessageType.Request.MES_BUS
                # else:
                #     req = None
            return req
    except:
        return None


if __name__ == '__main__':
    print(parse_action("SEND [EIFERT, THOMAS] [HELLO THOMAS]"))
    print(parse_action("SEND [6398C613619E4DCA88220ACA49603D87] [HELLO THOMAS 2]"))
    print(parse_action("SEND [6398C613619E4DCA88220ACA49603D87] ADD [accounta] [accountb] [1003]"))
    print(parse_action("SEND [6398C613619E4DCA88220ACA49603D87] SUB [accounta] [1003]"))



