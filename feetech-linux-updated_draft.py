#=============FEETECH SERVO MOTOR-MODBUS RTU (LINUX VERSION)=================
import minimalmodbus as mod
from feetech import api #removed
import time
from datetime import datetime, date
import os


#---------preparing the file path
'''
_date = str(date.today())
script_dir = os.path.dirname(__file__)
txt_path = os.path.join(script_dir, ''.join([_date, '.txt']))
'''

#---------initializing instrument
for x in range(0, 5):            #trying to connect 5 times             #CHECK IF THIS WILL LIMIT THE CONNECTION
    _date = str(date.today())
    script_dir = os.path.dirname(__file__)
    txt_path = os.path.join(script_dir, ''.join([_date, '.txt']))
    try:
        instrument = mod.Instrument('/dev/ttyUSB1', 1, mode = mod.MODE_RTU)
        err = None
    except Exception as e:
        err = e
        print("exception")
        pass
        
    if err:
        with open(txt_path, 'a') as f:
            f.write("----- ERROR: Could not connect to device -----")
            f.write('\n')
        time.sleep(2)               #waiting 2 seconds to try reconnecting
    else:
        print("Stuck at connecting")
        break
        #raise 
    

#---------settings
instrument.serial.baudrate = 115200
instrument.serial.bytesize = 8
instrument.serial.parity = mod.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1       #seconds

#---------port
instrument.close_port_after_each_call = False
instrument.clear_buffers_before_each_transaction = True


#---------reset function
def reset():   
    print("Reset function triggered")
    read_save(txt_path)

    start_time = time.time()
    while instrument.read_register(api.pres_pos) != 1520 and (time.time() - start_time) < 6:
        instrument.write_register(api.goal_pos, 1520)
    
    if instrument.read_register(api.pres_pos) == 1520:
        with open(txt_path, 'a') as f:
            f.write("----- Motor has been reset -----")
            f.write('\n')
            print("Motor has been reset")
        return True
    elif (time.time() - start_time) >= 6: 
        with open(txt_path, 'a') as f:
            f.write("----- ERROR: Motor cannot be reset -----")
            f.write('\n')
            print("Motor cannot be reset")
        #return False
        raise
#---------saving data function
def read_save(txt_path):
    err_stat = str(instrument.read_register(api.hardware_err_status))
    err_reset = str(instrument.read_register(api.err_reset))    
    volt = str(instrument.read_register(api.pres_in_volt))
    curr = str(instrument.read_register(api.pres_curr))
    temp = str(instrument.read_register(api.pres_temp))   
    vel = str(instrument.read_register(api.pres_vel))
    pos = str(instrument.read_register(api.pres_pos))  
    date_time = str(datetime.now())         #format: date time
    
    info = [date_time, err_stat, err_reset, volt, curr, temp, vel, pos]
    
    with open(txt_path, 'a') as f:
        for i in info:
            f.write(i)
            f.write(',')
        f.write('\n')

    print("Info saved in text file")
    

#----------action function
def move_to(_pos):
    # instrument.write_register(api.work_mode, 0)
    # instrument.write_register(api.torq_enable, 1)
    print("Passing through move to and pos sent = ", _pos)
    
    start_time = time.time()
    while instrument.read_register(api.pres_pos) != _pos and (time.time()-start_time) < 0.5:
        instrument.write_register(api.goal_pos, _pos)
    
    if 1520<=instrument.read_register(api.pres_pos) <= 1700 or (2400<=instrument.read_register(api.pres_pos)<=2600):
        curr_pos = instrument.read_register(api.pres_pos)
        print("After moving position is = ", curr_pos)
        return 
    else: return False
    
#----------calling
        
try:
    with open(txt_path, 'a') as f:
        f.write("----- Program Started -----")
        f.write('\n')
        
    instrument.write_register(api.work_mode, 0)
    instrument.write_register(api.torq_enable, 1)
    res = reset()
    if res == True:pass
    elif res == False: raise
    while True:
        new_date = str(date.today())
        print(new_date, _date)
        if new_date != _date:
            _date = new_date
            script_dir = os.path.dirname(__file__)
            txt_path = os.path.join(script_dir, ''.join([_date, '.txt']))
        
        if 1520<=instrument.read_register(api.pres_pos)<=1700: 
            res = move_to(2600)                     #180
            if res == False: reset()
            read_save(txt_path)
        elif 2400<=instrument.read_register(api.pres_pos)<=2600: 
            res = move_to(1520)                     #new zero
            if res == False: reset()
            read_save(txt_path)
except:
    with open(txt_path, 'a') as f:
        f.write("----- Program cannot be executed ----")
        f.write("\n") 
    raise


#------HARD RESET IN CASE OF FAILURE
#instrument.write_register(15, 61313)
#pos_off = instrument.read_register(15)
#print("Position offset value changed to = ", pos_off)
#curr_pos = instrument.read_register(api.pres_pos)
#print("current position = ", curr_pos)

#instrument.write_register(api.goal_pos, 0)
#instrument.write_register(api.goal_pos, 1024)
#curr_pos = instrument.read_register(api.pres_pos)
#print("current position after = ", curr_pos)\



