#!/usr/bin/env python
  
import socket
import os 
import sys
import thread
 
TCP_IP = '192.168.122.11'
TCP_PORT = 5005
BUFFER_SIZE = 1024
sock=None

def wait_for_ack():
   global sock
   while 1:
     data = sock.recv(BUFFER_SIZE)
     if not data:
       continue

     print data
     
 

def initialize_connection():
  global TCP_IP
  global TCP_PORT
  global BUFFER_SIZE
  global sock
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
  sock.connect((TCP_IP, TCP_PORT))
  return sock

def send_file(sock):
  fname=raw_input("Please enter filename :")
  if not os.path.exists(fname):
    print fname, 'doesn\'t exist. Please provide valid file name' 
    sys.exit(0) 

  print sys.argv[0]
  with open(fname, "rb") as f:
    msg = f.read(1023)
    while msg :
        #print "Sending %s"%msg
        sock.send(msg)
        msg = f.read(1023)

  #data = s.recv(BUFFER_SIZE)




if __name__=='__main__':
 try:

   initialize_connection()
   thread.start_new_thread( wait_for_ack, () )
   send_file(sock)

   while 1:
     pass

 finally:
   print "Connectio Closed"
   sock.close()
