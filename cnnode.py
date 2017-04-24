import socket
import sys
import json
import time
import random
import Queue
from time import localtime, strftime
from threading import Thread

class MyException(Exception): pass
class Timer():
    def __init__(self,interval):
        self.time = None
        self.status = False
        self.interval = interval
    def start(self):
        self.time = time.time()
        self.status = True
    def stop(self):
        self.status = False
    def timeout(self):
        return self.status and (time.time()-self.time)>self.interval
class Probe():
	def __init__(self,seq,ack,port):
		self.seq = seq
		self.ack = False
		self.port = port
	def send(self):
		### has sending interval
		port = int(self.port)
		s.sendto(json.dumps({'tag':'probe','seq':self.seq,'ack':self.ack,'local_port':routing_table['local_port']}),('',port))
		# print(str(routing_table['local_port'])+' send packet %d '%self.seq+'to '+str(port))
class Window():
	def __init__(self,port):
		self.base = 0
		self.nextseq = 0
		self.size = 5
		self.timer = Timer(0.5)
		self.probe_list = []
		self.port = port
	def reset(self):
		self.base = 0
		self.nextseq = 0
		window.timer.stop()
		self.probe_list = [] ### like a buffer
	def move_list(self,original_base,message_length):
		### a new packet acked
		for i in range(original_base,self.base):
			if self.probe_list:
				self.probe_list.pop(0)
		### don't need to append since this list is put all message at the begining
	def increase_nextseq(self):
		### a new packet sent
		self.nextseq = self.nextseq + 1
def send_probe(window,Summary_timer,DV_timer):
	while info_table['setup']==False:
		pass
	Summary_timer.start()
	DV_timer.start()
	while True:
		### reinitialize for the next round
		window.reset()
		end = window.base + info_table['message_length']
		while window.base < end:
			if window.nextseq < window.base+window.size and window.nextseq<10:
				probe = Probe(window.nextseq,False,window.port)
				window.probe_list.append(probe)
				probe.send()
				if window.base == window.nextseq:
					window.timer.start()
				window.nextseq += 1
			if window.timer.timeout():
				# print('packet %d timeout'%window.base),
				# print(' of port'),
				# print(window.port)
				window.timer.start()
				for probe in window.probe_list:
					probe.send()
		time.sleep(1) ## sending interval
def receive_ack(window):
	while True:
		for port,queue in queue_table.items():
			if port == window.port:
				packet = queue.get()
		if packet['tag']=='probe' and packet['ack']==True and int(window.port)==packet['local_port'] and packet['seq']!=-1: ### ack never drop
			# ### should judge the port
			# print('receive ack'),
			# print(packet['seq']),
			# print('from '),
			# print(packet['local_port'])
			tmpbase = window.base
			window.base = packet['seq']+1
			window.move_list(tmpbase,info_table['message_length'])
			if window.base == window.nextseq:
				window.timer.stop()
			else:
				window.timer.start()
def update_routing_table(packet):
	update_table['dv_update'] = False
	client_port = packet['local_port']
	for port, value in packet.items():
		if isinstance(value,dict):
			if int(port) == routing_table['local_port']:
				# print(value['distance']),
				# print(' of port '),
				# print(client_port)
				if routing_table[str(client_port)]['distance']!=value['distance'] and routing_table[str(client_port)]['nexthop']==None:  ### update distance 
					# print('distance update from port '+str(client_port)+'original local port to port'+port+'='+str(routing_table[str(client_port)]['distance'])+', new distance '+str(value['distance']))
					routing_table[str(client_port)]['distance']=value['distance']
					update_table['distance_update']=True

	for port, value in packet.items():
		if isinstance(value,dict):
			distance = value['distance'] + routing_table[str(client_port)]['distance']
			if int(port) != routing_table['local_port']:
				if routing_table.has_key(port):
					if routing_table[port]['distance']>distance or routing_table[port]['nexthop']==client_port:
						# print('update dv: port'+str(client_port)+' to port'+port+'='+str(value['distance'])+', local port to port'+str(client_port)+'='+str(routing_table[str(client_port)]['distance'])+', original distance to port'+port+'='+str(routing_table[port]['distance']))
						update_table['dv_update'] = True
						routing_table[port]['distance'] = distance
						routing_table[port]['nexthop'] = client_port
				else:
					update_table['dv_update'] = True
					routing_table[port] = {'receive_from':False,'send_to':False,'distance':distance,'received_number':0,'discarded_number':0,'nexthop':client_port,'probability':None}
