//---------- I N C L U D E S --------------------------------------------------
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>
#include <avr/eeprom.h>
#include <Wire.h>
#include <SparkFunHTU21D.h>
#include <Time.h>
#include <MCP79412RTC.h>



//---------- C O N S T A N T S ------------------------------------------------
//#define BOOT_POST

// Node controller (JP1)
#define PIN_RELAY_NC 4
#define PIN_HEARTBEAT_NC 5
// Network switch (JP2)
#define PIN_RELAY_SWITCH 6
#define PIN_HEARTBEAT_SWITCH 7
// Guest node 1 (JP3)
#define PIN_RELAY_GN1 8
#define PIN_HEARTBEAT_GN1 9
// Guest node 2 (JP4)
#define PIN_RELAY_GN2 10
#define PIN_HEARTBEAT_GN2 11
// Guest node 3 (JP5)
#define PIN_RELAY_GN3 12
#define PIN_HEARTBEAT_GN3 13
// Thermistors (JP10)
#define PIN_THERMISTOR_NC A0
#define PIN_THERMISTOR_SWITCH A1
#define PIN_THERMISTOR_GN1 A2
#define PIN_THERMISTOR_GN2 A3
#define PIN_THERMISTOR_GN3 A4
// Light detector
#define PIN_PHOTOCELL A5

// Period of heartbeat for ODroids (ms)
// This needs to be small and an even number
#define HEARTBEAT_PERIOD_ODROID 40

// Delay after bad environment reading during boot (seconds)
#define BOOT_BAD_ENVIRON_WAIT_TIME 5
// Delay after bad power reading during boot (seconds)
#define BOOT_BAD_POWER_WAIT_TIME 1

// I2C addresses for current sensors
#define ADDR_CURRENT_SENSOR_SYSMON 0x60
#define ADDR_CURRENT_SENSOR_NC 0x62
#define ADDR_CURRENT_SENSOR_SWITCH 0x63
#define ADDR_CURRENT_SENSOR_GN1 0x68
#define ADDR_CURRENT_SENSOR_GN2 0x6A
#define ADDR_CURRENT_SENSOR_GN3 0x6B

// Resolution of current sensors (with 8A range) (mA)
#define MILLIAMPS_PER_STEP 16

// Special characters for interacting with the node controller
#define NC_NOTIFIER_STATUS '@'
#define NC_NOTIFIER_PROBLEM '#'
#define NC_NOTIFIER_PARAMS_CORE '$'
#define NC_NOTIFIER_PARAMS_GN '^'
#define NC_NOTIFIER_TIME '*'
#define NC_DELIMITER ','
#define NC_TERMINATOR '!'

// Messages to send to node controller
#define PROBLEM_BOOT_GN1_TEMP "GN1:bf_t"
#define PROBLEM_BOOT_GN1_POWER "GN1:bf_p"
#define PROBLEM_BOOT_GN1_HEARTBEAT "GN1:bf_h"
#define PROBLEM_BOOT_GN2_TEMP "GN2:bf_t"
#define PROBLEM_BOOT_GN2_POWER "GN2:bf_p"
#define PROBLEM_BOOT_GN2_HEARTBEAT "GN2:bf_h"
#define PROBLEM_BOOT_GN3_TEMP "GN3:bf_t"
#define PROBLEM_BOOT_GN3_POWER "GN3:bf_p"
#define PROBLEM_BOOT_GN3_HEARTBEAT "GN3:bf_h"



//---------- G L O B A L S ----------------------------------------------------
volatile byte timer1_interrupt_fired = 0;
volatile byte _timer1_cycle = false;
volatile char USART_RX_char;
volatile boolean _USART_new_char = false;

HTU21D SysMon_HTU21D;

boolean GN1_booted = false;
boolean GN2_booted = false;
boolean GN3_booted = false;

