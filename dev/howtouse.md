create conda environment with dependencies: ``conda env create --file env.yml``

run server:
``python server.py``

run client1: ``python client1.py``

run client2: ``python client2.py``

run bank instance ``python bank.py``

## Some notes:
The message that needs to be relayed by the server to the other user is encrypted with RSA using public key of the receiving partner, so only the receiving partner can view the message.    

After adding message header, like the type of message, the message is further encrypted with AES. The session key is shared when client establishes session with the server. The session key is generated on the server side by a random number and encrypted with client's public key, the client receives the session key after decrypting with his private key. This is to prevent third party from evedropping during the session and symmetric key is more efficient computationly when server handles multiple requests. This is similar to TLS layer.

The message format is relatively free as it uses json format instead of using bit level format, where each field is separated by some delimiter. The json format is deliberately chosen since the project requirements are expected to change during the course, so a fixed format might subject to heavy change of code. One of the weakness of json format is that it requires more encoding length and also requires much more decoding effort than the fixed format, however for this small project it is more than enough and the freedom it allows to express is also a huge advantage.

The bank instances inherits the client class. This allows maximum code reuse, only one handler is overwritten to deal with business logic.

The bank mainly serves to handle business logic, although normal messaging can also be carried out as is per project requirement. However, such situations are not common in real life, as transaction is sensitive, and having someone to communicate over this business channel is not sensible thing to do. Simply install more clients can easily solve the problem. 

The select package is used to monitor I/O change in the socket on both the server and client side. However, the server keeps track of all the incoming sockets and removes them once their corresponding session ends, while the client monitors only one session that is established with the server.
The multithread programming is also used on client's side to handle incoming message while the main thread is for user entering text in the GUI.