def receive_probe_DV():
	while True:
		data,clientaddress = s.recvfrom(2048)
		packet = json.loads(data)
		if packet['tag']=='probe' and packet['ack']==True:
			for port,queue in queue_table.items():
				queue_table[port].put(packet)
		elif packet['tag']=='probe' and packet['ack']==False:
			port = packet['local_port']
			if discard_or_not(packet)==False:
				# print('packet_seq '),
				# print(packet['seq']),
				# print(' receive from '),
				# print(packet['local_port'])

				if packet['seq']==info_table[str(port)]:
					info_table[str(port)] += 1
				s.sendto(json.dumps({'tag':'probe','seq':info_table[str(port)]-1,'ack':True,'local_port':routing_table['local_port']}),('',port))
				# print('send ack%d to %d'%(info_table[str(port)]-1,port))
			else:
				pass
				# print('packet_seq '),
				# print(packet['seq']),
				# print(' discard from '),
				# print(packet['local_port'])
			if packet['seq'] == info_table['message_length']-1:
				info_table[str(port)]=0
				loss_rate = cal_link_loss(routing_table[str(port)]['received_number'],routing_table[str(port)]['discarded_number'])
				if loss_rate !=0 and routing_table[str(port)]['nexthop']==None:
					routing_table[str(port)]['distance']=loss_rate
				#print('['+str(time.time())+'] Link to '+str(port)+': '+str(routing_table[str(port)]['received_number'])+'packets received, '+str(routing_table[str(port)]['discarded_number'])+' packets lost, lost rate '+str(loss_rate))
		elif packet['tag']=='routing_table':
			# print('routing table received from'),
			# print(packet['local_port'])
			if info_table['setup']==False:
				info_table['setup']= True			
				receive_or_not = True
				broadcast_to_neighbor()
			else:
				update_routing_table(packet)
			if update_table['dv_update'] == True:
				print('['+str(time.time())+'] Node '+str(routing_table['local_port'])+' Rounting Table')
				for port, value in routing_table.items():
					if isinstance(value,dict):
						if value['nexthop']:
							print('- ('+str(value['distance'])+') -> Node '+str(port)+'; Next hop -> Node '+str(value['nexthop']))
						else:
							print('- ('+str(value['distance'])+') -> Node '+str(port))
def timer_update(Summary_timer,DV_timer):
	### a new thread
	while True:
		if Summary_timer.timeout():
			for port, value in routing_table.items():
				if isinstance(value,dict):
					if value['receive_from']==True:
						loss_rate = cal_link_loss(value['received_number'],value['discarded_number'])
						print('['+str(time.time())+'] Link to '+str(port)+': '+str(value['received_number'])+'packets received, '+str(value['discarded_number'])+' packets lost, lost rate '+str(loss_rate))
			Summary_timer.start()
		if DV_timer.timeout():
			update_table['distance_update']=False
			print('['+str(time.time())+'] Node '+str(routing_table['local_port'])+' Rounting Table')
			for port,value in routing_table.items():
				if isinstance(value,dict):
					if value['nexthop']:
						print('- ('+str(value['distance'])+') -> Node '+str(port)+'; Next hop -> Node '+str(value['nexthop']))
					else:
						print('- ('+str(value['distance'])+') -> Node '+str(port))
					if value['receive_from'] or value['send_to']: ## if it is neighor
						if original_distance[port] != value['distance']:  ## if update, update itself is not here!!
							original_distance[port] = value['distance']
							s.sendto(json.dumps(routing_table),('',int(port)))
			DV_timer.start()
