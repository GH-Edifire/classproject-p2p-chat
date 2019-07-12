#! /usr/bin/python
# A P2P UDP Chat Application
# Author: Keith Downer, Jonathan Kosasih, Justin Townsend
# Last Updated: 2017-10-26

# 4 threads in total should be created:
# 1 for sending ALIVE/update peerlist every x seconds
# 1 for "client": input & sending messages
# 1 for "server": receiving messages
# 1 for the startup routine which broadcasts to all local IPs


import socket
import time
import threading


### Definitions ###
port_range_begin = 12000
port_range_end   = 12001

ip_range_begin = 1  # sending to ip addr x.x.x.0 or x.x.x.255 not allowed
ip_range_end   = 254

# Timeout value
timeout = 9

# Acquire the ip address of the computer this program is running on.
local_ip = input("Input the local IP address: ")
print("LOCAL IP: ", local_ip)

# Create the list for storing peers.
peer_list = []

# Boolean variable that tells if we are done/quitting
done = False

# Set UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

### Scanning for peers ###
# Send “HELLO” messages to all local IP Addresses for each port in port range.
class Startup(threading.Thread):
    def run(self):
        global done
        global client_socket
        global local_ip
        # Inform client that we are searching for peers.
        print("Searching for peers, please wait ...")
        local_network = local_ip[:local_ip.rfind(".")+1]
        for i in range(ip_range_begin, ip_range_end+1):
            ip_addr = local_network + str(i)
            for port in range(port_range_begin, port_range_end+1):
               if(done):
                   self.exit()
               client_socket.sendto("HELLO".encode(), (ip_addr, port))

# update time for all peers + send ALIVE to everyone every "x" seconds
def alive():
    global done
    current_time = time.time()
    #print("time test ",(time.time() % 3))
    if(len(peer_list) > 0 and time.time() % 3 > 1 and done == False):
        index1 = int(0)
        for index1 in range(len(peer_list)):
            time_delta = time.time() - current_time
            tempTime = peer_list[index1][2]
            tempTime = tempTime - time_delta
            if(tempTime < 0):
                temp_peer = [peer_list[index1][0], False, tempTime]
            else:
                temp_peer = [peer_list[index1][0], True, tempTime]
                identity,port = peer_list[index1][0]
                #print("sending ALIVE to ",identity)
                client_socket.sendto("ALIVE".encode(), peer_list[index1][0])
    # timer_value == how often you want to update the list
    timer_value = 3
    if(not done):
        threading.Timer(3,alive).start()


# Create listen thread
class Server(threading.Thread):
    def run(self):        
        global peer_list
        global port_range_begin
        global timeout
        global client_socket
        global local_ip
        global done
        # Bind port
        client_socket.bind(("", port_range_begin))
        #print("Server Listening setup\n")
        i = 1
        current_time = time.time()
        alive()
        while(done == False):
            current_time = time.time()
            if(i == 1):
                #startup(client_socket,local_ip)  # its dead jim
                startup_thread = Startup()
                startup_thread.start()  # should have a startup.join() somewhere, but who cares
                i = i + 1

            recieve, senderAddress = client_socket.recvfrom(1024)
            message = recieve.decode()
            messageOpCode = message.split()[0]

            ### TEST RECIEVING MESSAGES ###
            #print("\trecieved: ", messageOpCode, " from ", senderAddress)
            ###-------------------------###

            # ACK received, check if they are in peer list, if not add to peer list
            if(messageOpCode == "ACK"):
                test = 0
                index1 = 0
                for index1 in range(len(peer_list)):
                    if(peer_list[index1][0] == senderAddress):
                        test = 1
                        break
                if(test == 0):
                    peer_list.append([senderAddress, True, timeout])
                    ip,port = senderAddress
                    print("\t" + ip + " found.")

                else:
                    peer_list.remove(peer_list[index1])
                    peer_list.append([senderAddress, True, timeout])
            # HELLO received, check if they are in peer list, if not add to peer list, then send ACK back
            if(messageOpCode == "HELLO" ):
                #print("entered Hello\n")
                test = 0
                index1 = 0
                if(len(peer_list) > 0):
                    for index1 in range(len(peer_list)):
                        if(peer_list[index1][0] == senderAddress):
                            test = 1
                            break
                if(test == 0):
                    peer_list.append([senderAddress, True, timeout])
                else:
                    peer_list.remove(peer_list[index1])
                    peer_list.append([senderAddress, True, timeout])
                identity,tempPort = senderAddress
                if(identity != local_ip):
                    print(identity + " has connected\n")
                client_socket.sendto("ACK".encode(), senderAddress)
            # MSG received, check peer list to update timeout, then display message and send ACK back
            if(messageOpCode == "MSG"):
                #print("entered MSG\n")
                test = 0
                index1 = 0
                for index1 in range(len(peer_list)):
                    if(peer_list[index1][0] == senderAddress):
                        test = 1
                        break
                if(test == 1):
                    peer_list.remove(peer_list[index1])
                    peer_list.append([senderAddress, True, timeout])
                else:
                    peer_list.append([senderAddress, True, timeout])
                identity,tempPort = senderAddress
                print(identity+">>> ",message[4:]+"\n")
                client_socket.sendto("ACK".encode(), senderAddress)
            # ALIVE received, update peer list
            if(messageOpCode == "ALIVE"):
                test = 0
                index1 = 0
                for index1 in range(len(peer_list)):
                    if(peer_list[index1][0] == senderAddress):
                        test = 1
                        break
                if(test == 1):
                    peer_list.remove(peer_list[index1])
                    peer_list.append([senderAddress, True, timeout])
                else:
                    peer_list.append([senderAddress, True, timeout])
            # LEAVE received, remove or flag the leaver so we don't send messages
            if(messageOpCode == "LEAVE"):
                test = 0
                index1 = 0
                for index1 in range(len(peer_list)):
                    if(peer_list[index1][0] == senderAddress):
                        test = 1
                        break
                if(test == 1):
                    peer_list.remove(peer_list[index1])
                identity,tempPort = senderAddress
                if(identity != local_ip):
                    print(identity + " has disconnected\n")
            # Reset message (might not be necessary)
            recieve = ""
            
class Client(threading.Thread):
    def run(self):
        global peer_list
        global client_socket
        global done

        print("Client initiated: type in your message\n")
        print("Type \quit to exit.\n")
        done = False
        index1 = int(0)
        while(done == False):
            message = input()
            # check message first
            # if regular message, append MSG to front then send message to all members of list
            # if "\quit" start disconnect process
            if(message == "\quit"):
                #start disconnect
                if(len(peer_list) > 0):
                    #print(peer_list)
                    # FIXME: unknown bug related to duplicated non-sent messages and index out of range thingy
                    for index1 in range(len(peer_list)):
                        client_socket.sendto("LEAVE".encode(), peer_list[index1][0])
                done = True
                client_socket.close()
                print("Quitting out...\n")
                break;
            else:
                message = "MSG " + message
                # start send to all members
                #print(message)
                if(len(peer_list) > 0):
                    for index1 in range(len(peer_list)):
                        client_socket.sendto(message.encode(), peer_list[index1][0])
                else:
                    print("Nobody else is in the chat\n")
                        
# Main Body
#print("Starting server\n")
server = Server()
server.start()

# wait 5 seconds for server to finish setting up, then start client
time.sleep(5)
#print("Starting client\n")
client = Client()
client.start()

# sync up server and client threads
server.join()
client.join()
