/*********************************************************************
  This is an example for our nRF8001 Bluetooth Low Energy Breakout

  Pick one up today in the adafruit shop!
  ------> http://www.adafruit.com/products/1697

  Adafruit invests time and resources providing this open source code,
  please support Adafruit and open-source hardware by purchasing
  products from Adafruit!

  Written by Kevin Townsend/KTOWN  for Adafruit Industries.
  MIT license, check LICENSE for more information
  All text above, and the splash screen below must be included in any redistribution
*********************************************************************/

// This version uses the internal data queing so you can treat it like Serial (kinda)!
/////////////////////////////////////////////////////////////////////////////////////////////////////////
// BLUETOOTH
#include <SPI.h>
#include <Wire.h>
#include "Adafruit_BLE_UART.h" // Needed for Bluetooth
#include <Adafruit_Sensor.h>   // Needed for accelerometer
#include <Adafruit_LSM303_U.h> // Needed for accelerometer



// Connect CLK/MISO/MOSI to hardware SPI
// e.g. On UNO & compatible: CLK = 13, MISO = 12, MOSI = 11
#define ADAFRUITBLE_REQ 10
#define ADAFRUITBLE_RDY 2     // This should be an interrupt pin, on Uno thats #2 or #3
#define ADAFRUITBLE_RST 9

Adafruit_BLE_UART BTLEserial = Adafruit_BLE_UART(ADAFRUITBLE_REQ, ADAFRUITBLE_RDY, ADAFRUITBLE_RST);
Adafruit_LSM303_Mag_Unified   mag = Adafruit_LSM303_Mag_Unified(12345); // the magnetometer
Adafruit_LSM303_Accel_Unified accel = Adafruit_LSM303_Accel_Unified(12346); // the accelerometer

aci_evt_opcode_t laststatus = ACI_EVT_DISCONNECTED;

/////////////////////////////////////////////////////////////////////////////////////////////////////////



/////////////////////////////////////////////////////////////////////////////////////////////////////////


// FLEX



int flexSensorPin = A0; //analog pin 0
int flexSensorReading = 0;
int n = 0;
double sum = 0;
int flexCount = 0;
int THRESHOLD = 60;
/////////////////////////////////////////////////////////////////////////////////////////////////////////




/*
/////////////////////////////////////////////////////////////////////////////////////////////////////////
//HEART

// Define pins for LED and sensor.
int ledPin = 7;
int sensorPin = 0;
// lasttime is used to have a very precise measurement of the time so the calculated pulse is correct.
unsigned long lasttime;
double heartValue;

/////////////////////////////////////////////////////////////////////////////////////////////////////////
*/





/*
void displayAccelDetails(void)
{
  sensor_t sensor;
  accel.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" m/s^2");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" m/s^2");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" m/s^2");  
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

void displayMagDetails(void)
{
  sensor_t sensor;
  mag.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" uT");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" uT");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" uT");  
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}
*/


/**************************************************************************/
/*!
    Configure the Arduino and start advertising with the radio
*/
/**************************************************************************/
void BluetoothSetup()
{
  Serial.println(F("Adafruit Bluefruit Low Energy nRF8001 Print echo demo"));

  // BTLEserial.setDeviceName("NEWNAME"); /* 7 characters max! */

  BTLEserial.begin();
}

void MagSetup()
{
  Serial.println("Magnetometer Test"); Serial.println("");
  mag.enableAutoRange(true);
  /* Initialise the sensor */
  if(!mag.begin())
  {
    /* There was a problem detecting the LSM303 ... check your connections */
    Serial.println("Ooops, no LSM303 detected ... Check your wiring!");
    while(1);
  }
  // displayMagDetails();
}

void AccelSetup()
{

  Serial.println("Accelerometer Test"); Serial.println("");
  /* Initialise the sensor */
  if(!accel.begin())
  {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println("Ooops, no LSM303 detected ... Check your wiring!");
    while(1);
  }
  
  /* Display some basic information on this sensor */
  // displayAccelDetails();

}

float accX;
float accY;
float accZ;

void readAccel(void) {
  /* Get a new sensor event */ 
  sensors_event_t event; 
  accel.getEvent(&event);
  /* Display the results (acceleration is measured in m/s^2) */
  // Serial.print("X: "); Serial.print(event.acceleration.x); Serial.print("  ");
  // Serial.print("Y: "); Serial.print(event.acceleration.y); Serial.print("  ");
  // Serial.print("Z: "); Serial.print(event.acceleration.z); Serial.print("  ");Serial.println("m/s^2 ");
  accX = event.acceleration.x;
  accY = event.acceleration.y;
  accZ = event.acceleration.z;
  delay(500);
}




float magX;
float magY;
float magZ;



