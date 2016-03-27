import serial
import sys
import socket

sock=''
serial_port='/dev/ttyACM0'
message_id=1
payload_size=6
serial_size = 1

def connect_to_Raspi():
  global sock
  #Connect to raspberri pi using wifi
  TCP_IP = '192.168.43.206'
  TCP_PORT = 5010
  BUFFER_SIZE = 1024

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
  sock.connect((TCP_IP, TCP_PORT))
  #s.send(MESSAGE)
  #data = s.recv(BUFFER_SIZE)
  #s.close()
 
 
def write_output(finput,binfile,ser ):
    global message_id
    global sock
    #ser.read ---> read one byte at a time
    while True:
        for data in ser.read():
            if data:
              print(data)

	      if int(data)!=message_id:
	        sock.send(message_id)
		continue			
		
              char=ser.read()
              if char :
 		print "Recieved %s"%char
		message_id+=1
		sock.send(message_id)	
              else :
		sock.send(message_id)
                        
                if finput == True:
                  #binfile.write((''.join(chr(i) for i in char)).encode('ascii'))
                  binfile.write(data[2])


def write_output1(finput,binfile,ser ):
    global message_id
    global sock
    global payload_size
    global serial_size

    #ser.read ---> read one byte at a time
    while True:
        msg_id=-1
	while ser.inWaiting() < 1+payload_size :
            	#if ser.inWaiting() == serial_size:
		  #print ser.inWaiting()
		  #serial_size+=1
		continue
        #print "Before Readline"
        data=ser.read(1+payload_size)
 
        #print data      
        if data[0].isdigit():
          msg_id=int(data[0])
	  #print msg_id,
        else :
	  continue

        #if msg_id != message_id:
        #  print "I was expecting %d Msg ID. But I got %d"%(message_id, msg_id)
        sock.send(str(msg_id))
	#print "\nmsg_id=%d"%msg_id
        #  continue

        #message_id+=1
        #if message_id >15 :
	#   message_id=1

        #sock.send(str(message_id))
        if finput == False:
 	  #if(data[2] == '\n'):
	  #  print
	  sys.stdout.write(data[1:1+payload_size])
          sys.stdout.flush()
        else:
          #binfile.write((''.join(chr(i) for i in data[2])).encode('ascii'))
	  binfile.write(data[1:1+payload_size])
	  #binfile.flush()		
        #print



def connect_to_serial(file_input=False):
 global serial_port
 try:
  fname='test_file'
  binfile=open(fname,'wb')

  ser = serial.Serial(
    port = serial_port , \
    baudrate=9600, \
    parity=serial.PARITY_NONE, \
    stopbits=serial.STOPBITS_ONE, \
    bytesize=serial.EIGHTBITS, \
    timeout=0)
  ser.flush()
  print("connected to: "+ser.portstr)
  count=1

  #write_output(file_input,binfile,ser)
  write_output1(file_input,binfile,ser)
 

 #except KeyboardInterrupt:
 finally :
  binfile.close()           
  #ser.close()




if __name__ == '__main__':

   connect_to_Raspi()

   if (len(sys.argv) > 1) :
      print 'Argument %s'%sys.argv[0]
      connect_to_serial(True)
   else :
      connect_to_serial() 

