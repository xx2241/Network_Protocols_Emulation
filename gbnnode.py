import socket
import sys
import json
import time
import random
import Queue
from time import localtime, strftime
from threading import Thread

### message: input string
### data: character
### packet: data or ack with header of sequence number
### ack: True or False
### received_seq_list: True or False


class MyException(Exception): 
	pass

class Timer():
    def __init__(self):
        self.time = None
        self.status = False
    def start(self):
        self.time = time.time()
        self.status = True
    def stop(self):
        self.status = False
    def timeout(self):
        return self.status and (time.time()-self.time)>0.5


def initialization():
	if len(sys.argv) == 6:
		try:
			self_port,peer_port,window_size = int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
		except:
			raise MyException("port number and window size should be integer")
			sys.exit()
		if sys.argv[4]!='-d' and sys.argv[4]!='-p':
			raise MyException('-d for deterministic way to drop packet, -p for probabilistic way to drop packet')
			sys.exit()
		else:
			drop_mode = sys.argv[4]
			drop_value = float(sys.argv[5])
	if len(sys.argv)!=6:
		raise MyException("please input as the following format:\n>>> python gbnnode.py <self_port> <peer_port> <window_size> [-d <value_of_n>|-p <value_of_n>]")
		sys.exit()
	return self_port,peer_port,window_size,drop_mode,drop_value

def input_message(messageQ):
	while True:
		try:
			print('node> '),
			data = raw_input()
			if data.startswith('send '):
				message = data[5:]
				messageQ.put(message)
			else:
				raise MyException("please input as the following format:\n>>> send <message>")
				sys.exit()
		except Exception as x: 
			print(str(x))
			sys.exit()


def put_into_buffer(messageQ,data_buffer):
	### does this need one more thread?
	while True:
		message = messageQ.get()
		window_list['message_length'] = window_list['message_length']+len(message)
		for i in range(0,len(message)):
			sequence_number = window_list['message_length']-len(message)+i
			data = message[i]
			data_buffer[window_list['message_length']-len(message)+i] = {'seq':sequence_number,'data':str(data),'ack':False}

def get_from_buffer(sequence_number, data_buffer):
	return data_buffer[sequence_number]

def remove_from_buffer(packet,data_buffer):
	data_buffer[packet['seq']] = None ##### test if 32 bit can be used like this!!!!!!

def send_packet(packet,peer_port):
	s.sendto(json.dumps(packet), ('',peer_port))
	if packet['ack'] == False:
		print('['+str(time.time())+']'+'packet'+str(packet['seq'])+' '+packet['data']+ ' sent')
	if packet['ack'] == True:
		print('['+str(time.time())+']'+'ACK'+str(packet['seq'])+' sent, expecting packet'+str(packet['seq']+1))

def discard_packet(received_number_list,packet,drop_mode, drop_value):
	### return boolean value, True: discard, False: not_discard
	if drop_mode == '-d':
		if (received_number_list[0]) % int(drop_value) != 0:
			return False
		else:
			if packet['ack'] == False:
				print('['+str(time.time())+']'+'packet'+str(packet['seq'])+' '+packet['data']+ ' discarded')
			elif packet['ack'] == True:
				print('['+str(time.time())+']'+'ACK'+str(packet['seq'])+' discarded')
			return True
	if drop_mode == '-p':
		if random.random() > drop_value:
			return False
		else:
			if packet['ack'] == False:
				print('['+str(time.time())+']'+'packet'+str(packet['seq'])+' '+packet['data']+ ' discarded')
			elif packet['ack'] == True:
				print('['+str(time.time())+']'+'ACK'+str(packet['seq'])+' discarded')
			return True

def loss_rate_calculation(dropped, total):
	loss_rate = float(dropped)/total
	print('[Summary] '+str(dropped)+'/'+str(total)+' packets dropped, loss rate = '+str(loss_rate))
	print('node> '),
	sys.stdout.flush()


					
