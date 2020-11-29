BUFLEN = 1024
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 52800

# user sessions
sessions = [] # list of session
socket2session = {} # mapping from socket to session
id2session = {}  # mapping from user to session

# manage user
users = {}  # stores all user information here, id -> info
name2id = {}  # (firstname,lastname) -> user id


# manage connection
# connections = {}  # addr -> {user: }
id2addr = {}
bytes_buffer = {}
received = {}
to_receive = {}