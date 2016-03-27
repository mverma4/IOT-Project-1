int analogPin = A0;     // potentiometer wiper (middle terminal) connected to analog pin 3
                       // outside leads to ground and +5V
                                                                                                                                                                                                                                                                           
int val = 0;           // variable to store the value read           
int level1 = 80;                                                                                                                     
int NO_OF_CHARS = 6;
int MSG_ID_BITS = 1;
int ARR_SIZE = NO_OF_CHARS*8 + MSG_ID_BITS;

int i = 0;

//declaring 
int *arr;
char *chars;
int high, low;

int k = 0;                                                                                                                                                                                                                                                                    
int bits[2];                                                                                                                                                                                                                                                                   
int ascii_val;                                                                                                                                                                                                                                                                 
int first=1;                                                                                                                                                                                                                                                                   
int started = 0;                                                                                                                                                                                                                                                               
int D = 3; //delay value                                                                                                                                                                                                                                                      
int bit1, bit2;                                                                                                                                                                                                                                                                
int msg_id;                                                                                                                  
char c;

void setup()
{
  chars=(char *)malloc(sizeof(char)*NO_OF_CHARS);
  arr = (int*)malloc(sizeof(int)*ARR_SIZE);
  Serial.begin(9600);          //  setup serial
}

int powint(int x, int y)
{
     int val=x;
     for(int z=0;z<=y;z++)
     {
       if(z==0)
         val=1;
       else
         val=val*x;
     }
     return val;
}

int my_atoi(int *arr, int high, int low)
{   
    int sum = 0;
    for(int j = high; j>=low; j--)
    { 
         sum += powint(2,high-j)*(*(arr+j));
    }
    return sum;
}
int my_msgID(int *arr){
    int sum = 0;
    for(int j = MSG_ID_BITS-1; j>=0; j--)
    { 
         sum += powint(2,MSG_ID_BITS-1-j)*(*(arr+j));
    }
    return sum;
}

void loop()

{
  // read the input pin
  //delay(D);
  val = analogRead(analogPin);  
  //Serial.println(val);
  
  if(started == 1){
    
    delay(D);
    
    if(val > level1) *(arr+i++) = 1;
    else *(arr+i++) = 0;
  
    if(i == ARR_SIZE)
    { 
      //msg_id = my_msgID(arr);
      msg_id = *arr;
      
      for(int l=0; l<NO_OF_CHARS; l++){
          low = l*8 + MSG_ID_BITS;
          high = low + 7;
          ascii_val = my_atoi(arr, high, low);
          chars[l] = ascii_val;
      }

      i = 0;
      started = 2;
    }
  } else if(started == 2){ 
      
      delay(D);  
    
      if(val > level1){          
          Serial.print(msg_id);
          for(int l=0; l<NO_OF_CHARS; l++){
                Serial.print(chars[l]); 
          }
        }
        started = 0;
        
  }  else {
    
      if(val > level1){
        delay(4.8);
        started = 1;
      }
  }
  
}