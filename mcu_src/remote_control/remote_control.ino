#include <PPMReader.h>

// RC Controller
byte interruptPin = 2;
byte channelAmount = 8;
PPMReader ppm(interruptPin, channelAmount);
int RCinput[16];

// #define left_speed;
// #define right_speed;
int driving_speed;

// RIGHT Motor Pins
int Dir1_R =5;
int Dir2_R =4;
int Speed_R = 6;

// LEFT Motor Pins
int Dir1_L = 13;
int Dir2_L = 12;
int Speed_L = 11;

// Openrb Reset Pin
int Arm_reset = 8;


void setup() {
  // SERIAL BEGIN
  Serial.begin(115200); 
  // Right Motor setup
  pinMode(Dir1_R, OUTPUT);
  pinMode(Dir2_R, OUTPUT); 
  pinMode(Speed_R, OUTPUT); 
  // Left Motor setup
  pinMode(Dir1_L, OUTPUT); 
  pinMode(Dir2_L, OUTPUT); 
  pinMode(Speed_L, OUTPUT);

  // For Openrb reset
  pinMode(Arm_reset, OUTPUT);
  digitalWrite(Arm_reset, HIGH);
}

void loop() {
  digitalWrite(Arm_reset, HIGH);

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
    Serial.println("Reset Robot Arm");
    digitalWrite(Arm_reset, LOW);
    delay(10);
    digitalWrite(Arm_reset, HIGH);
  }
  if (RCinput[5] < 2000){
    digitalWrite(Arm_reset, HIGH);
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
  digitalWrite(Dir1_R, LOW);
  digitalWrite(Dir2_R, HIGH); 
  analogWrite(Speed_R, 0);
  digitalWrite(Dir1_L, LOW); 
  digitalWrite(Dir2_L, HIGH); 

  analogWrite(Speed_L, 0);
}
void Go_Forward(int driving_speed){
  digitalWrite(Dir1_R, LOW);
  digitalWrite(Dir2_R, HIGH); 
  analogWrite(Speed_R, driving_speed);
  digitalWrite(Dir1_L, LOW); 
  digitalWrite(Dir2_L, HIGH); 
  analogWrite(Speed_L, driving_speed);
}
void Go_Backward(int driving_speed){
  digitalWrite(Dir1_R, HIGH);
  digitalWrite(Dir2_R, LOW);
  analogWrite(Speed_R, driving_speed);
  digitalWrite(Dir1_L, HIGH); 
  digitalWrite(Dir2_L, LOW); 
  analogWrite(Speed_L, driving_speed); 
}
void Turn_Left(int driving_speed){
  digitalWrite(Dir1_R, LOW);
  digitalWrite(Dir2_R, HIGH); 
  analogWrite(Speed_R, driving_speed);
  digitalWrite(Dir1_L, HIGH); 
  digitalWrite(Dir2_L, LOW); 
  analogWrite(Speed_L, driving_speed); 
}
void Turn_Right(int driving_speed){
  digitalWrite(Dir1_L, LOW); 
  digitalWrite(Dir2_L, HIGH); 
  analogWrite(Speed_L, driving_speed);
  digitalWrite(Dir1_R, HIGH);
  digitalWrite(Dir2_R, LOW);
  analogWrite(Speed_R, driving_speed);
}