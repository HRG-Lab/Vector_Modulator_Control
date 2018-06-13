/*
Cube_Calibration.ino is the code that runs on the Arduino while doing the calibration.
It simply reads a command and sets the control voltages accordingly.
This code works together with the Cube_Calibration.py
 */

const double pi = 3.14159265;
const double IVscale[] = {13140.0, 13085.0, 13095.0, 13122.0, 13140.0, 13155.0,
                          13155.0, 13095.0, 13125.0, 13060.0, 13060.0, 13095.0,
                          13080.0, 13095.0, 13115.0, 13065.0, 13115.0, 13060.0};
                          
const double QVscale[] = {13110.0, 13105.0, 13110.0, 13120.0, 13140.0, 13170.0,
                          13135.0, 13140.0, 13120.0, 13100.0, 13080.0, 13115.0,
                          13065.0, 13150.0, 13100.0, 13120.0, 13110.0, 13035.0};

const int totalElements = 18;

const int ledPin = 13; // the pin that the LED is attached to
int incomingByte;      // a variable to read incoming serial data into
const int _sck = 4;
const int _sdi = 5;
const int ctl = 10; //board layer 1 activate, each other layer must have a jumper from the pin to pin 10 to create multi layered board
const int ldac = 9;
const int clearpin = 8;
const int ctl5 = 12; //board layer 5 activate
const int ctl4 = 11; //board layer 4 activate
const int ctl2 = 7; //board layer 2 activate
const int ctl3 = 6; //board layer 3 activate    

double Iset = 0;
double Qset = 0;

void setup() {
   /*
   Sets the data rate in bits per second (baud) for serial data transmission. For communicating with the computer
   use one of these rates: 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, or 115200. You can,
   however, specify other rates - for example, to communicate over pins 0 and 1 with a component that requires a particular baud rate.
   */
   Serial.begin(115200);

   // ct1 = 10, oard layer 1 activate, each other layer must have a jumper from the pin to pin 10 to create multi layered board
   pinMode(ctl, OUTPUT);

   // _sck = 4
   pinMode(_sck, OUTPUT);

   // _sdi = 5
   pinMode(_sdi, OUTPUT);

   // ldac = 9
   pinMode(ldac,OUTPUT);

   // clearpin = 8
   pinMode(clearpin, OUTPUT);

   // ct12 = 7, board layer 2 activate
   pinMode(ctl2, OUTPUT);

   // ct13 = 6, board layer 3 activate
   pinMode(ctl3, OUTPUT);

   // ct14 = 11, board layer 4 activate
   pinMode(ctl4, OUTPUT);

   // ct15 = 12, board layer 5 activate
   pinMode(ctl5, OUTPUT);
  
   digitalWrite(clearpin, HIGH);
  
   digitalWrite(ctl,HIGH);

   digitalWrite(ctl2,HIGH);

   digitalWrite(ctl3, HIGH);
   
   digitalWrite(ctl4, HIGH);
   
   digitalWrite(ctl5, HIGH);
  
   digitalWrite(_sck,HIGH);
   
   digitalWrite(ldac,HIGH);

 
   for(int i=0; i<totalElements; i++){
      writeVoltage(i+1,'I',1.5);
      writeVoltage(i+1,'Q',1.5); 
   } 
}





void loop(){
  // This function returns the number of bytes of data in the buffer that are waiting for you to read.
  // If there are no messages waiting to be read, then the function returns 0.
   while(Serial.available()>0){
      
      // parseInt() returns the first valid (long) integer number from the serial buffer. Characters that are not integers (or the minus sign) are skipped.
      int antennaNum = Serial.parseInt();
      
      char type = Serial.read();
      
      // parseFloat() returns the first valid floating point number from the current position. Initial characters that are not digits (or the minus sign) are skipped.
      // parseFloat() is terminated by the first character that is not a floating point number.
      float Vset = Serial.parseFloat();
    
      writeVoltage(antennaNum,type,Vset);
  }
}