void readMagSensor(void) {
  /* Get a new sensor event */ 
  sensors_event_t event; 
  mag.getEvent(&event);
 
  /* Display the results (magnetic vector values are in micro-Tesla (uT)) */
  // Serial.print("X: "); Serial.print(event.magnetic.x); Serial.print("  ");
  // Serial.print("Y: "); Serial.print(event.magnetic.y); Serial.print("  ");
  // Serial.print("Z: "); Serial.print(event.magnetic.z); Serial.print("  ");Serial.println("uT");
  magX = event.magnetic.x;
  magY = event.magnetic.y;
  magZ = event.magnetic.z;
  delay(500);
}
/**************************************************************************/
/*!
    Constantly checks for new events on the nRF8001
*/
/**************************************************************************/
//aci_evt_opcode_t laststatus = ACI_EVT_DISCONNECTED;

void BluetoothSend(String s)
{
  // Tell the nRF8001 to do whatever it should be working on.
  BTLEserial.pollACI();

  // Ask what is our current status
  aci_evt_opcode_t status = BTLEserial.getState();
  // If the status changed....
  if (status != laststatus) {
    // print it out!
    if (status == ACI_EVT_DEVICE_STARTED) {
      Serial.println(F("* Advertising started"));
    }
    if (status == ACI_EVT_CONNECTED) {
      Serial.println(F("* Connected!"));
    }
    if (status == ACI_EVT_DISCONNECTED) {
      Serial.println(F("* Disconnected or advertising timed out"));
    }
    // OK set the last status change to this one
    laststatus = status;
  }
  //Serial.println("TEST0");
  if (status == ACI_EVT_CONNECTED) {
    // Lets see if there's any data for us!
    if (BTLEserial.available()) {
      Serial.print("* "); Serial.print(BTLEserial.available()); Serial.println(F(" bytes available from BTLE"));
    }
    // Serial.println("TEST1");
    // OK while we still have something to read, get a character and print it out
    //   while (BTLEserial.available()) {
    //      char c = BTLEserial.read();
    //     Serial.print(c);
    //   }

    // Next up, see if we have any data to get from the Serial console
    //Serial.println("TEST2");

    // Read a line from Serial
    Serial.setTimeout(100); // 100 millisecond timeout
    //String s = Serial.readString(); Input Parameter

    // We need to convert the line to bytes, no more than 20 at this time

    // Serial.println("TEST3");
    s = s + "#";
    uint8_t sendbuffer[40];
    s.getBytes(sendbuffer, 40);
    char sendbuffersize = min(40, s.length());
    Serial.print(F("\n* Sending -> \""));
    Serial.print((char *)sendbuffer);
    Serial.println("\"");

    // write the data
    BTLEserial.write(sendbuffer, sendbuffersize);

  }
}






void readFlexSensor(int debug) {
  readFlexSensor();

  if (flexSensorReading < THRESHOLD)
  {
    while (flexSensorReading < THRESHOLD) {
      readFlexSensor();
    }
    flexCount++;
    if (debug > 0) {
      Serial.println();
      Serial.print(flexCount);
      Serial.print( "   --   " );
      Serial.println(THRESHOLD);
    }
    updateThreshold(flexSensorReading);
  }

}

void readFlexSensor() {
  flexSensorReading = analogRead(flexSensorPin);
  sum = sum + flexSensorReading;
  n = n + 1;
  delay(20);
}

void updateThreshold(int reading) {
  THRESHOLD = 1.2 * sum / n;
  Serial.print("Update Threshold to " );
  Serial.println(THRESHOLD);
  if (THRESHOLD > 70 || THRESHOLD < 40) {
    THRESHOLD = 65;
  }
  sum = 0;
  n = 0;
}





/*
void heartSetup() {
  pinMode (ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH);

  lasttime = micros();
}



void readHeartSensor() {
  // Wait 10 ms between each measurement.
  while (micros() - lasttime < 1000) {
    delayMicroseconds(100);
  }
  // Read the signal.
  heartValue = analogRead(sensorPin);
  lasttime = micros();
}
*/









void setup(void) {
  Serial.begin(9600);
  while (!Serial); // Leonardo/Micro should wait for serial init
  BluetoothSetup();
  //heartSetup();
  AccelSetup();
  MagSetup();
}

void loop(void) {
  //readHeartSensor();
  //s =  "HEART:" + String(heartValue, 5);
  //BluetoothSend(s);

  readFlexSensor(1);
  String s =  "STRETCH:" + String(flexCount, 5);
  BluetoothSend(s);

  readAccel();
  s =  "ACCEL:" + String(accX, 5) + "," + String(accY, 5) + "," + String(accZ, 5);
  BluetoothSend(s);

  readMagSensor();
  s =  "MAG:" + String(magX, 5) + "," + String(magY, 5) + "," + String(magZ, 5);
  BluetoothSend(s);


}







