#!/usr/bin/python3
import threading
import time
import socket
import sys
import os
import re
from datetime import date

global HOST
global PORT
HOST = '127.0.0.1'
PORT = int(sys.argv[1])

conn_pool = []
#board=dict()
#board[NCTU]=[owner, dict()]
#board[NCTU][1][post]=[,,]
#map=dict()
#map[post_id]=[.....]  
#map[post_id]= -1  if post deleted

#comment[post_id]=[comment, commentor]
class Board():
	def __init__(self):
		self.board=dict()
		self.map=[-1] # use map.append
		self.comment=dict()
board=Board()
User=dict()
#User[name]=[name, email, password]
class Chatroom():
	def __init__(self):
		self.chatrm=dict()
#chatrm[owner]=[port, open_or_not]  if open: 1   要檢查是int 或 str
chatroom=Chatroom()
def Init():
	global server
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((HOST, PORT))
	server.listen(10)

def Write(conn, msg):
	conn.sendall(msg.encode())	

def HandleClient():
	while True:
		conn, addr = server.accept()
		conn_pool.append(conn)
		print("New connection.")
		threads = threading.Thread(target = HandleBBS, args = (conn,))
		threads.setDaemon(True)
		threads.start()

def CheckUserExist(name): #檢查有沒有這個user
	if name in User:
		return True
	return False

def CreateUser(name, email, passwd):
	User[name]=[name, email, passwd]

def GetUser(name):
	user=User[name]
	return user

def CheckBoardExist(board_name):
	if board_name in board.board:
		return True
	return False

def CreateBoard(board_name, moderator):
	board.board[board_name]=[moderator, dict()]

def GetBoardList():
	board_list=[]
	for board_name in board.board:
		board_list.append([board_name, board.board[board_name][0]])
	return board_list

def CreatePost(board_name, title, content, author, date):
	board.board[board_name][1]=[board_name, title, content, author, date]
	board.map.append([board_name, title, content, author, date])
	post_id=len(board.map)-1
	board.comment[post_id]=[] #有comment就append

def GetPostList(board_name):
	post_list=[]
	#print(len(board.map))
	#print(board.map)
	for i in range(len(board.map)-1): #第一個不算要減掉
		j=i+1 #serial number從1開始 , 第一個是 -1 , 無意義
		#print(board.map[i][0])
		if board.map[j] != -1 and board.map[j][0] == board_name:
			post_list.append([j, board.map[j][1], board.map[j][3], board.map[j][4]])
	return post_list

def GetPost(post_id):
	i=post_id 
	post=[post_id, board.map[i][0], board.map[i][1], board.map[i][2], board.map[i][3], board.map[i][4]]  # title content author date
	return post 

def CheckPostExist(post_id):

	if len(board.map) -1 < post_id:
		return False
	if board.map[post_id] == -1:
		return False
	return True

def DeletePost(post_id):
	board.map[post_id]= -1


def UpdatePostTitle(post_id, message):
	board.map[post_id][1] = message
	board.board[board.map[post_id][0]][1][1]=message #board.map[post_id][0]=board_name
	#print(board.map[post_id])
	#print(board.board[board.map[post_id][0]][1])

def UpdatePostContent(post_id, message):
	board.map[post_id][2] = message
	board.board[board.map[post_id][0]][1][2]=message
	#print(board.map[post_id])
	#print(board.board[board.map[post_id][0]][1])

def CreateComment(post_id, comment, commenter):
	board.comment[post_id].append([commenter, comment])

def GetPostCommentList(post_id):
	comment_list = board.comment[post_id]
	return comment_list

def GetCommentCount(post_id):
	return len(board.comment[post_id])
def create_chatroom(user,port):
	chatroom.chatrm[user]=[port, 1]#open
#def join_chatroom(user, owner, port):

