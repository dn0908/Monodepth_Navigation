#include <PPMReader.h>

// RC Controller
byte interruptPin = 2;
byte channelAmount = 8;
PPMReader ppm(interruptPin, channelAmount);
int RCinput[16];

// #define left_speed;
// #define right_speed;
int driving_speed;

// Motor Pins
const int IA1=4;
const int IA2=5;
const int IB1=7;
const int IB2=6;


void setup() {
  // SERIAL BEGIN
  Serial.begin(115200); 
  // MOTOR SETUP
  pinMode(IA1, OUTPUT);
  pinMode(IA2, OUTPUT);
  pinMode(IB1, OUTPUT);
  pinMode(IB2, OUTPUT);
}

void loop() {
  RC();
  int v = (RCinput[5] - 1080)*180/900;
  Serial.println(v); // print RC input in Serial Monitor

  // RCinput [3] : left stick down 1000 and up 2000
  // RCinput [1] : right stick left 1000 and right 2000

  if (RCinput[3] == 1500 & RCinput[1] == 1500){
    Serial.println("Stop");
    Stop();
  }

  if (RCinput[3] > 1520){
    Serial.println("Go Forward");
    driving_speed = map(RCinput[3], 1520, 2000, 50, 255);
    Go_Forward(driving_speed);
  }
  if (RCinput[3] < 1480){
    Serial.println("Go Backward");
    driving_speed = 255-((RCinput[3]-1000)*205/480);  
    Go_Backward(driving_speed);
  }
  if (RCinput[1] > 1520){
    Serial.println("Turn Right");
    driving_speed = map(RCinput[3], 1520, 2000, 50, 255);
    Turn_Right(255);
  }
  if (RCinput[1] < 1480){
    Serial.println("Turn Left");
    driving_speed = 255-((RCinput[3]-1000)*205/480);
    Turn_Left(255);
  }
  if (RCinput[5] == 2000){
    Serial.println("Reset?");
  }
  if (RCinput[5] < 2000){
    Serial.println("Do not Reset?");
  }

}

// RC signal function
void RC(){
  for (byte channel = 1; channel <= channelAmount; ++channel){
    unsigned value = ppm.latestValidChannelValue(channel, 0);
    RCinput[channel]=int(value);
    Serial.print(value);
    if(channel<channelAmount) Serial.print('\t');
  }
}

///////////////// Driving Functions/////////////////
void Stop(){
  MA1_Forward(0);
  MB1_Forward(0);
}
void Go_Forward(int driving_speed){
  MA1_Forward(driving_speed);
  MB1_Forward(driving_speed);
}
void Go_Backward(int driving_speed){
  MA2_Backward(driving_speed);
  MB2_Backward(driving_speed);
}
void Turn_Left(int driving_speed){
  MA2_Backward(driving_speed);
  MB1_Forward(driving_speed);
}
void Turn_Right(int driving_speed){
  MA1_Forward(driving_speed);
  MB2_Backward(driving_speed);
}

// LEFT = MA
void MA1_Forward(int Speed1)  //fast decay; Speed = High duty-cycle
{
     analogWrite(IA1,Speed1);
     digitalWrite(IA2,LOW);
}

void MA2_Backward(int Speed1)  //slow decay; Speed = Low duty-cycle
{
    int Speed2=255-Speed1;
    analogWrite(IA1,Speed2);
    digitalWrite(IA2,HIGH);
}

// LEFT = MB
void MB1_Forward(int Speed1)
{
     analogWrite(IB1,Speed1);
     digitalWrite(IB2,LOW);
}

void MB2_Backward(int Speed1)
{
    int Speed2=255-Speed1;
    analogWrite(IB1,Speed2);
    digitalWrite(IB2,HIGH);
}