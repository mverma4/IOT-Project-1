#!/usr/bin/env python

import socket
import RPi.GPIO as GPIO
import time
import sys
import thread

sleepTimer=0.01
TCP_IP = '192.168.43.206'
eth='192.168.122.11'
disconnect_time=0
TCP_PORT = 5005
TCP_PORT_PC2=5010
message_id=0
exp_msg_id=-1
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
output_pin=18
max_char=1
max_waiting_time=300 #Max waiting time in mili seconds

white=''

def initialize():
  global white
  global output_pin
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup(output_pin,GPIO.OUT)


def wait_for_ack() :
  global exp_msg_id
  global TCP_IP
  global TCP_PORT_PC2
  global BUFFER_SIZE
  #Receive message ID from laptop2. and store the next expected message ID in exp_msg_id global variable  

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((TCP_IP, TCP_PORT_PC2))
  s.listen(2)

  conn, addr = s.accept()
  print 'Connected to PC2:', addr

  while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data:
      continue
 
    print "received message ID:", data
    exp_msg_id=int(data)

  conn.close()



def start_pc2_connection():
   thread.start_new_thread( wait_for_ack, () )


def get_msg_id(pc1,ftype=False):
    global exp_msg_id
    global disconnect_time
    global max_waiting_time
    count=0
    #Wrapper to get the proper message ID from the PC2 connection thread

    #Timeout incase noreply from PC2
    while (exp_msg_id == -1 and count != max_waiting_time ):
       time.sleep(0.001)
       count+=1
       continue

    if count == max_waiting_time:
       print "TIMEOUT.. No Ack Receieved from PC2.."
       disconnect_time+=1
       
       if disconnect_time > 10 and ftype == True:
         pc1.send("Can't Transfer File! Some Error Happened... Please try again")
         pc1.close()
         sys.exit(0)
         
       #One less than the message_id. Corner scenario
       #if delta ==0 :
       #  return 15

       #return delta-1	
    else :
      disconnect_time=0	
    
    print "Receieved %d Message ID from PC2"%exp_msg_id 
    
    return exp_msg_id

def wait_for_message_id(pc1,ftype):
   global message_id
   global exp_msg_id

   resend_character=False
   receieved_from_pc2=get_msg_id(pc1,ftype)
   exp_msg_id=-1  #Reset the message ID.
 
   if (receieved_from_pc2 != message_id):
      resend_character=True
      print "In wait_for_message_id() method.. Msg ID Expected %d. But observed From PC2 %d"%(message_id, receieved_from_pc2)     
      return resend_character
   else :
      return resend_character  #Do not resend the character



def send_message_hdr(count, send_message_id, i, pc1,arr):
      global message_id  #Global Val 0 initially
      #global white
      global exp_msg_id  #Message ID receieved from Thread
   
      global resend_flag 
      #Send Message ID for every 8 characters.Message ID is 1 Byte
      #And also we need to wait for the previous 8 charcter acknowledgement from the PC2
      #max_char variable is used to send message ID after every x bytes of data. Its value is initialised to 1
      #if (count % max_char   == 0):
         #delta=(message_id+1)%16   #Expect Next Message ID ACK from PC2. 
 	 #if delta == 0:
	 #  delta=1 
         #exp_msg_id_pc2= get_msg_id()
         #if (message_id != 0 and exp_msg_id_pc2 != delta):
          #  print "Message - %d NOT delivered properly --- > Delta : %d" % (message_id,delta)
          #  k=i
          #  if resend_flag == 0:  #We should not decremtn array val during each retransmission
          #    i=i-max_char
	      #message_id-=1  #FIX ME
          #  else :
	  #    k = i+max_char      #If it;s resend data, i is already decremented. So increment k by max_chars
            
	    #message_id-=1  #FIX ME
          #  print "Resending %d - %d characters[ %s ]"%(i,k,arr[i:k])
          #  pc1.send('%c'%arr[i:k])
	  #  not_delivered=1       #Used to skip incrementing the message_id value
         #elif exp_msg_id_pc2 == message_id:
         #   print "Second case!"
	    
         #else :
         #   print "Expected message ID %d. Recieved Ack from PC2 %d"%(delta, exp_msg_id)
	 #   send_message_id=1     #This flag used to controle message ID transmission. 1 means send
         #   message_id=delta           
         

      #send_message_id=1
      #msg_id+=1

      #if not_delivered==1:
      #   print '*'*20
      # 	 print "Sending Sync bits!"
      #   for m in range(20):
     # 	   GPIO.output(output_pin, 0)
     # 	   time.sleep(sleepTimer)

     #    print '*'*20

      if send_message_id == 1 :
        resend_flag=0 #Reset the flag, since next character successfully delivered
        print '-'*30
	GPIO.output(output_pin, 1)
        time.sleep(sleepTimer)
	GPIO.output(output_pin, 1)
        time.sleep(sleepTimer)

        print "Message ID is %d"%message_id
        for j in range(4) :
          if ((message_id & (1<<(3-j)) ) == (1<<(3-j))) :
            intensity= 1
            print "1"

          else :
            intensity= 0
  	    print "0"

          #msg_id=msg_id<<1

          GPIO.output(output_pin, intensity)
          time.sleep(sleepTimer)

        # Reset send_message_id flag. It should not send the message ID till next eight characters
        #send_message_id=0
        #Reset exp_msg_id global variable
        #exp_msg_id=-1

        print '-'*30

      #count=count%max_char   
      #not_delivered=0
      return (count, send_message_id,i)
 

def start_server(ftype=False):
  global message_id
  #Connect to PC1 
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((eth, TCP_PORT))
  s.listen(1)

  conn, addr = s.accept()
  print 'Connection address:', addr

  while 1:
    #Accept data from PC1
    data = conn.recv(BUFFER_SIZE)
    if not data:
      break
    count =0
    send_message_id=1
    i=0

    #For each character in the recieved data stream
    while i < len(data):
      #Pick One character at a time and find ASCII val 
      char = ord(data[i])
      count+=1
      print data[i], char

      
      print "So far %d char's sent. Message ID is %d"%(count,message_id)

      #Send Message Header
      count,send_message_id, i = send_message_hdr(count, send_message_id,i, conn,data)


      for j in range(8) :
        if ((char & (1<<(7-j)) ) == (1<<(7-j)) ) :
          intensity= 1
          print '1'

        else :
          intensity= 0
          print '0'



	GPIO.output(output_pin,intensity)
        time.sleep(sleepTimer)


      #Send Message end bits 110
      print '110'
      GPIO.output(output_pin,1)
      time.sleep(sleepTimer)
      GPIO.output(output_pin,1)
      time.sleep(sleepTimer)
      GPIO.output(output_pin,0)
      time.sleep(sleepTimer)

      #Wait for Acknowledgment. 
      resend_character= wait_for_message_id(conn,ftype)
      if resend_character== True:
         print "Seems like %c character not sent properly. Resending it"%data[i]
         conn.send(data[i])
         continue
      else :
         i+=1  #Increment the data index 
         message_id+=1
         if message_id >15:
	   message_id=0


    GPIO.output(output_pin,0)
    #conn.send(data)

    print "Sent data %s"%data

  conn.close()





if __name__ =='__main__':
  try: 
    if len(sys.argv) >1:
       ftype=True
    else:
       ftype=False

    initialize()
  
    start_pc2_connection()
 
    start_server(ftype) 
  
  finally :
    GPIO.output(output_pin,0)
    
    GPIO.cleanup()  

