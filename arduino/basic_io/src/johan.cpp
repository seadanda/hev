#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include "Adafruit_MCP9808.h"
#include <INA.h>

#define DEBUG

#ifdef DEBUG
#define DEBUG_SERIAL(x)  Serial.begin (x) 
#define DEBUG_PRINT(x)  Serial.print (x)
#define DEBUG_PRINTLN(x)  Serial.println (x)
#define DEBUG_PRINT2(x,y)  Serial.print (x,y)
#define DEBUG_PRINTLN2(x,y)  Serial.println (x,y)

#else
#define DEBUG_SERIAL(x) 
#define DEBUG_PRINT(x)
#define DEBUG_PRINTLN(x)
#define DEBUG_PRINT2(x,y) 
#define DEBUG_PRINTLN2(x,y)
#endif

//Flag to close all valves of the system to stop the data taking in a safe state
bool stop = true;

// Create the MCP9808 temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();


// Set Board to "ESP32 Dev Module"
// Set Port to /dev/ttyUSB0 on Linux

const int freq = 500; // 900 Hz for burkert 2875; Note - could be 500 Hz; depending on valve
float duty_cycle = 0.0;
const float max_duty_cycle = 0.85;

//const int pin_valve_air_in        = 3;   // RX0
const int pin_valve_o2_in         = 5;   // STRAPPING PIN (prefer as output / high-Z)
const int pin_valve_inhale        = 21;  // formerly valve_out
const int pin_valve_exhale        = 19;  // formerly valve_scavenge
const int pin_valve_purge         = 18;
//const int pin_valve_atmosphere    = 12;  // A15  // STRAPPING PIN (prefer as output / high-Z)
const int pin_valve_air_in        = 25; // DAC0



const int redled                  = 12; // red led on J28
const int yellowled               = 16;
const int greenled                = 17;

const int buzzer               = 2;




const int p_patient               = 32; // red led on J28
const int p_buffer                = 34; // 
const int p_air_supply            = 36; // 
const int p_air_regulated         = 39; // 
const int p_inhale                = 35; // 
const int p_o2_supply             = 27; // 
const int p_o2_regulated          = 14; // 


uint8_t        devicesFound = 0;       ///< Number of INAs found


INA_Class      INA;    

TwoWire I2CMCP9808 = TwoWire(0);

void setup() {

        Serial.begin(9600);
        //Wire.begin(SDA,SCL);
        Wire.begin(22,23);
        I2CMCP9808.begin(22,23);

        if (!tempsensor.begin(0x18, &I2CMCP9808)) {
                Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
                while (1);
        }

        tempsensor.setResolution(3); 



        // NodeMCU32
        // pwm
        ledcSetup(0, freq, 8);  
        ledcSetup(1, freq, 8);  

        //ledcSetup(1,2200,8); // buzzer frequency

        //ledcAttachPin(pin_valve_o2_in      , 0);  
        ledcAttachPin(pin_valve_inhale     , 0);  
        ledcAttachPin(pin_valve_exhale     , 1);  

        ledcAttachPin(buzzer     , 1);  

        //ledcWrite(1, 128); //buzzer

        pinMode(A13, INPUT); // potentiometer

        // pressure sensors IO config

        pinMode(p_patient, INPUT);
        pinMode(p_buffer, INPUT);
        pinMode(p_air_supply, INPUT);
        pinMode(p_air_regulated, INPUT);
        pinMode(p_inhale, INPUT);
        pinMode(p_o2_supply, INPUT);
        pinMode(p_o2_regulated, INPUT);


        // Valves IO config

        pinMode(pin_valve_air_in,OUTPUT);
        //pinMode(pin_valve_exhale,OUTPUT);
        pinMode(pin_valve_purge,OUTPUT);
        pinMode(pin_valve_o2_in,OUTPUT);

        // LEDs IO config

        pinMode(redled,OUTPUT);
        pinMode(yellowled,OUTPUT);
        pinMode(greenled,OUTPUT);



	if(stop){
	//To Close all valves of the system
        digitalWrite(pin_valve_air_in, LOW);
        digitalWrite(pin_valve_exhale, LOW);
        digitalWrite(pin_valve_purge, LOW);
        digitalWrite(pin_valve_o2_in, LOW);
	}
	else{
		//Default values for data taking
		digitalWrite(pin_valve_air_in, HIGH);
		//digitalWrite(pin_valve_exhale, LOW);
		digitalWrite(pin_valve_purge, LOW);
		digitalWrite(pin_valve_o2_in, HIGH);
	}


        //digitalWrite(redled, HIGH);
        //digitalWrite(yellowled, HIGH);
        //digitalWrite(greenled, HIGH);

        DEBUG_PRINT("Hello");
        Serial.println("Hello");



        // current sensor configuration

        devicesFound = INA.begin(1,500000); // Set to an expected 1 Amp maximum and a 100000 microOhm resistor
        while (INA.begin(1, 500000) == 0)
        {
                DEBUG_PRINTLN("No INA device found, retrying in 10s...");
                delay(1000); // Wait 10 seconds before retrying 
        } // while no devices detected
        DEBUG_PRINT(" - Detected ");
        DEBUG_PRINT(devicesFound);
        DEBUG_PRINTLN(" INA devices on the I2C bus");
        INA.setBusConversion(8500);            // Maximum conversion time 8.244ms
        INA.setShuntConversion(8500);          // Maximum conversion time 8.244ms
        INA.setAveraging(128);                 // Average each reading n-times
        INA.setMode(INA_MODE_CONTINUOUS_BOTH); // Bus/shunt measured continuously
        INA.AlertOnBusOverVoltage(true,5000);  // Trigger alert if over 5V on bus




}

