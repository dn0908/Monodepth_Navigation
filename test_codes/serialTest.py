import serial
import time

serial_port = "/dev/ttymxc0"
baud_rate = 115200

try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(2)
    
    message = "F"
    
    ser.write(message.encode())
    
    print(f"Message sent: {message}")
    time.sleep(1)
    message = "F"
    
    ser.write(message.encode())
    
    print(f"Message sent again: {message}")
    time.sleep(1)

    ser.close()

except serial.SerialException as e:
    print(f"Error: {e}")
