#! /usr/bin/env python3
import random
import sys
import socket
import os
import datetime
from collections import deque
import threading
import select
# global ID, random_num
# ID =  str(random.randint(0, 100000))
# random_num = 0
conn_pool = []
#close_chatroom = 0
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
def update_last(owner, msg):
	#print('update')
	#print(msg)
	msg=f'update-last {owner} {msg}'
	server.sendall(msg.encode())
# 	chatroom.last_three.append(msg)
# 	if len(chatroom.last_three)>3:
# 		chatroom.last_three.popleft()

def create_chatroom(owner, chatrm_port):
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
	# chatroom.last_three[user]=deque()
	#chatroom.map[user]=dict()


	while True:
	# 	#print('start accept')

	 	conn, addr = chatrm_server.accept()
	 	user=conn.recv(1024).decode('utf-8').strip()
	 	chatroom.map[user]=conn
	 	threads = threading.Thread(target = chatroom_broadcast, args = (conn, owner,user))
	# 	threads.setDaemon(True)
	 	threads.start()

def chatroom_broadcast(conn, owner, user):
	while True:
		#print('broadcast')
		data = conn.recv(1024).decode('utf-8').strip()
		while data == '':
			data = conn.recv(1024).decode('utf-8').strip()
		if len(data.split('$', -1)) == 3: #leave
			leave_user = data.split('$', -1)[2]
			chatroom.map.pop(leave_user)
			return  #一個connection就用一個function，所以要整個拿掉
		x=datetime.datetime.now()
		h=x.hour
		m=x.minute
		msg=f'{user}[{h}:{m}]:{data}'
		print(msg)#owner自己看
		for man in chatroom.map:#給其它人看
			#if man != user:
			c=chatroom.map[man]
			c.sendall(msg.encode())
		update_last(owner, msg)
		# chatroom.last_three[owner].append(msg)#更新最新三句話
		# if len(chatroom.last_three)>3:
		# 	chatroom.last_three.popleft()

def join_chatroom(user, owner, target_port):
	chatroom_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
	#print('server receive')
	last_three_get=server.recv(1024).decode('utf-8').strip()
	last_three_get=last_three_get.split('$', -1)
	#print('receive finish')
	if last_three_get[0] != 'nothing':
		for msg in last_three_get:
			print(msg)
	#print('print finish')
#	leave = 0
	while True:

		#print('start infinite while')
		sockets_list = [sys.stdin, chatroom_server]
		read_socket, write_socket, error_socket = select.select(sockets_list,[],[])
		for socks in read_socket:
			#print('enter read socket')
			if socks == chatroom_server:
				msg=socks.recv(1024).decode('utf-8').strip()
				#msg=f'here {msg} here'
				if msg[-1] == '$':
					print("Welcome back to BBS.")
					chatroom_server.close()
					#leave = 1
					return
				else:
					print(msg)
			else:
				#print('pre-here')
				input_user=sys.stdin.readline()
				input_user=input_user.strip()
				sys.stdout.flush()
				if input_user == 'leave-chatroom':
					input_user = f'$leave-chatroom${user}'
					chatroom_server.sendall(input_user.encode())
					print('Welcome back to BBS.')
					print('we may have to reduce the owner chatroom.map')
					return
				else:
					chatroom_server.sendall(input_user.encode())
		#print('leave for loop')



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
		data = server.recv(1024).decode('utf-8').strip()
		data = data.split('$', -1)
		if len(data) > 1:
			print("********************************\n")
			print("**Welcome to the the chatroom.**\n")
			print("********************************\n")
			owner = data[1]
			msg=f'last-three {owner}'
			server.sendall(msg.encode())
			last_three_get=server.recv(1024).decode('utf-8').strip()
			#print('get three')
			last_three_get=last_three_get.split('$', -1)
			for msg in last_three_get:
				print(msg)

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
					#print('leave')
					#chatroom.chatrm[owner][1]=0 #close
					msg=f'leave-chatroom-from {owner}'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.map:
						#if man != owner:
						msg+='$'	
						c=chatroom.map[man]
						c.sendall(msg.encode())
					print("Welcome back to BBS")
					return
				elif input_owner == 'detach':
					break
				else:
					#print('here')

					msg=f'{owner}[{h}:{m}]:{input_owner}'
					update_last(owner,msg)
					for man in chatroom.map:
						#if man != owner:
						c=chatroom.map[man]
						c.sendall(msg.encode())
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
			owner = data[1]
			msg=f'last-three {owner}'
			server.sendall(msg.encode())
			#last_three_get=server.recv(1024).decode('utf-8').strip()
			last_three_get=server.recv(1024).decode('utf-8').strip()
			last_three_get=last_three_get.split('$', -1)
			#print('receive finish')
			if last_three_get[0] != 'nothing':
				for msg in last_three_get:
					print(msg)
			#chatroom.chatrm[owner][1]=1
			while True:
				input_owner=input()
				x=datetime.datetime.now()
				h=x.hour
				m=x.minute
				if input_owner == 'leave-chatroom':
					#close_chatroom =  1
					#chatroom.chatrm[owner][1]=0 #close
					msg=f'leave-chatroom-from {owner}'
					server.sendall(msg.encode())
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.map:
						#if man != user:
						c=chatroom.map[man]
						msg+='$'
						c.sendall(msg.encode())
					print("Welcome back to BBS")
					break
				elif input_owner == 'detach':
					break
				else:

					msg=f'{owner}[{h}:{m}]:{input_owner}'
					for man in chatroom.map:
						#if man != :owner
						c=chatroom.map[man]
						c.sendall(msg.encode())
					update_last(owner, msg)
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
				# 	print('just leave')
				# 	break
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

					##close_chatroom = 1
					#print('leave')
					#chatroom.chatrm[owner][1]=0 #close
					msg=f'leave-chatroom-from {owner}'
					server.sendall(msg.encode())
					#print('have send server')
					#input()
					msg=f'{owner}[{h}:{m}]:the chatroom is close.'
					for man in chatroom.map:
						#if man != owner:
						c=chatroom.map[man]
						msg+='$'						
						c.sendall(msg.encode())
						#print(f'send to {man}')
					print("Welcome back to BBS")
					#input()
					#leave = 1
					break
				elif input_owner == 'detach':
					break
				else:
					#print('here')
					
					msg=f'{owner}[{h}:{m}]:{input_owner}'
					update_last(owner,msg)
					for man in chatroom.map:
						#if man != owner:
						c=chatroom.map[man]
						c.sendall(msg.encode())

			
					
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
