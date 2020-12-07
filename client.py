#! /usr/bin/env python3
import random
import sys
import socket
import os
import datetime
from collections import deque
import threading
# global ID, random_num
# ID =  str(random.randint(0, 100000))
# random_num = 0
conn_pool = []
class Chatroom():
	def __init__(self):
		#self.chatrm=dict()
		#self.member=[]
		self.map=dict()
		#self.last_three=dict()
	
#last_three[owner]=deque()
#map[user]=conn
#member=[member1,member2,member3]
#chatrm[owner]=[port, open_or_not]  if open: 1   要檢查是int 或 str
chatroom=Chatroom()
def create_chatroom(user, chatrm_port):
	chatrm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	chatrm_server.bind(('127.0.0.1', int(chatrm_port)))
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
	# chatroom.last_three[user]=deque()
	#chatroom.map[user]=dict()
	return chatrm_server
def handle_chatroom_client(owner, chatrm_server):
	while True:
		conn, addr = chatrm_server.accept()
		user=conn.recv(1024).decode('utf-8').strip()
		chatroom.map[user]=conn
		threads = threading.Thread(target = chatroom_broadcast, args = (conn, owner,user))
		threads.setDaemon(True)
		threads.start()
def chatroom_broadcast(conn, owner, user):
	while True:
		data = conn.recv(1024).decode('utf-8').strip()
		x=datetime.datetime.now()
		h=x.hour
		m=x.minute
		msg=f'{user}[{h}:{m}]:{data}'
		print(msg)#owner自己看
		for man in chatroom.map:#給其它人看
			if man != user:
				c=chatroom.map[man]
				c.sendall(msg.encode())
		chatroom.last_three[owner].append(msg)#更新最新三句話
		if len(chatroom.last_three)>3:
			chatroom.last_three.popleft()

def join_chatroom(user, owner, target_port):
	chatroom_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#print(chatroom.chatrm)
	#print(chatroom.chatrm[owner])
	chatroom_server.connect((HOST, int(target_port)))
	chatroom_server.sendall(user.encode())
	#chatroom.member[owner].append(user)
	Handle_join_chatroom(chatroom_server, owner, user)

def Handle_join_chatroom(chatroom_server,owner,user):
	print("Action: connection to chatroom server.\n")
	print("********************************\n")
	print("** Welcome to the the chatroom. **\n")
	print("********************************\n")
	msg=f'last-three {owner}'
	server.sendall(msg.encode())
	last_three_get=server.recv(1024).decode('utf-8').strip()
	last_three_get=last_three_get.split('$', -1)
	for msg in last_three_get:
		print(msg)
	while True:
		sockets_list = [sys.stdin, chatroom_server]
		read_socket, write_socket, error_socket = select.select(sockets_list,[],[])
		for socks in read_socket:
			if socks == chatroom_server:
				msg=socks.recv(1024)
				msg=str(msg.decode())
				if msg == 'Welcome back to BBS':
					print("Welcome back to BBS.")
					chatroom_server.close()
				else:
					print(msg)
			else:
				input_user=input()
				if input_user == 'leave-chatroom':
					print('we may have to reduce the owner chatroom.map')
					break
				else:
					chatroom_server.sendall(input_user.encode())



def HandleBBS(server):
	print("********************************\n")
	print("** Welcome to the BBS server. **\n")
	print("********************************\n")
	while True:
		input_cmd = input('% ')

		cmd_string = str(input_cmd.strip()) # delete \n
		cmd = cmd_string.split(' ', -1)  # string to list

#		input_cmd = f'{ID}${input_cmd}'
		exit_not = HandleClientCommand(server, cmd, cmd_string)#, input_cmd)
		if exit_not:
			break
