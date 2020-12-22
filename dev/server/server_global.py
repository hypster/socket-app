BUFLEN = 1024
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 52800

SESSION_TAG = 'session_tag'

# online info
sessions = [] # list of session
socket2session = {} # mapping from socket to session
id2session = {}  # mapping from user to session
# id2addr = {}

# manage user
users = {}  # stores all user information here, id -> info
name2id = {}  # (firstname,lastname) -> user id


bytes_buffer = {}
received = {}
to_receive = {}