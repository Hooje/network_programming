#! /usr/bin/env python3
import random
import sys
import socket
import os
import datetime
from collections import deque
import threading
import select
import time
from signal import signal, SIGPIPE, SIG_DFL, SIG_IGN
signal(SIGPIPE, SIG_IGN)

# global ID, random_num
# ID =  str(random.randint(0, 100000))
# random_num = 0
#conn_pool = []
#close_chatroom = 0
detach = 0
map_lock=0
owner_close=0
#lock = 1
class Chatroom():
    def __init__(self):
        #self.chatrm=dict()
        #self.member=[]
        self.map=dict()
        self.last_three=deque()
    
#last_three[owner]=deque()
#map[user]=conn
#member=[member1,member2,member3]
#chatrm[owner]=[port, open_or_not]  if open: 1   要檢查是int 或 str
chatroom=Chatroom()
def print_last_three_owner():
    #print('print last three owner')

    for i in chatroom.last_three:
        print(i)
def print_last_three(chatroom_server):
    #print('print last three')
    msg=f'&'
    #print('want to get three')
    chatroom_server.sendall(msg.encode())
    chatroom_server.recv(1024)
    chatroom_server.sendall(msg.encode())
    last_three_get=chatroom_server.recv(1024).decode('utf-8').strip()
    last_three_get=last_three_get.split('$', -1)
    #print('get three finish')
    if last_three_get[0] != 'nothing':
        for mm in last_three_get:
            print(mm)
    chatroom_server.sendall('finish last three'.encode())
def update_last(owner, msg, conn):
    #print('update last')
    #print(msg)
    #msg=f'update-last {owner} {msg}'
    #conn.sendall(msg.encode())
    chatroom.last_three.append(msg)
    if len(chatroom.last_three)>3:
        chatroom.last_three.popleft()
    #print('update_last')
def update_last_owner(msg):
    #print('update last owner')
    chatroom.last_three.append(msg)
    if len(chatroom.last_three)>3:
        chatroom.last_three.popleft()
def create_chatroom(owner, chatrm_port):
    global map_lock
    #print('here')
    chatrm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chatrm_server.bind((HOST, int(chatrm_port)))
    chatrm_server.listen(10)
    print("start to create chatroom...\n")
    print("********************************\n")
    print("** Welcome to the the chatroom. **\n")
    print("********************************\n")
    #chatroom.chatrm[user]=[chatrm_port, 1]
    # print(chatroom.chatrm)
    # print(chatroom.chatrm[user])
    # chatroom.member[user]=[]
    # chatroom.member[user].append(user)
    #chatroom.last_three=deque()
    #chatroom.map[user]=dict()


    while True:
    #    #print('start accept')

        # x=datetime.datetime.now()
        # h=x.hour
        # m=x.minute
        conn, addr = chatrm_server.accept()
        user=conn.recv(1024).decode('utf-8').strip()
        conn.sendall('connect'.encode())
        # while(map_lock==1):
        #     pass
        # map_lock=1
        chatroom.map[user]=conn
        # print(f'sys[{h}:{m}]:{user} join us.')
        #map_lock=0
        threads = threading.Thread(target = chatroom_broadcast, args = (conn, owner,user))
    #    threads.setDaemon(True)
        threads.start()