def HandleClientCommand(server, cmd, cmd_string):#, input_cmd):
	if cmd[0] == 'exit':
		server.sendall(cmd_string.encode('utf-8'))
		return 1
	elif cmd[0] == 'attach':

		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		if data.decode('utf-8').strip() == '1':
			print("********************************\n")
			print("**Welcome to the the chatroom.**\n")
			print("********************************\n")
			owner = server.recv(1024).decode('utf-8').strip()
			msg=f'last-three {owner}'
			server.sendall(msg.encode())
			last_three_get=server.recv(1024).decode('utf-8').strip()
			for msg in last_three_get:
				print(msg)
			while True:
				input_owner=input()
				if input_owner == 'leave-chatroom':
					#chatroom.chatrm[owner][1]=0 #close
					msg='leave-chatroom-from owner'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.map:
						if man != user:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					msg=f'Welcome to BBS'
					for man in chatroom.map:
						if man != user:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					
					print("Welcome back to BBS")
					break
				elif input_owner == 'detach':
					break
				else:
					x=datetime.datetime.now()
					h=x.hour
					m=x.minute
					msg=f'{owner}[{h}:{m}]:{data}'
					for man in chatroom.map:
						if man != user:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					chatroom.last_three[owner].append(msg)
					if len(chatroom.last_three)>3:
						chatroom.last_three.popleft()
		else:
			print(data.decode('utf-8').strip())

	elif cmd[0] == 'restart-chatroom':
		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		if data.decode('utf-8').strip() == '1':
			print("start to create chatroom…")
			print("********************************\n")
			print("**Welcome to the the chatroom.**\n")
			print("********************************\n")
			owner = server.recv(1024).decode('utf-8').strip()
			for msg in chatroom.last_three[owner]:
				print(msg)
			chatroom.chatrm[owner][1]=1
			while True:
				input_owner=input()
				if input_owner == 'leave-chatroom':
					chatroom.chatrm[owner][1]=0 #close
					msg='leave-chatroom-from owner'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.map:
						if man != user:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					print("Welcome back to BBS")
					break
				elif input_owner == 'detach':
					break
				else:
					x=datetime.datetime.now()
					h=x.hour
					m=x.minute
					msg=f'{owner}[{h}:{m}]:{data}'
					for man in chatroom.map:
						if man != user:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					chatroom.last_three[owner].append(msg)
					if len(chatroom.last_three)>3:
						chatroom.last_three.popleft()
		else:
			print(data.decode('utf-8').strip())
	elif cmd[0] == 'create-chatroom':
		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		data=data.decode('utf-8').strip()

		if data == '1':
			print('success create')
			owner = server.recv(1024).decode('utf-8').strip()
			#print(owner)
			#print(cmd[1])
			chatrm_server=create_chatroom(owner, cmd[1])
			thread = threading.Thread(target = handle_chatroom_client, args=(owner,chatrm_server))
			thread.start()
			while True:
				input_owner=input()
				if input_owner == 'leave-chatroom':
					chatroom.chatrm[owner][1]=0 #close
					msg='leave-chatroom-from owner'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.map:
						if man != user:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					print("Welcome back to BBS")
					break
				elif input_owner == 'detach':
					break
				else:
					x=datetime.datetime.now()
					h=x.hour
					m=x.minute
					msg=f'{owner}[{h}:{m}]:{data}'
					for man in chatroom.map:
						if man != owner:
							c=chatroom.map[man]
							c.sendall(msg.encode())
					chatroom.last_three[owner].append(msg)
					if len(chatroom.last_three)>3:
						chatroom.last_three.popleft()
		else:
			print('didn create')
			print(data)
	elif cmd[0] == 'join-chatroom':
		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		data=data.decode('utf-8').strip() 
		if data == '1':
			print('join success')
			msg=server.recv(1024).decode('utf-8').strip()
			msg=msg.split('$',-1)
			user, target_port=msg[0], msg[1]
			join_chatroom(user, cmd[1], target_port)
			#thread = threading.Thread(target = )
		else :
			print('join error')
			print(data)
	else:
		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		if len(data) == 0:
			server.close()
			return
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
