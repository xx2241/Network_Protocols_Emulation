Name: Xun Xue
UNI: xx2241

Programming Assignment 2 - Network Protocols Emulation


1. Go-Back-N Protocol

1.1 Usage Scenarios:

(1) Starting Program
python gbnnode.py <self-port> <peer-port> <window-size> [-d <value-of-n> ｜ －p <value-of-p>]

The user should only specify either -d or -p. The square bracket and the vertical line means to choose between the two options.-d means the GBN node will drop packets (data or ACK) in a deterministic way (for every n packets), and -p means the GBN node will drop packets with a probability of p.

(2) Sending Messages
After the GBN node has started, node> is prompted for commands. There is only one command allowed: node> send <message>message is a character string which the sender will send to the <peer-port>

1.2 Test Cases

(1)Sender side:
xuns-MacBook-Pro:Network Protocols Emulation xx$ python gbnnode.py 2222 1111 5 -p 0.2
node>  send abcdefghi
node>  [1492997227.25]packet0 a sent
[1492997227.25]packet1 b sent
[1492997227.25]packet2 c sent
[1492997227.25]packet3 d sent
[1492997227.25]packet4 e sent
[1492997227.26]ACK0 received, window moves to 1
[1492997227.27]ACK1 received, window moves to 2
 [1492997227.27]packet5 f sent
[1492997227.27]ACK2 received, window moves to 3
[1492997227.27]ACK3 discarded
[1492997227.27]packet6 g sent
[1492997227.27]ACK3 received, window moves to 4
[1492997227.27]packet7 h sent
[1492997227.27]ACK3 received, window moves to 4
[1492997227.27]ACK3 received, window moves to 4
[1492997227.27]packet8 i sent
[1492997227.27]ACK3 received, window moves to 4
[1492997227.77]packet4 timeout
[1492997227.77]packet4 e sent
[1492997227.77]packet5 f sent
[1492997227.77]packet6 g sent
[1492997227.77]ACK4 received, window moves to 5
[1492997227.77]packet7 h sent
[1492997227.77]packet8 i sent
[1492997227.77]ACK5 discarded
[1492997227.77]ACK6 received, window moves to 7
[1492997227.77]ACK6 received, window moves to 7
[1492997228.27]packet7 timeout
[1492997228.27]packet7 h sent
[1492997228.27]packet8 i sent
[1492997228.77]packet7 timeout
[1492997228.77]packet7 h sent
[1492997228.77]packet8 i sent
[1492997228.78]ACK7 discarded
[1492997228.78]ACK8 discarded
[1492997229.27]packet7 timeout
[1492997229.28]packet7 h sent
[1492997229.28]packet8 i sent
[1492997229.28]ACK7 received, window moves to 8
[1492997229.28]ACK8 received, window moves to 9
[Summary] 4/16 packets dropped, loss rate = 0.25
node> 
(2) Receiver side:
xuns-MacBook-Pro:Network Protocols Emulation xx$ python gbnnode.py 1111 2222 5 -p 0.2
node>  [1492997227.25]packet0 a received
[1492997227.26]ACK0 sent, expecting packet1
[1492997227.26]packet1 b received
[1492997227.26]ACK1 sent, expecting packet2
[1492997227.26]packet2 c received
[1492997227.26]ACK2 sent, expecting packet3
[1492997227.26]packet3 d received
[1492997227.26]ACK3 sent, expecting packet4
[1492997227.26]packet4 e discarded
[1492997227.27]packet5 f received
[1492997227.27]ACK3 sent, expecting packet4
[1492997227.27]packet6 g received
[1492997227.27]ACK3 sent, expecting packet4
[1492997227.27]packet7 h received
[1492997227.27]ACK3 sent, expecting packet4
[1492997227.27]packet8 i received
[1492997227.27]ACK3 sent, expecting packet4
[1492997227.77]packet4 e received
[1492997227.77]ACK4 sent, expecting packet5
[1492997227.77]packet5 f received
[1492997227.77]ACK5 sent, expecting packet6
[1492997227.77]packet6 g received
[1492997227.77]ACK6 sent, expecting packet7
[1492997227.77]packet7 h discarded
[1492997227.77]packet8 i received
[1492997227.77]ACK6 sent, expecting packet7
[1492997228.27]packet7 h discarded
[1492997228.27]packet8 i discarded
[1492997228.77]packet7 h received
[1492997228.78]ACK7 sent, expecting packet8
[1492997228.78]packet8 i received
[1492997228.78]ACK8 sent, expecting packet9
[1492997229.28]packet7 h received
[1492997229.28]ACK7 sent, expecting packet8
[1492997229.28]packet8 i received
[1492997229.28]ACK8 sent, expecting packet9
[Summary] 4/20 packets dropped, loss rate = 0.2
node> 