def send(peer_port,window_size,drop_mode,drop_value,ack_list,data_buffer,timer, window_list):

	### have input
	while True:
		if timer.timeout() == True:
			print('['+str(time.time())+']'+'packet'+str(window_list['base']) + ' timeout')
			for i in range(window_list['base'],window_list['nextseq']): ## python it means to nextseq - 1
				packet = get_from_buffer(i,data_buffer)
				send_packet(packet,peer_port)
			timer.start()
		if window_list['nextseq'] < window_list['base'] + window_size:
			if data_buffer[window_list['nextseq']] != None:
				packet = get_from_buffer(window_list['nextseq'],data_buffer)
				window_list['nextseq'] = window_list['nextseq'] + 1
				send_packet(packet,peer_port)
				timer.start()


def receive(peer_port,timer_list,window_list,data_buffer,received_seq_list,drop_mode,drop_value):
	received_number_list = [0]
	dropped = 0
	while True:
		data = None
		clientaddress = None
		try:
			data, clientaddress = s.recvfrom(2048)
		except socket.error:
			continue
		packet = json.loads(data)
		if packet['ack']==False and packet['seq'] == -2:
				loss_rate_calculation(dropped,received_number_list[0])
				timer.stop()
		else:
			received_number_list[0] = received_number_list[0] + 1
			if discard_packet(received_number_list,packet,drop_mode,drop_value) == False:
				if packet['ack'] == False and packet['seq'] != -2:
					### receiver
					print('['+str(time.time())+']'+'packet'+str(packet['seq'])+' '+packet['data']+ ' received')
					if packet['seq'] == 0 or received_seq_list[packet['seq']-1] == True:
						ack_packet = {'seq':packet['seq'],'data':None,'ack':True}
						received_seq_list[packet['seq']] = True
						send_packet(ack_packet,peer_port)
					else:  #### there are not received packet before this packet
						for i in range(len(received_seq_list)):
							if received_seq_list[i] == False:
								last_received_seq = i-1
								break
						ack_packet = {'seq':last_received_seq,'data':None,'ack':True}
						send_packet(ack_packet,peer_port)


				elif packet['ack'] == True:
					### sender
					print('['+str(time.time())+']'+'ACK'+str(packet['seq'])+' received, window moves to '+str(packet['seq']+1))
					if data_buffer[packet['seq']] == None:
						pass
					else: ### ack means all previous packet has been received
						data_buffer[packet['seq']] = None
						window_list['base'] = packet['seq'] + 1
						if window_list['base'] != window_list['nextseq']:
							timer.start()
						elif window_list['base'] == window_list['nextseq']:
							timer.stop()
							if window_list['base'] == window_list['message_length']:
								loss_rate_calculation(dropped,received_number_list[0])
								timer.stop()
								s.sendto(json.dumps({'seq':-2,'data':None,'ack':False}),('',peer_port))

						
			else:
				dropped = dropped + 1


			### ignore duplicate ack	


if __name__ == '__main__':
	try:
		### put all these into a loop
		self_port,peer_port,window_size,drop_mode,drop_value = initialization()	
		data_buffer = [None] * 2000 ### think about modify it to a fixed length array
		window_list = {'base':0, 'nextseq':0, 'message_length':0,'expected':0}
		# timer_list = {'timeout':False, 'reset':False, 'stop':False} ## record timer status
		timer = Timer()
		ack_list = {'seq':-1,'status':False}
		received_seq_list = [False] * 2000
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('',self_port))
		t1 = Thread(target=send, args=(peer_port,window_size,drop_mode,drop_value,ack_list,data_buffer,timer, window_list))
		t2 = Thread(target=receive,args=(peer_port,timer,window_list,data_buffer,received_seq_list,drop_mode,drop_value))
		t1.setDaemon(True)
		t2.setDaemon(True)	
		t1.start()
		t2.start()
		messageQ = Queue.Queue()
		t3 = Thread(target=input_message,args=(messageQ,))
		t3.setDaemon(True)
		t3.start()
		t0 = Thread(target=put_into_buffer,args=(messageQ,data_buffer)) ### to be modify
		t0.setDaemon(True)
		t0.start()
		while 1:
			pass


	except KeyboardInterrupt:
		print(">>> Bye")
		raise KeyboardInterrupt
		sys.exit()
	except Exception as x: 
		print(">>> " + str(x))
		sys.exit()
	finally:
		sys.exit()



		