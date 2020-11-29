from server.server_global import *
from message_function import *
def handle_start(res):
    type = res['type']
    if type == 'register':
        return handle_register(res)
    elif type == 'send':
        return handle_send(res)


def handle_register(res, conn, addr):

    # try:
        id = res['id']
        if id in users:
            return {'status': 1, 'text': 'you registered already'}
        firstname = res['firstname'].lower()
        lastname = res['lastname'].lower()
        pk = res['public']
        # save in users table
        users[id] = {'firstname': firstname, 'lastname': lastname, 'id': id, 'public': pk}

        # save name-id mapping
        if (firstname, lastname) in name2id:
            name2id[(firstname, lastname)].append(id)
        else:
            name2id[(firstname, lastname)] = [id]

        # save login status in connections
        # connections[addr] = id
        return {'status': 1, 'text': 'register ok'}
    # except (KeyError, AttributeError):
        return {'status': 0, 'text': 'please pass id, firstname, lastname and public key'}


def handle_send(res):
    try:
        msg = {'status': 1, 'message': res['message']}
        if 'id' in res:
            id = [res['id']]
        else:
            firstname = res['firstname'].lower()
            lastname = res['lastname'].lower()
            id = name2id[(firstname, lastname)]
        # print("id:" + str(id))
        id_online = []
        for i in id:
            if i in id2session:  # if user is not online
                id_online.append(i)
        if not len(id_online):  # if all users are not online
            return {'status': 0, 'text': 'user is not online'}
        for i in id_online:  # send message to every receiver
            sess = id2session[i]
            print(sess.user)
            s = sess.socket
            # TODO encrypt message
            msg['id'] = i
            msg['firstname'] = users[i]['firstname']
            msg['lastname'] = users[i]['lastname']
            print('resending msg to other user')
            msg = json.dumps(msg)
            s.sendall(format_message(msg))
        # res_msg = get_response(s)
        # TODO: send ack message to sender

    except (KeyError, AttributeError):
        return {'status': 0, 'text': 'please pass id/firstname, lastname and your message'}

    return {'status': 1, 'text': 'message sent'}
