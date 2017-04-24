import socket
import sys
import json
import time
from time import localtime, strftime
from threading import Thread

class MyException(Exception): pass

def initialization():
	input_info = sys.argv
	local_port = None
	neighbor_list = []
	loss_rate_list = []
	try:
		local_port = int(sys.argv[1])
	except:
		raise MyException("port number should be integer between 1024 and 65534")
	routing_table['local_port'] = local_port
	for i in range(2,len(input_info)):
		if input_info[i] == 'last':
			info_table['start'] = True
		elif i%2 == 0:
			try:
				neighbor_list.append(int(input_info[i]))
			except:
				raise MyException("port number should be integer between 1024 and 65534")
		elif i%2 == 1:
			try:
				loss_rate_list.append(float(input_info[i]))
			except:
				raise MyException('loss rate should be float between 0 and 1')
	for i in zip(neighbor_list,loss_rate_list):
		neighbor_table['neighbors'].append(i[0])
		neighbor_table['distance'].append(i[1])
		routing_table['destination'].append(i[0])
		routing_table['nexthop'].append(None)
		routing_table['distance'].append(i[1])


def broadcast_to_neighbor():
	routing_table['timestamp'] = str(time.time())
	for neighbor_port in neighbor_table['neighbors']:
		s.sendto(json.dumps(routing_table),('',neighbor_port))

def update_routing_table(client_packet):
	### client packet is routing table
	neighbor_index = neighbor_table['neighbors'].index(client_packet['local_port'])
	update_or_not = False
	for destination in client_packet['destination']:
		if destination != routing_table['local_port']:
			destination_index = client_packet['destination'].index(destination)
			if destination not in routing_table['destination']:
				### no such destination so add it
				update_or_not = True
				routing_table['destination'].append(destination)
				routing_table['nexthop'].append(client_packet['local_port'])
				routing_table['distance'].append(neighbor_table['distance'][neighbor_index]+client_packet['distance'][destination_index])
			else:
				routing_table_index = routing_table['destination'].index(destination)
				if (neighbor_table['distance'][neighbor_index] + client_packet['distance'][destination_index]) < routing_table['distance'][routing_table_index]:
					routing_table['distance'][routing_table_index] = neighbor_table['distance'][neighbor_index] + client_packet['distance'][destination_index]
					routing_table['nexthop'][routing_table_index] = client_packet['local_port']
					update_or_not = True
	return update_or_not



def dvnode():
	while True:
		try:
			client_packet, clientaddress = s.recvfrom(2048)
			client_packet = json.loads(client_packet)
		except socket.error:
			continue
		if info_table['setup'] == False:
			info_table['setup'] = True
			broadcast_to_neighbor()
		if update_routing_table(client_packet) == True:
			info_table['start'] = True
			print('['+str(time.time())+'] Node '+str(routing_table['local_port'])+' Rounting Table')
			for i in range(len(routing_table['destination'])):
				if routing_table['nexthop'][i]:
					print('- ('+str(routing_table['distance'][i])+') -> Node '+str(routing_table['destination'][i])+'; Next hop -> Node '+str(routing_table['nexthop'][i]))
				else:
					print('- ('+str(routing_table['distance'][i])+') -> Node '+str(routing_table['destination'][i]))
		if info_table['start']:
			info_table['start'] = False
			broadcast_to_neighbor()



if __name__ == '__main__':

	try:
		info_table = {'start':False,'setup':False}
		neighbor_table = {'neighbors':[],'distance':[]}
		routing_table = {'local_port':None,'destination':[],'nexthop':[],'distance':[],'timestamp':None} ## if direct then nexthop is None
		initialization()
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind(('',routing_table['local_port']))
		if info_table['start']:
			broadcast_to_neighbor()
			info_table['start'] = False
			info_table['setup'] = True
		dvnode()
	except KeyboardInterrupt:
		raise KeyboardInterrupt
		sys.exit()
	except Exception as x: print('>>> '+str(x))
	finally:
		sys.exit()





