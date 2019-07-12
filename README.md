# classproject-p2p-chat
Class project creating a P2P chat program in python. Only uses the command line. Designed with specifications detailed in class, in that the program will scan for other local chat clients and attempt to connect each other. Introduction to UDP packets, which are fast but do not guarantee transmission to destination.

Each instance of the program will have 4 threads, which house the client and server abilities. Server will keep track of which IPs are connected and who to send messages to. Client allows sending of message and client commands like "/quit" which will send a notice to other clients that this user is no longer connected and to not send messages to this IP.

Example Screenshot:
![Screenshot](https://github.com/GH-Edifire/classproject-p2p-chat/blob/master/Screenshot%20from%202017-10-26%2017-52-59.png)