void writeVoltage(int antennaNum, char type, float Vset){
   unsigned int highword = 0;
 
   unsigned int lowword = 0;
 
   unsigned int converted = 0;

   // equivalent to the expression antennaNum = antennaNum - 1
   antennaNum -= 1;
 
   double scaled =  Vset;//5375.0; // DAC Word / Voltage (LSB/volt) from Nick

   if(type =='I' || type == 'i'){
      scaled *= IVscale[antennaNum];
   }
   if(type == 'Q' || type == 'q'){
      scaled *= QVscale[antennaNum];
   }

   converted = (int) scaled;

   /* 
   bitshift right (>>)
   bitshift left (<<)
   ex:
   int a = 5;       // binary: 0000000000000101
   int b = a << 3;  // binary: 0000000000101000
   int c = b >> 3;  // binary: 0000000000000101
   */
   highword = converted >> 12; //the command bytes require that the LSB of the highword have value

   lowword = converted << 4; //rest of value to be written to register...

   if( (0 <= antennaNum) && (antennaNum <= 3)){
      if(type == 'I' || type == 'i'){
         highword += 0x0300 + (2*antennaNum)*16;
         writeLayer(ctl,highword,lowword);
      }
   if(type == 'Q' || type == 'q'){
      highword += 0x0300 + (2*antennaNum+1)*16;
      writeLayer(ctl,highword,lowword);
   }
   }else if( (4 <= antennaNum) && (antennaNum <= 7)){
      antennaNum -= 4;
      if(type == 'I' || type == 'i'){
         highword += 0x0300 + (2*antennaNum)*16;
         writeLayer(ctl2,highword,lowword);
      }
      if(type == 'Q' || type == 'q'){
         highword += 0x0300 + (2*antennaNum+1)*16;
         writeLayer(ctl2,highword,lowword);
      }
   }else if( (8 <= antennaNum) && (antennaNum <= 11)){
      antennaNum -= 8;
      if(type == 'I' || type == 'i'){
         highword += 0x0300 + (2*antennaNum)*16;
         writeLayer(ctl3,highword,lowword);
      }
      if(type == 'Q' || type == 'q'){
         highword += 0x0300 + (2*antennaNum+1)*16;
         writeLayer(ctl3,highword,lowword);
      }
   }else if( (12 <= antennaNum) && (antennaNum <= 15)){
      antennaNum -= 12;
      if(type == 'I' || type == 'i'){
         highword += 0x0300 + (2*antennaNum)*16;
         writeLayer(ctl4,highword,lowword);
      }
      if(type == 'Q' || type == 'q'){
         highword += 0x0300 + (2*antennaNum+1)*16;
         writeLayer(ctl4,highword,lowword);
      }
   }else if( (16 <= antennaNum) && (antennaNum <= 17)){
      antennaNum -= 16;
   if(type == 'I' || type == 'i'){
      highword += 0x0300 + (4*antennaNum+1)*16;
      writeLayer(ctl5,highword,lowword);
   }
   if(type == 'Q' || type == 'q'){
      highword += 0x0300 + (4*antennaNum+3)*16;
      writeLayer(ctl5,highword,lowword);
   }
   }
}





void writeLayer(int layer,int high, int low){
   digitalWrite(layer,LOW);

   // shiftOut (pin# which is the bit to be sent, pin# used as a clock pin, A flag to determine whether the bits will be sent starting with the least significant bit or most significant. MSBFIRST/LSBFIRST, The byte of data to be sent)
   shiftOut(_sdi, _sck, MSBFIRST, (high>>8));
   
   shiftOut(_sdi, _sck, MSBFIRST, high);
   
   shiftOut(_sdi, _sck, MSBFIRST, (low>>8));
   
   shiftOut(_sdi, _sck, MSBFIRST, low);
   
   digitalWrite(layer,HIGH);
   
   digitalWrite(ldac,LOW);
   
   digitalWrite(ldac,HIGH);
}