2. Distance-Vector Routing Algorithm

2.1 Usage Scenarios:

(1) Starting Program
python dvnode.py <local-port> <neighbor1-port> <loss-rate-1> <neighbor2-port> <loss-rate-2> ... [last]

<local-port>: The UDP listening port number (1024-65534) of the node.
<neighbor#-port>: The UDP listening port number (1024-65534) of one of the neighboring nodes.
<loss-rate-#>: This will be used as the link distance to the <neighbor#-port>.It is between 0-1 and represents the probability of a packet being dropped on that link.last: Indication of the last node information of the network. The proram should understand this arg as optional (he command with this argument, the routing message exchanges among the nodes shouldkick in.

2.2 Test Cases

input:
^Cxuns-MacBook-Pro:Network Protocols Emulation xx$ python dvnode.py 1111 2222 .1333 .5
^Cxuns-MacBook-Pro:Network Protocols Emulation xx$ python dvnode.py 2222 1111 .1333 .2 4444 .8
^Cxuns-MacBook-Pro:Network Protocols Emulation xx$ python dvnode.py 3333 1111 .5222 .2 4444 .5
^Cxuns-MacBook-Pro:Network Protocols Emulation xx$ python dvnode.py 4444 2222 .8 3333 .5ast

output:

port 1111
[1492999785.89] Node 1111 Routing Table
- (0.1) -> Node 2222
- (0.5) -> Node 3333
[1492999785.89] Node 1111 Routing Table
- (0.1) -> Node 2222
- (0.3) -> Node 3333; Next hop -> Node 2222
- (0.9) -> Node 4444; Next hop -> Node 2222
[1492999785.89] Node 1111 Routing Table
- (0.1) -> Node 2222
- (0.3) -> Node 3333; Next hop -> Node 2222
- (0.8) -> Node 4444; Next hop -> Node 2222

port 2222
^Cxuns-MacBook-Pro:Network Protocols Emulation xx$ python dvnode.py 2222 1111 .1333 .2 4444 .8
[1492999785.89] Node 2222 Routing Table
- (0.1) -> Node 1111
- (0.2) -> Node 3333
- (0.8) -> Node 4444
[1492999785.89] Node 2222 Routing Table
- (0.1) -> Node 1111
- (0.2) -> Node 3333
- (0.7) -> Node 4444; Next hop -> Node 3333

port 3333
[1492999785.89] Node 3333 Routing Table
- (0.5) -> Node 1111
- (0.2) -> Node 2222
- (0.5) -> Node 4444
[1492999785.89] Node 3333 Routing Table
- (0.3) -> Node 1111; Next hop -> Node 2222
- (0.2) -> Node 2222
- (0.5) -> Node 4444

port 4444
[1492999785.89] Node 4444 Routing Table
- (0.8) -> Node 2222
- (0.5) -> Node 3333
[1492999785.89] Node 4444 Routing Table
- (0.7) -> Node 2222; Next hop -> Node 3333
- (0.5) -> Node 3333
- (1.0) -> Node 1111; Next hop -> Node 3333
[1492999785.89] Node 4444 Routing Table
- (0.7) -> Node 2222; Next hop -> Node 3333
- (0.5) -> Node 3333
- (0.9) -> Node 1111; Next hop -> Node 2222
[1492999785.89] Node 4444 Routing Table
- (0.7) -> Node 2222; Next hop -> Node 3333
- (0.5) -> Node 3333
- (0.8) -> Node 1111; Next hop -> Node 3333



3. Combination

Notice: I initialize the distance of neighbors to 100 instead of 0!!!

3.1 Usage Scenarios:

python cnnode.py <local-port> receive <neighbor1-port> <loss-rate-1> <neighbor2-port> <loss-rate-2> ... <neighborM-port> <loss-rate-M> send <neighbor(M+1)-port> <neighbor(M+2)-port> ... <neighborN-port> [last]

<local-port>: The UDP listening port number (1024-65534) of the node.
receive: The current node will be the probe receiver for the following neighbors.
<neighbor#-port>: The UDP listening port number (1024-65534) of one of the neighboring nodes. If you are using a different sending port number, you have to add the listening port number to your own packet header.
<loss-rate-#>: The probability to drop the probe packets. Keep listing the pair of <sender-port> and <loss-rate> for all your neighboring nodes.
send: The current node will be the probe sender for the following neighbors. Keep listing the pair of <neighbor-port> and <loss-rate> for all your neighboring nodes.
last: The optional argument. Indication of the last node information of the network. Upon the input of the command with this argument, the routing message exchanges among the nodes shouldkick in.

