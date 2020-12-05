#! /usr/bin/env python3
import random
import sys
import socket
import os
import datetime
from collections import deque
# global ID, random_num
# ID =  str(random.randint(0, 100000))
# random_num = 0
conn_pool = []
class Chatroom():
	def __init__(self):
		self.chatrm=dict()
		self.member=dict()
		self.map=dict()
		self.last_three=dict()
	
#last_three[owner]=deque()
#map[owner]=dict()
#map[owner][user]=conn
#member[owner]=[member1,member2,member3]
#chatrm[owner]=[port, open_or_not]  if open: 1   要檢查是int 或 str
chatroom=Chatroom()
def create_chatroom(user, chatrm_port):
	chatrm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	chatrm_server.bind(('127.0.0.1', chatrm_port))
	chatrm_server.listen(10)
	print("start to create chatroom...\n")
	print("********************************\n")
	print("** Welcome to the the chatroom. **\n")
	print("********************************\n")
	chatroom.chatrm[user]=[chatrm_port, 1]
	chatroom.member[user]=[]
	chatroom.member[user].append(user)
	chatroom.last_three[user]=deque()
def handle_chatroom_client(owner):
	while True:
		conn, addr = chatrm_server.accept()
		user=conn.recv(1024).decode('utf-8').strip()
		chatroom.map[owner][user]=conn
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
		for man in chatroom.member[owner]:#給其它人看
			if man != user:
				c=chatroom.map[owner][man]
				c.sendall(msg.encode())
		chatroom.last_three[owner].append(msg)#更新最新三句話
		if len(chatroom.last_three)>3:
			chatroom.last_three.popleft()

def join_chatroom(user, owner)
	chatroom_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	chatroom_server.connect((HOST, chatroom.chatrm[owner][0]))
	chatroom_server.sendall(user.encode())
	chatroom.member[owner].append(user)
	Handle_join_chatroom(chatroom_server, owner, user)

def Handle_join_chatroom(chatroom_server,owner,user)
	print("Action: connection to chatroom server.\n")
	print("********************************\n")
	print("** Welcome to the the chatroom. **\n")
	print("********************************\n")
	for msg in chatroom.last_three[owner]:
		print(msg)
	while True:
		sockets_list = [sys.stdin, chatroom_server]
		read_socket, write_socket, error_socket = select.select(sockets_list,[],[])
		for socks in read_socket:
			if socks == chatroom_server:
				msg=socks.recv(1024)
				msg=str(msg.decode())
				if chatroom.chatrm[owner][1] == 0:
					print("Welcome back to BBS.")
					chatroom_server.close()
			else:
				input_user=input()
				if input_user == 'leave-chatroom':
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
			for msg in chatroom.last_three[owner]:
				print(msg)
			owner = server.recv(1024).decode('utf-8').strip()
			while True:
				input_owner=input()
				if input_owner == 'leave-chatroom':
					chatroom.chatrm[owner][1]=0 #close
					msg='leave-chatroom-from owner'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.member[owner]:
						if man != user:
							c=chatroom.map[owner][man]
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
					for man in chatroom.member[owner]:
						if man != user:
							c=chatroom.map[owner][man]
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
					for man in chatroom.member[owner]:
						if man != user:
							c=chatroom.map[owner][man]
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
					for man in chatroom.member[owner]:
						if man != user:
							c=chatroom.map[owner][man]
							c.sendall(msg.encode())
					chatroom.last_three[owner].append(msg)
					if len(chatroom.last_three)>3:
						chatroom.last_three.popleft()
		else:
			print(data.decode('utf-8').strip())
	elif cmd[0] == 'create-chatroom':
		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		if data.decode('utf-8').strip() == '1':
			owner = server.recv(1024).decode('utf-8').strip()
			create_chatroom(owner, cmd[1])
			thread = threading.Thread(target = handle_chatroom_client, args(owner,))
			thread.start()
			while True:
				input_owner=input()
				if input_owner == 'leave-chatroom':
					chatroom.chatrm[owner][1]=0 #close
					msg='leave-chatroom-from owner'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.member[owner]:
						if man != user:
							c=chatroom.map[owner][man]
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
					for man in chatroom.member[owner]:
						if man != user:
							c=chatroom.map[owner][man]
							c.sendall(msg.encode())
					chatroom.last_three[owner].append(msg)
					if len(chatroom.last_three)>3:
						chatroom.last_three.popleft()
		else :
			print(data.decode('utf-8').strip())
	elif cmd[0] == 'join-chatroom'
		server.sendall(cmd_string.encode('utf-8'))
		data = server.recv(1024)
		if data.decode('utf-8').strip() == '1':
			user = server.recv(1024).decode('utf-8').strip()
			join_chatroom(user, cmd[1])
			thread = threading.Thread(target = )
	else :

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