def HandleCommand(conn, cmd, cmd_orig, login_status, login_user):
	msg = None
	if cmd[0] == 'register':
		if len(cmd) != 4:
			msg = 'Usage: register <username> <email> <password>\n'
		else:
			if CheckUserExist(cmd[1]):
				msg = 'Username is already used.\n'
			else:
				CreateUser(cmd[1], cmd[2], cmd[3])
				msg = 'Register successfully.\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'login':
		if len(cmd) != 3:
			msg = 'Usage: login <username> <password>\n'
		else:
			# 參數數量正確，檢查username & passwd & login status
			if login_status == True:
				msg = 'Please logout first.\n'
			else: 
				if CheckUserExist(cmd[1]):
					user = GetUser(cmd[1])
					if cmd[2] == user[2]:
						login_status = True
						login_user = cmd[1]
						msg = 'Welcome, ' + cmd[1] + '.\n'
					else:
						msg = 'Login failed.\n'
				else:
					msg = 'Login failed.\n'
		Write(conn, msg)
		return login_status, login_user, False
		
	elif cmd[0] == 'whoami':
		if len(cmd) != 1:
			msg = 'Usage: whoami\n'
		else:
			if login_status == False:
				msg = 'Please login first.\n'
			else:
				msg = login_user + '\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'logout':
		if len(cmd) != 1:
			msg = 'Usage: logout\n'
		else:
			if login_status == False:
				msg = 'Please login first.\n'
			elif chatroom.chatrm[login_user][1]==1:
				msg = 'Please do “attach” and “leave-chatroom” first'
			else:
				msg = 'Bye, ' + login_user + '.\n'
				login_user = None
				login_status = False
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'create-board':
		if len(cmd) != 2:
			msg = 'Usage: create-board <name>\n'
		else:
			if login_status == False:
				msg = 'Please login first.\n'
			else:
				if CheckBoardExist(cmd[1]):
					msg = 'Board already exists.\n'
				else:
					CreateBoard(cmd[1], login_user)
					msg = 'Create board successfully.\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'list-board':
		if len(cmd) == 1:
			board_list = GetBoardList()
			msg = 'Index\tName\tModerator\n'
			board_cnt = 0
			for board in board_list:
				board_cnt += 1
				msg += str(board_cnt) + '\t' + board[0] + '\t' + board[1] + '\n'

		elif len(cmd) == 2:
			board_list = GetBoardList()
			msg = 'Index\tName\tModerator\n'
			board_cnt = 0
			key = cmd[1][2:]
			for board in board_list:
				if re.search(key, board[0]) != None:
					board_cnt += 1
					msg += str(board_cnt) + '\t' + board[0] + '\t' + board[1] + '\n'

		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'create-post':
		if login_status == False:
			msg = 'Please login first.\n'
		else:
			cmd_orig_title = cmd_orig.find('--title')
			cmd_orig_content = cmd_orig.find('--content')
			if '--title' in cmd and '--content' in cmd and cmd.index('--title') < cmd.index('--content') and cmd[2] == '--title':
				if login_status == False:
					msg = 'Please login first.\n'
				else:
					if CheckBoardExist(cmd[1]):
						today = str(date.today())
						CreatePost(cmd[1], cmd_orig[cmd_orig_title + 8 : cmd_orig_content].strip(), cmd_orig[cmd_orig_content + 10 :].strip(), login_user, today)
						#+8  和  +10  是因為  --title 有七個字....
						msg = 'Create post successfully.\n'
					else:
						msg = 'Board does not exist.\n'
			else:
				msg = 'Usage: create-post <board-name> --title <title> --content <content>\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'list-post':
		if len(cmd) == 2:
			if CheckBoardExist(cmd[1]):
				msg = 'ID\t\tTitle\t\tAuthor\t\tDate\n'
				post_list = GetPostList(cmd[1])
				for post in post_list:
					day = post[3].split('-', -1)
					msg += str(post[0]) + '\t\t' + post[1] + '\t\t' + post[2] + '\t\t' + day[1] + '/' + day[2] + '\n'
			else:
				msg = 'Board does not exist.\n'

		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'read':
		if len(cmd) != 2:
			msg = 'Usage: read <post-id>\n'
		else:
			post_id = int(cmd[1])
			if CheckPostExist(post_id):
				post = GetPost(post_id)
				post_content = str(post[3]).replace('<br>', '\n')
				msg = 'Author\t:'
				msg += post[4] + '\nTitle\t:' + post[2] + '\nDate\t:' + post[5] + '\n--\n' + post_content + '\n--\n'
				comment_count = GetCommentCount(post_id)
				comment_list = GetPostCommentList(post_id)
				if comment_count != 0:
					for comment in comment_list:
						msg += comment[0] + ': ' + str(comment[1]).replace('<br>', '\n\t') + '\n'
			else:
				msg = 'Post does not exist.\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'delete-post':
		if login_status == False:
			msg = 'Please login first.\n'
		else:
			if len(cmd) != 2:
				msg = 'Usage: delete-post <post-id>\n'
			else:
				post_id = int(cmd[1])
				if CheckPostExist(post_id):
					post = GetPost(post_id)
					author = post[4]
					if login_user == author:
						DeletePost(post_id)
						msg = 'Delete successfully.\n'
					else:
						msg = 'Not the post owner.\n'
				else:
					msg = 'Post does not exist.\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'update-post':
		if login_status == False:
			msg = 'Please login first.\n'
		else:
			if  len(cmd) < 4 or (cmd[2] != '--title' and cmd[2] != '--content'):
				msg = 'Usage: update-post <post-id> --title/content <new>\n'
			else:
				post_id = int(cmd[1])
				if CheckPostExist(post_id):
					post = GetPost(post_id)
					author = post[4]
					if login_user == author:
						if cmd[2] == '--title':
							cmd_orig_title = cmd_orig.find('--title')
							UpdatePostTitle(post_id, cmd_orig[cmd_orig_title + 8:].strip())
						else:
							cmd_orig_content = cmd_orig.find('--content')
							UpdatePostContent(post_id, cmd_orig[cmd_orig_content + 10:].strip())
						msg = 'Update successfully.\n'
					else:
						msg = 'Not the post owner.\n'
				else:
					msg = 'Post does not exist.\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'comment':
		if login_status == False:
			msg = 'Please login first.\n'
		else:
			if len(cmd) < 3:
				msg = 'Usage: comment <post-id> <comment>\n'
			else:
				post_id = int(cmd[1])
				if CheckPostExist(post_id):
					cmd_orig_post_id = cmd_orig.find(cmd[1])
					CreateComment(post_id, cmd_orig[cmd_orig_post_id + len(cmd[1]):].strip(), login_user)
					msg = 'Comment successfully.\n'
				else:
					msg = 'Post does not exist.\n'
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'leave-chatroom-from':#因為在BBS打leave-chatroom 沒用
		chatroom.chatrm[cmd[1]][1]=0
	elif cmd[0] == 'attach':
		if login_status == False:
			msg = 'Please login first.\n'
		elif login_user not in chatroom.chatrm:
			msg = 'Please create-chatroom first.'
		else:
			msg='1'
			Write(conn,msg)
			msg=login_user
		Write(conn, msg)
		return login_status, login_user, False
	elif cmd[0] == 'list-chatroom':
		if login_status == False:
			msg = 'Please login first.\n'
		else:
			msg="Chatroom_name\tStatus\n"
			for room in chatroom.chatrm:
				if room[1] == 1:
					status="open"
				else:
					status="close"
				msg += f'{room}\t{status}'
		Write(conn, msg)
		return login_status, login_user, False
	elif cmd[0] == 'restart-chatroom':
		if login_status == False:
			msg = 'Please login first.\n'
		elif login_user not in chatroom.chatrm:
			msg = 'Please create-chatroom first.'
		elif chatroom.chatrm[login_user][1]==1:
			msg = 'Your chatroom is still running.'
		else:
			msg = '1'
			Write(conn, msg)
			msg = login_user
		Write(conn, msg)
		return login_status, login_user, False

	elif cmd[0] == 'create-chatroom':
		if login_status == False:
			msg = 'Please login first.\n'
		else:
			if login_user in chatroom.chatrm:
				msg='User has already created the chatroom'
			else: 
				create_chatroom()
				msg='1'
				Write(conn, msg)
				msg=login_user
		Write(conn, msg)
		return login_status, login_user, False
	elif cmd[0] == 'join-chatroom':
		if login_status == False:
			msg = 'Please login first.\n'
		elif cmd[1] not in chatroom.chatrm or chatroom.chatrm[cmd[1]][1] == '0' :
			msg = 'The chatroom does not exist or the chatroom is close.' 
		else:
			#join_chatroom()
			msg = '1'
			Write(conn,msg)
			msg = login_user
		Write(conn,msg)
		return login_status, login_user, False

	elif cmd[0] == 'exit':
		conn.close()
		conn_pool.remove(conn)
		return login_status, login_user, True

	else:
		msg = 'Command not found. Your command is ' + cmd[0] + '.\n'
		Write(conn, msg)
		return login_status, login_user, False

def HandleBBS(conn):
	login_status = False
	login_user = None
	exitornot = False
	# conn.sendall(b"********************************\n")
	# conn.sendall(b"** Welcome to the BBS server. **\n")
	# conn.sendall(b"********************************\n")
	while True:
		#conn.sendall(b'% ')
		data = conn.recv(1024)
		if len(data) == 0:
			conn.close()
			conn_pool.remove(conn)
			break
		cmd_orig = str(data.decode().strip())
		cmd = str(cmd_orig).split(' ', -1)
		login_status, login_user, exitornot = HandleCommand(conn, cmd, cmd_orig, login_status, login_user)
		if exitornot:
			break

if __name__ == "__main__":
	Init()
	thread = threading.Thread(target = HandleClient)
	thread.setDaemon(True)
	thread.start()
	while True:
		cmd = input()
		if cmd == 'exit':
			break
	
