import requests
import subprocess
import serial
import time

ESP8266_IP = "192.168.0.110"
Mode = "wired" #wireless

def update_esp8266_ip():
    """Auto-Update the Current IP of ESP8266 Wifi Module (Use if ESP Ip changed due to power loss or wifi reconnection)"""
    for i in range(100, 111):
        try:
            if requests.get(f"http://192.168.0.{i}/", timeout=1).status_code == 200:
                ESP8266_IP = f"192.168.0.{i}"
                print(f"ESP8266 found at: {ESP8266_IP}")
                break
        except: pass

def relay_request(number,state,ip=ESP8266_IP,Mode=Mode):
    """relay_request(1,state) for Red Light , state 1 for ON and state 0 for OFF.
    relay_request(2,state) for Yellow Light , state 1 for ON and state 0 for OFF.
    relay_request(3,state) for Pink Light , state 1 for ON and state 0 for OFF.
    relay_request(4,state) for Turning ON/OFF TV , state 1 for ON and state 0 for OFF.
    """
    if Mode=="wireless":
        curl_cmd = f'''curl http://{ip}/?command='''
        relays = [["a","b","c","d"],["A","B","C","D"]]
        state_list = ["R","r"]
        result = subprocess.run(curl_cmd+state_list[state]+relays[state][number-1], shell=True, capture_output=True, text=True)
        print(result.stdout)
    elif Mode=="wired":
        # Replace 'COM3' with the correct serial port for your Arduino
        arduino = serial.Serial('COM3', 115200, timeout=1)
        time.sleep(2) 
        commands = [["a","b","c","d"],["A","B","C","D"]]
        arduino.write(commands[state][number-1].encode())
        time.sleep(0.1)
        arduino.close()  # Close the serial connection


if __name__ == "__main__":
    # update_esp8266_ip()
    relay_request(1,0,ip=ESP8266_IP)