def discard_or_not(packet):
	### receiver side
	#### ack and DV will never be dropped!!!!!!!
	#### index is the index in receive_from list
	port = str(packet['local_port'])
	routing_table[port]['received_number']+=1
	if random.random() > routing_table[port]['probability']:
		return False
	else:
		routing_table[port]['discarded_number']+=1
		return True
def cal_link_loss(receive,drop):
	if receive==0:
		return 0
	else:
		return round(float(drop)/receive,2)
def initialization():
	input_info = sys.argv
	local_port = None
	try:
		local_port = int(sys.argv[1])
	except:
		raise MyException("port number should be integer between 1024 and 65534")
	i = 1
	while i < len(input_info):
		i = i+1
		if input_info[i] == 'receive':
			while True:
				i = i+1
				try:
					port = int(input_info[i])
					routing_table[str(port)]={'receive_from':True,'send_to':False,'distance':100,'received_number':0,'discarded_number':0,'nexthop':None,'probability':0}
				except:
					try:
						probability = float(input_info[i])
						routing_table[str(port)]['probability'] = probability
					except:
						break
		if input_info[i] == 'send':
			while True:
				i = i+1
				try:
					port = int(input_info[i])
					if routing_table.has_key(str(port)):
						routing_table[str(port)]['send_to']=True
					else:
						routing_table[str(port)]={'receive_from':False,'send_to':True,'distance':100,'received_number':0,'discarded_number':0,'nexthop':None,'probability':0}
				except:
					if i == len(input_info):
						break
					elif input_info[i] == 'last':
						info_table['setup'] = True
						info_table['is_last'] = True
	routing_table['local_port'] = local_port			
def broadcast_to_neighbor():
	for port, value in routing_table.items():
		if isinstance(value,dict):
			port = int(port)
			s.sendto(json.dumps(routing_table),('',int(port)))
if __name__ == '__main__':
	info_table ={'setup':False,'message_length':10,'is_last':False} ### port:expected_number!!!!  ## last -> start == True, alredy setup -> start == True, setup: send when first received
	routing_table = {'tag':'routing_table','local_port':None,'timestamp':None} # 'port':{'receive_from':False,'send_to':False,'distance':100,'received_number':0'discarded_number':0,'nexthop':None,'probability':None}
	## when send_to==False and receive_from==False, it is not neighbor
	queue_table = {}
	original_distance = {}
	update_table = {'dv_update':False,'distance_update':False}
	initialization()
	for port,value in routing_table.items():
		if isinstance(value,dict):
			original_distance[port] = value['distance']
			if value['receive_from']:
				info_table[port]=0
			if value['send_to']:
				queue = Queue.Queue()
				queue_table[port] = queue
	print(routing_table)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('',routing_table['local_port']))
	if info_table['is_last']== True:
		broadcast_to_neighbor()
	Summary_timer = Timer(1)
	DV_timer = Timer(3)
	t0 = Thread(target=timer_update,args=(Summary_timer,DV_timer,))
	t0.setDaemon(True)
	t0.start()
	t1 = Thread(target=receive_probe_DV,args=())
	t1.setDaemon(True)
	t1.start()
	for port, value in routing_table.items():
		if isinstance(value,dict):
			if value['send_to']==True:
				window = Window(port)
				t2 = Thread(target=send_probe,args=(window,Summary_timer,DV_timer,))
				t3 = Thread(target=receive_ack,args=(window,))
				t2.setDaemon(True)
				t3.setDaemon(True)
				t2.start()
				t3.start()
			elif info_table['setup']:
				Summary_timer.start()
				DV_timer.start()
	while True:
		pass