void loop() {



        float res = analogRead(A13);  //12 bit ADC on esp32
        float pressure_patient = analogRead(p_patient);  //12 bit ADC on esp32
        float pressure_buffer = analogRead(p_buffer);  //12 bit ADC on esp32
        float pressure_asupply = analogRead(p_air_supply);  //12 bit ADC on esp32
        float pressure_aregulated = analogRead(p_air_regulated);  //12 bit ADC on esp32
        float pressure_inhale = analogRead(p_inhale);  //12 bit ADC on esp32
        float pressure_o2supply = analogRead(p_o2_supply);  //12 bit ADC on esp32
        float pressure_o2regulated = analogRead(p_o2_regulated);  //12 bit ADC on esp32


        tempsensor.wake();  //sensor on
        float c = tempsensor.readTempC();

        tempsensor.shutdown_wake(1); //sensor off

        duty_cycle =  res/4096.0;

        if (duty_cycle > max_duty_cycle){
                duty_cycle = max_duty_cycle;
        }


        //Serial.print("Pot ");
        //Serial.print(String((int)res));
        //Serial.print(" p_patient ");
        //Serial.print(String((int)pressure_patient));
        //Serial.print(" p_buffer ");
        //Serial.print(String((int)pressure_buffer));
        //Serial.print(" p_as ");
        //Serial.print(String((int)pressure_asupply));
        //Serial.print(" p_ar ");
        //Serial.print(String((int)pressure_aregulated));
        //Serial.print(" p_inhale ");
        //Serial.print(String((int)pressure_inhale));
        //Serial.print(" p_o2s ");
        //Serial.print(String((int)pressure_o2supply)); 
        //Serial.print(" p_o2r ");
        //Serial.print(String((int)pressure_o2regulated));

        //Serial.print(" Temp: "); 
        //Serial.print(c, 4);


        //// measuring Valves voltage and current
        //Serial.print(" ");
        //Serial.print((float)INA.getBusMilliVolts(0)/1000.0,4);
        //DEBUG_PRINT("V ");
        //DEBUG_PRINT2((float)INA.getShuntMicroVolts(0)/5,0);  
        //DEBUG_PRINT("mA "); 
        //DEBUG_PRINT2((float)INA.getShuntMicroVolts(1)/5,0);  
        //DEBUG_PRINT("mA ");   
        //DEBUG_PRINT2((float)INA.getShuntMicroVolts(2)/5,0);  
        //DEBUG_PRINT("mA ");
        //DEBUG_PRINT2((float)INA.getShuntMicroVolts(3)/5,0);  
        //DEBUG_PRINT("mA ");

	if(stop){

		ledcWrite(0, 0);//val);// exhale
		ledcWrite(1, 0);//val);// exhale

	}
	else{

		duty_cycle = 0.74;
		float low_duty_cycle = 0.54;//525;
		int nsteps = 1; // number of steps of 10 ms in between 

		float step_size = (duty_cycle-low_duty_cycle) / nsteps;

		int val = (int)(255.0*duty_cycle);

		int vallow = (int)(255.0*low_duty_cycle);

		//Serial.print(" duty cycle ");
		//Serial.println(String(duty_cycle));
		//Serial.print(" raw val ");
		//Serial.println(String(val));

		digitalWrite(greenled, HIGH);
		//ledcWrite(0, val);// inhale
		ledcWrite(0, vallow);//vallow);// exhale
		delay(1000);

		for(int i=0; i<nsteps ; i++){
			int _val = (int)( 255.0 * ( low_duty_cycle + ( i * step_size ) ) );
			ledcWrite(0,_val);
			delay(10);
		}

		ledcWrite(0, val);//val);// exhale
		delay(1000);
		//ledcWrite(1, 0);// exhale
		//digitalWrite(greenled, LOW);

		//delay(1000);
	}
}
