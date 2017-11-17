import os
import glob
import time
import datetime
import sqlite3

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Create database connection
conn = sqlite3.connect('home')
c = conn.cursor()

# Create beer fridge table if it doesn't already exist
c.execute('''CREATE TABLE IF NOT EXISTS beer_fridge (date text, time text, temp real, state integer)''')
conn.commit()

# Setup thermoster
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_raw_temp():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def get_temp():
    lines = read_raw_temp()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def save_temp(temp):
    current_time = datetime.datetime.now();
    date = current_time.strftime("%B %d, %Y")
    time = current_time.time().isoformat()
    insertion = [date, time, temp]
    c.execute('INSERT INTO beer_fridge (date, time, temp, state) VALUES (?, ?, ?, null)', (insertion,))
    conn.commit()

while True:
	temp = get_temp()
    print temp
    save_temp(temp)
	time.sleep(360)
