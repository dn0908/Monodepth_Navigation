import serial
import time

serial_port = "/dev/ttymxc0" # For google coral dev board (UART port 0)
baud_rate = 115200

try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    time.sleep(2)
    
    message = "F"
    serial_write_start_time = time.perf_counter()
    ser.write(message.encode())
    serial_write_end_time = time.perf_counter()
    serial_writing_time = serial_write_end_time - serial_write_start_time
    print(f"Message sent: {message}")
    print(f"Serial writing time: {serial_writing_time}")
    time.sleep(1)

    essage = "F"
    serial_write_start_time = time.perf_counter()
    ser.write(message.encode())
    serial_write_end_time = time.perf_counter()
    serial_writing_time = serial_write_end_time - serial_write_start_time
    print(f"Message sent: {message}")
    print(f"Serial writing time: {serial_writing_time}")
    time.sleep(1)

    ser.close()

except serial.SerialException as e:
    print(f"Error: {e}")