def chatroom_broadcast(conn, owner, user):
    global detach, owner_close
    while True:
        have_leave =0
        not_update=0
        #print('broadcast')
        #while lock==1:
        data = conn.recv(1024).decode('utf-8').strip()
        conn.sendall(f'finish {data} finish'.encode())
        if data == '&':
            conn.recv(1024)
            #print('&')
            last = chatroom.last_three
            msg='nothing'
            #print(last)
            for i in range(len(last)):
                if i == 0:
                    msg=last[0]
                else:
                    #print(last[i])
                    msg+=f'${last[i]}'
            conn.sendall(msg.encode())
            conn.recv(1024)
            continue #不走下面

        speak=user
        #while data == '':
        #    conn.close()
        #    return
            #data = conn.recv(1024).decode('utf-8').strip()
        if data=='':
        #if len(data.split('$', -1)) == 3: #leave
            #leave_user = data.split('$', -1)[2]
            chatroom.map.pop(user)
            conn.close()
            if owner_close==1:
                return
            #map_lock = 0
            speak='sys'
            data=f'{user} leave us'
            not_update=1
            have_leave=1#離開就不再收了
            #return  #一個connection就用一個function，所以要整個拿掉
        
        x=datetime.datetime.now()
        h=x.hour
        m=x.minute
        #print(data[0:3])
        if data[0:3] == 'sys':
            #print('is sys')
            not_update=1
            msg=data

        else:
            msg=f'{speak}[{h}:{m}]:{data}'
            

        if detach == 0: #不是detach
            #print('not detach')
            #print(detach)
            print(msg)#owner自己看
        # while(map_lock==1):
        #     pass
        # map_lock=1
        for man in chatroom.map:#給其它人看
            if man != user:
                #print(f'try to send to {man}')
                c=chatroom.map[man]
                c.sendall(msg.encode())
        #map_lock=0
        if not_update ==0:
            update_last(owner, msg, conn)
        if have_leave==1:
            return
        # chatroom.last_three[owner].append(msg)#更新最新三句話
        # if len(chatroom.last_three)>3:
        #    chatroom.last_three.popleft()

def join_chatroom(user, owner, target_port):
    chatroom_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    chatroom_server.connect((HOST, int(target_port)))
    chatroom_server.sendall(user.encode())
    chatroom_server.recv(1024) #receive 'connect'
    #chatroom.member[owner].append(user)
    Handle_join_chatroom(chatroom_server, owner, user)

def Handle_join_chatroom(chatroom_server,owner,user):
    #print("Action: connection to chatroom server.\n")
    print("********************************\n")
    print("** Welcome to the the chatroom. **\n")
    print("********************************\n")
    x=datetime.datetime.now()
    h=x.hour
    m=x.minute
    mmsg=f'sys[{h}:{m}]:{user} join us.'
    chatroom_server.sendall(mmsg.encode())
    chatroom_server.recv(1024)
    #msg=f'last-three {owner}'
    #server.sendall(msg.encode())
    #print('server receive')
    print_last_three(chatroom_server)
    # last_three_get=server.recv(1024).decode('utf-8').strip()
    # last_three_get=last_three_get.split('$', -1)
    #print('receive finish')
    # if last_three_get[0] != 'nothing':
    #    for msg in last_three_get:
    #        print(msg)
    #print('print finish')
#    leave = 0
    while True:

        #print('start infinite while')
        sockets_list = [sys.stdin, chatroom_server]
        read_socket, write_socket, error_socket = select.select(sockets_list,[],[])
        for socks in read_socket:
            #print('enter read socket')
            if socks == chatroom_server:
                msg=socks.recv(1024).decode('utf-8').strip()
                #msg=f'here {msg} here'
                #print(msg)
                if msg=='finish':
                    print('msg is finish')
                    continue
                if msg:
                    if msg[-1] == '$':
                        print("Welcome back to BBS.")
                        #socks.sendall('ready to close'.encode())
                        chatroom_server.close()
                        #leave = 1
                        return
                
                print(msg)
            else:
                #print('pre-here')
                input_user=sys.stdin.readline()
                input_user=input_user.strip()
                sys.stdout.flush()
                if input_user == 'leave-chatroom':
                    chatroom_server.close()
                    #input_user = f'$leave-chatroom${user}'
                    #chatroom_server.sendall(input_user.encode())
                    print('Welcome back to BBS.')
                    #print('we may have to reduce the owner chatroom.map')
                    return
                else:
                    chatroom_server.sendall(input_user.encode())
                    chatroom_server.recv(1024)
        #print('leave for loop')



def HandleBBS(server):
    print("********************************\n")
    print("** Welcome to the BBS server. **\n")
    print("********************************\n")
    while True:
        input_cmd = input('% ')

        cmd_string = str(input_cmd.strip()) # delete \n
        cmd = cmd_string.split(' ', -1)  # string to list

#        input_cmd = f'{ID}${input_cmd}'
        exit_not = HandleClientCommand(server, cmd, cmd_string)#, input_cmd)
        if exit_not:
            break