// EEPROM addresses whose values are set by node controller:
uint32_t EEMEM E_USART_BAUD;
uint16_t EEMEM E_USART_RX_BUFFER_SIZE;
uint8_t EEMEM E_STATUS_REPORT_PERIOD;
uint8_t EEMEM E_MAX_NUM_SOS_BOOT_ATTEMPTS;
uint8_t EEMEM E_MAX_NUM_SUBSYSTEM_BOOT_ATTEMPTS;
uint16_t EEMEM E_BOOT_TIME_NC;
uint8_t EEMEM E_BOOT_TIME_SWITCH;
uint16_t EEMEM E_BOOT_TIME_GN1;
uint16_t EEMEM E_BOOT_TIME_GN2;
uint16_t EEMEM E_BOOT_TIME_GN3;
uint8_t EEMEM E_PRESENT_GN1;
uint8_t EEMEM E_PRESENT_GN2;
uint8_t EEMEM E_PRESENT_GN3;
uint8_t EEMEM E_HEARTBEAT_TIMEOUT_NC;
uint8_t EEMEM E_HEARTBEAT_TIMEOUT_SWITCH;
uint8_t EEMEM E_HEARTBEAT_TIMEOUT_GN1;
uint8_t EEMEM E_HEARTBEAT_TIMEOUT_GN2;
uint8_t EEMEM E_HEARTBEAT_TIMEOUT_GN3;
uint8_t EEMEM E_BAD_TEMP_TIMEOUT_SYSMON;
uint8_t EEMEM E_BAD_TEMP_TIMEOUT_NC;
uint8_t EEMEM E_BAD_TEMP_TIMEOUT_SWITCH;
uint8_t EEMEM E_BAD_TEMP_TIMEOUT_GN1;
uint8_t EEMEM E_BAD_TEMP_TIMEOUT_GN2;
uint8_t EEMEM E_BAD_TEMP_TIMEOUT_GN3;
uint16_t EEMEM E_AMP_NOISE_CEILING;
uint8_t EEMEM E_BAD_CURRENT_TIMEOUT_SYSMON;
uint8_t EEMEM E_BAD_CURRENT_TIMEOUT_NC;
uint8_t EEMEM E_BAD_CURRENT_TIMEOUT_SWITCH;
uint8_t EEMEM E_BAD_CURRENT_TIMEOUT_GN1;
uint8_t EEMEM E_BAD_CURRENT_TIMEOUT_GN2;
uint8_t EEMEM E_BAD_CURRENT_TIMEOUT_GN3;
uint16_t EEMEM E_TEMP_MIN_SYSMON;
uint16_t EEMEM E_TEMP_MAX_SYSMON;
uint16_t EEMEM E_TEMP_MIN_NC;
uint16_t EEMEM E_TEMP_MAX_NC;
uint16_t EEMEM E_TEMP_MIN_SWITCH;
uint16_t EEMEM E_TEMP_MAX_SWITCH;
uint16_t EEMEM E_TEMP_MIN_GN1;
uint16_t EEMEM E_TEMP_MAX_GN1;
uint16_t EEMEM E_TEMP_MIN_GN2;
uint16_t EEMEM E_TEMP_MAX_GN2;
uint16_t EEMEM E_TEMP_MIN_GN3;
uint16_t EEMEM E_TEMP_MAX_GN3;
uint8_t EEMEM E_HUMIDITY_MIN_SYSMON;
uint8_t EEMEM E_HUMIDITY_MAX_SYSMON;
uint16_t EEMEM E_AMP_MAX_SYSMON;
uint16_t EEMEM E_AMP_MAX_NC;
uint16_t EEMEM E_AMP_MAX_SWITCH;
uint16_t EEMEM E_AMP_MAX_GN1;
uint16_t EEMEM E_AMP_MAX_GN2;
uint16_t EEMEM E_AMP_MAX_GN3;
// EEPROM addresses whose values are not set by node controller:
uint8_t EEMEM E_NC_ENABLED;
uint8_t EEMEM E_SWITCH_ENABLED;
uint8_t EEMEM E_GN1_ENABLED;
uint8_t EEMEM E_GN2_ENABLED;
uint8_t EEMEM E_GN3_ENABLED;
uint8_t EEMEM E_POST_RESULT;
uint8_t EEMEM E_TIMER_TEST_INCOMPLETE;
uint8_t EEMEM E_NUM_SOS_BOOT_ATTEMPTS;
uint8_t EEMEM E_FIRST_BOOT;



//---------- S E T U P --------------------------------------------------------
void setup() 
{
  // Debug
  delay(5000);

  // Is POST enabled?
  #ifdef BOOT_POST
    // Is everything (internal) working correctly?
    if(POST())
    {
      // Boot self, node controller, and ethernet switch.  Boot successful?
      if(boot_primary())
        // Boot the guest nodes
        boot_gn();
    }
    // Something non-fatal failed the POST
    else
      // Go to partial boot sequence
      boot_SOS();
  #else
    // Boot self, node controller, and ethernet switch.  Boot successful?
    if(boot_primary())
    {
      Serial.println("Booted");

      // Boot the guest nodes
      boot_gn();
    }
  #endif

  // Clear counter, since its been counting for awhile already
  timer1_interrupt_fired = 0;
}



//---------- L O O P ----------------------------------------------------------
void loop() 
{
  // Has the timer finished a cycle?
  if(_timer1_cycle)
  {
    // Clear the flag
    _timer1_cycle = false;

    // Environ. checks go here

    // Time to send a status report?
    if(timer1_interrupt_fired >= eeprom_read_byte(&E_STATUS_REPORT_PERIOD))
      send_status();

    // Send problem report to node controller
    //send_problem();

    // Check heartbeat of guest node 2
    //check_heartbeat(2);
  }
}



//---------- S E N D _ S T A T U S --------------------------------------------
/*
   Sends a status report of all important info to the node controller.

   :rtype: none
*/
void send_status()
{
  // Tell the node controller that a status report is coming
  Serial.println(NC_NOTIFIER_STATUS);

  // Give it time to get ready
  delay(10);

  Serial.print("Light: ");
  Serial.println(analogRead(PIN_PHOTOCELL));

  timer1_interrupt_fired = 0;
}



//---------- S E N D _ P R O B L E M ------------------------------------------
/*
   Sends a problem report to the node controller.

   :param String problem: description of the problem

   :rtype: none
*/
void send_problem(String problem)
{
  // Tell the node controller that a problem report is coming
  Serial.println(NC_NOTIFIER_PROBLEM);

  // Give it time to get ready
  delay(10);

  // Send problem report
  Serial.println("problem report");
}



//---------- T I M E R 1 _ O V E R F L O W _ I N T E R R U P T ----------------
/*
   Interrupt for Timer1 overflow.  Resets the watchdog and increments the
   counter used to tell the MCU when to check the environment.

   :rtype: none
*/
 ISR(TIMER1_OVF_vect)
{
  // Reset watchdog
  wdt_reset();

  // Increment the counter for how many timer overflows have occurred
  timer1_interrupt_fired++;

  // Set the flag to indicate a complete timer cycle
  _timer1_cycle = true;
}



//---------- U S A R T 1 _ R X _ I N T E R R U P T ----------------------------
/*
   Interrupt for USART1 receive.

   :rtype: none
*/
ISR(USART1_RX_vect)
{
  // Read and store new character
  USART_RX_char = Serial.read();

  // Set flag to tell main program that new serial data is available
  _USART_new_char = true;
}