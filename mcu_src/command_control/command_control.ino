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
    Go_Forward(80);
    if (Serial.available()>0) {
        String data = Serial.readStringUntil('\n');
        // Serial.print("SERIAL DATA READ : ");
        // Serial.println(data);
        
        if (data == "F"){
            // Serial.println("Go Forward");
            Go_Forward(255);
            delay(500);
        }
        if (data == "R"){
            // Serial.println("Turn Right");
            Turn_Left(255);
            delay(500);
        }
        if (data == "L"){
            // Serial.println("Turn Left");
            Turn_Right(255);
            delay(500);
        }
        else {
            Stop();
            delay(500);
        }
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
  MA1_Forward(driving_speed);
  MB2_Backward(driving_speed);
}
void Turn_Right(int driving_speed){
  MB1_Forward(driving_speed);
  MA2_Backward(driving_speed);
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