def HandleClientCommand(server, cmd, cmd_string):#, input_cmd):
    global detach, map_lock, owner_close
    if cmd[0] == 'exit':
        time.sleep(3)
        server.sendall(cmd_string.encode('utf-8'))
        data = server.recv(1024)
        if len(data) == 0:
            server.close()
            return 1
        #return 1
    elif cmd[0] == 'attach':

        server.sendall(cmd_string.encode('utf-8'))
        data = server.recv(1024).decode('utf-8').strip()
        data = data.split('$', -1)
        if len(data) > 1:
            detach = 0
            #print('detach become to 0')
            print("********************************\n")
            print("**Welcome to the the chatroom.**\n")
            print("********************************\n")
            print_last_three_owner()
            # owner = data[1]
            # msg=f'last-three {owner}'
            # server.sendall(msg.encode())
            # last_three_get=server.recv(1024).decode('utf-8').strip()
            # #print('get three')
            # last_three_get=last_three_get.split('$', -1)
            # for msg in last_three_get:
            #    print(msg)

            while True:
                #print('while init')
                input_owner=sys.stdin.readline()
                input_owner=input_owner.strip()
                x=datetime.datetime.now()
                h=x.hour
                m=x.minute
                #test=f'here {input_owner} here'
                #print(test)
                #print("an input")
                if input_owner == 'leave-chatroom':
                    #msg=f'sys[{h}:{m}]:{user} leave us.'
                    #chatroom_server.sendall(msg.encode())
                    #print('leave')
                    #chatroom.chatrm[owner][1]=0 #close
                    owner=data[1]
                    msg=f'leave-chatroom-from {owner}'
                    server.sendall(msg.encode())
                    msg=f'sys[{h}:{m}]:the chatroom is close.$'
                    owner_close = 1
                    # while(map_lock==1):
                    #     pass
                    # map_lock=1
                    for man in chatroom.map:
                        #print(f'try to send to {man}')
                        #if man != owner:
                        #msg+='$'    
                        c=chatroom.map[man]
                        c.sendall(msg.encode())
                        
                    # map_lock=0
                    print("Welcome back to BBS")
                    return
                elif input_owner == 'detach':
                    print('Welcome back to BBS')
                    detach = 1
                    #print("detach = 1")
                    break
                else:
                    #print('here')
                    owner = data[1]
                    msg=f'{owner}[{h}:{m}]:{input_owner}'
                    update_last_owner(msg)
                    # while(map_lock==1):
                    #     pass
                    # map_lock=1
                    for man in chatroom.map:
                        #print(f'try to send to {man}')
                        #if man != owner:
                        c=chatroom.map[man]
                        c.sendall(msg.encode())
                    #map_lock=0
        else:
            print(data[0])

    elif cmd[0] == 'restart-chatroom':

        server.sendall(cmd_string.encode('utf-8'))
        data = server.recv(1024).decode('utf-8').strip()
        data = data.split('$', -1)
        if len(data) > 1:
            #close_chatroom = 0
            print("start to create chatroom…")
            print("********************************\n")
            print("**Welcome to the the chatroom.**\n")
            print("********************************\n")
            print_last_three_owner()
            # owner = data[1]
            # msg=f'last-three {owner}'
            # server.sendall(msg.encode())
            # #last_three_get=server.recv(1024).decode('utf-8').strip()
            # last_three_get=server.recv(1024).decode('utf-8').strip()
            # last_three_get=last_three_get.split('$', -1)
            # #print('receive finish')
            # if last_three_get[0] != 'nothing':
            #    for msg in last_three_get:
            #        print(msg)
            #chatroom.chatrm[owner][1]=1
            while True:
                input_owner=input()
                x=datetime.datetime.now()
                h=x.hour
                m=x.minute
                if input_owner == 'leave-chatroom':
                    #msg=f'sys[{h}:{m}]:{user} leave us.'
                    #chatroom_server.sendall(msg.encode())
                    #close_chatroom =  1
                    #chatroom.chatrm[owner][1]=0 #close
                    owner = data[1]
                    msg=f'leave-chatroom-from {owner}'
                    server.sendall(msg.encode())
                    msg=f'sys[{h}:{m}]:the chatroom is close.$'
                    owner_close=1
                    # while(map_lock==1):
                    #     pass
                    # map_lock=1
                    for man in chatroom.map:
                        #if man != user:
                        c=chatroom.map[man]
                        #msg+='$'
                        #print(f'try to send to {man}')
                        c.sendall(msg.encode())
                        #c.recv(1024)
                    #map_lock=0
                    print("Welcome back to BBS")
                    break

                elif input_owner == 'detach':
                    print('Welcome back to BBS')
                    detach = 1
                    break
                else:
                    owner = data[1]
                    msg=f'{owner}[{h}:{m}]:{input_owner}'
                    # while(map_lock==1):
                    #     pass
                    # map_lock=1
                    for man in chatroom.map:
                        #if man != :owner
                        #print(f'try to send to {man}')
                        c=chatroom.map[man]
                        c.sendall(msg.encode())
                    #map_lock=0
                    update_last_owner(msg)
        else:
            print(data[0])

    elif cmd[0] == 'create-chatroom':
        server.sendall(cmd_string.encode('utf-8'))
        data = server.recv(1024)
        data=data.decode('utf-8').strip()
        data=data.split('$', -1)
        if len(data) > 1:
            #print('success create')
            owner = data[1]
            #print(owner)
            #print(cmd[1])
            thread_create_server=threading.Thread(target = create_chatroom, args=(owner,cmd[1]))
            thread_create_server.setDaemon(True)
            thread_create_server.start()
            
            #leave = 0
            #print('before input owner')
            while True:
                # if leave == 1:
                #    print('just leave')
                #    break
                #print('input owner')
                input_owner=sys.stdin.readline()
                input_owner=input_owner.strip()
                x=datetime.datetime.now()
                h=x.hour
                m=x.minute
                #test=f'here {input_owner} here'
                #print(test)
                #print("an input")
                if input_owner == 'leave-chatroom':
                    #msg=f'sys[{h}:{m}]:{user} leave us.'
                    #chatroom_server.sendall(msg.encode())
                    ##close_chatroom = 1
                    #print('leave')
                    #chatroom.chatrm[owner][1]=0 #close
                    msg=f'leave-chatroom-from {owner}'
                    server.sendall(msg.encode())
                    #print('have send server')
                    #input()
                    msg=f'sys[{h}:{m}]:the chatroom is close.$'
                    owner_close=1
                    # while(map_lock==1):
                    #     pass
                    # map_lock=1
                    for man in chatroom.map:
                        #if man != owner:

                        #print(f'try to send to {man}')
                        c=chatroom.map[man]
                        #msg+='$'                        
                        c.sendall(msg.encode())
                    #map_lock=0
                        #print(f'send to {man}')
                    print("Welcome back to BBS")
                    #input()
                    #leave = 1
                    break
                elif input_owner == 'detach':
                    print('Welcome back to BBS')
                    detach = 1
                    #print('detach = 1')
                    break
                else:
                    #print('here')
                    
                    msg=f'{owner}[{h}:{m}]:{input_owner}'
                    update_last_owner(msg)
                    # while(map_lock==1):
                    #     pass
                    # map_lock=1
                    for man in chatroom.map:
                        #print(f'try to send to {man}')
                        #if man != owner:
                        c=chatroom.map[man]
                        c.sendall(msg.encode())
                    #map_lock=0

            
                    
        else:
            #print('didn create')
            print(data[0])
    elif cmd[0] == 'join-chatroom':
        server.sendall(cmd_string.encode('utf-8'))
        data = server.recv(1024)
        data=data.decode('utf-8').strip() 
        data=data.split('$', -1)
        if len(data) > 1:
            #print('join success')
            user, target_port=data[0], data[1]
            #join_chatroom(user, cmd[1], target_port)
            thread_join = threading.Thread(target = join_chatroom, args=(user,cmd[1],target_port))
            thread_join.start()
            thread_join.join()
        else :
            #print('join error')
            print(data[0])
    else:
        server.sendall(cmd_string.encode('utf-8'))
        data = server.recv(1024)
        
        data = str(data.decode('utf-8').strip())
        print(data)


HOST = sys.argv[1]
PORT = int(sys.argv[2])
addr = (HOST, PORT)
#server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.connect((HOST, PORT))
except socket.error:
    print('TCP error happened.')
    exit(1)
HandleBBS(server)