3.2 Test Cases

initialize the distance to 100

input:
xx2241@instance-w4119:~/Network_Protocols_Emulation$ python cnnode.py 1111 receive send 2222 3333
xx2241@instance-w4119:~/Network_Protocols_Emulation$ python cnnode.py 2222 receive 1111 .1 send 3333 4444
xx2241@instance-w4119:~/Network_Protocols_Emulation$ python cnnode.py 3333 receive 1111 .5 2222 .2 send 4444
xx2241@instance-w4119:~/Network_Protocols_Emulation$ python cnnode.py 4444 receive 2222 .8 3333 .5 send last

output:
port 1111
start
[1493002452.52] Node 1111 Rounting Table
- (100) -> Node 2222
- (100) -> Node 3333
- (200) -> Node 4444; Next hop -> Node 3333
converge:
[1493002667.35] Node 1111 Rounting Table
- (0.08) -> Node 2222
- (0.29) -> Node 3333; Next hop -> Node 2222
- (0.79) -> Node 4444; Next hop -> Node 2222

port 2222:
start:
[1493002453.28] Link to 1111: 16packets received, 1 packets lost, lost rate 0.06
[1493002454.29] Link to 1111: 17packets received, 1 packets lost, lost rate 0.06
[1493002455.78] Link to 1111: 19packets received, 1 packets lost, lost rate 0.05
[1493002455.78] Node 2222 Rounting Table
- (100) -> Node 3333
- (0.05) -> Node 1111
- (100) -> Node 4444
converge:
[1493002664.89] Link to 1111: 293packets received, 24 packets lost, lost rate 0.08
[1493002666.03] Link to 1111: 294packets received, 24 packets lost, lost rate 0.08
[1493002667.03] Link to 1111: 295packets received, 24 packets lost, lost rate 0.08
[1493002667.86] Node 2222 Rounting Table
- (0.21) -> Node 3333
- (0.08) -> Node 1111
- (0.71) -> Node 4444; Next hop -> Node 3333

port 3333:
start:
[1493002453.53] Link to 2222: 20packets received, 1 packets lost, lost rate 0.05
[1493002453.53] Link to 1111: 14packets received, 6 packets lost, lost rate 0.43
[1493002454.77] Link to 2222: 30packets received, 3 packets lost, lost rate 0.1
[1493002454.78] Link to 1111: 25packets received, 11 packets lost, lost rate 0.44
[1493002455.39] Node 3333 Rounting Table
- (0.13) -> Node 2222
- (0.49) -> Node 1111
- (100) -> Node 4444
converge:
[1493002671.07] Node 3333 Rounting Table
- (0.21) -> Node 2222
- (0.29) -> Node 1111; Next hop -> Node 2222
- (0.5) -> Node 4444
[1493002672.07] Link to 2222: 1450packets received, 300 packets lost, lost rate 0.21
[1493002672.07] Link to 1111: 1440packets received, 713 packets lost, lost rate 0.5

port 4444
start:
[1493002435.66] Node 4444 Rounting Table
- (100) -> Node 3333
- (100) -> Node 2222
[1493002437.02] Link to 3333: 0packets received, 0 packets lost, lost rate 0
[1493002437.02] Link to 2222: 0packets received, 0 packets lost, lost rate 0
[1493002438.27] Link to 3333: 0packets received, 0 packets lost, lost rate 0
[1493002438.27] Link to 2222: 0packets received, 0 packets lost, lost rate 0
converge:
[1493002668.82] Node 4444 Rounting Table
- (0.79) -> Node 1111; Next hop -> Node 3333
- (0.71) -> Node 2222; Next hop -> Node 3333
- (0.5) -> Node 3333
[1493002669.82] Link to 2222: 1419packets received, 1133 packets lost, lost rate 0.8
[1493002669.82] Link to 3333: 1413packets received, 713 packets lost, lost rate 0.5
[1493002670.82] Link to 2222: 1424packets received, 1136 packets lost, lost rate 0.8
[1493002670.82] Link to 3333: 1423packets received, 717 packets lost, lost rate 0.5


Data structure or Algorithms used:
1. Distance Vector(Bellman-Ford algorithm)
2. Queue
Use queue on receiver side for multithreading
3. Dictionary
To maintain information within multithreading

Program Features
Same as the PA2 homework description file


