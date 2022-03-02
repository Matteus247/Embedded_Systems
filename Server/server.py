from concurrent.futures import process
import socket
import threading
import paho.mqtt.client as mqtt
import json
import eventlet
import socketio
import matplotlib.pyplot as plt
import scipy
import scipy.signal
from scipy import integrate
import numpy as np
import math

#DATABASE SUPPORT CODE FOR AXELERATE TRACKER
import time
from sys import getsizeof
import sqlite3 as db
from datetime import datetime

############################################################
#                     START OF DATABASE                    #
############################################################


# Initialiase the database
def database_init():
    ### INITIALISE A NEW TABLE WITH THE FOLLOWING ATTRIBUTES ###
    connection = db.connect("skating_data.db")
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS sessions (
                                                date DATE,
                                                time TIME,
                                                air_time FLOAT,
                                                landing_time FLOAT,
                                                total_rotation FLOAT,
                                                peak_rotation FLOAT,
                                                toe_heavy BOOL) """)

# Store the given data in the databse
def database_write(air_time, landing_time, total_rotation, peak_rotation, toe_heavy):
    connection = db.connect("skating_data.db")
    cursor = connection.cursor()

    ### GET CURRENT TIME TO PAIR WITH INCOMING DATA ###
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.today().strftime('%H:%M:%S')

    ### INSERT WHOLE DATA TO DATABASE ###
    data_to_upload = (current_date, current_time, air_time, landing_time, total_rotation, peak_rotation, toe_heavy)
    db_insert_statement = "INSERT INTO sessions VALUES (?,?,?,?,?,?,?)"
    cursor.execute(db_insert_statement, data_to_upload)

    ### SAVE DATABASE STATE ###
    connection.commit()

# Get the relevant data between the two timestamps
def database_read(start_date, end_date):
    air_time_list = []
    landing_time_list = []
    total_rotation_list = []
    peak_rotation_list = []
    toe_heavy_list = []

    ### RETRIEVE DATA FROM THE DATABASE ###
    connection = db.connect("skating_data.db")
    cursor = connection.cursor()

    db_select_statement = "SELECT * FROM sessions WHERE date BETWEEN ? AND ?"
    date_range = (start_date, end_date)
    cursor.execute(db_select_statement, date_range)

    ### GET ALL THE ENTRIES RETURNED FROM THE SELECT STATEMENT ###
    results = cursor.fetchall()
    #print(results)

    ### ADD ALL VALUES TO THEIR CORRESPONDING LISTS ###
    for i in range (0, len(results)):
        air_time_list.append((i+1,results[i][2]))
        landing_time_list.append((i+1,results[i][3]))
        total_rotation_list.append((i+1,results[i][4]))
        peak_rotation_list.append((i+1,results[i][5]))
        toe_heavy_list.append((i+1,results[i][6]))

    print(air_time_list, landing_time_list, total_rotation_list, peak_rotation_list, toe_heavy_list)

    return (air_time_list, landing_time_list, total_rotation_list, peak_rotation_list, toe_heavy_list)

############################################################
#               START OF SIGNAL PROCESSING                 #
############################################################

# Create a 1D gaussian filter
def gaussian_filter_1d(sigma):
    # sigma: the parameter sigma in the Gaussian kernel (unit: pixel)
    #
    # return: a 1D array for the Gaussian
    size = 6 * sigma
    h = np.zeros(size + 1)
    for i in range(size + 1):
        x = i - 3 * sigma
        h[i] = math.exp(-(x**2) / (2 * sigma * sigma)) / (np.sqrt(2 * np.pi) * sigma)
    return h

# Takes a starting index and returns a tuple containing the peak value, the time of the peak value and the index of the value AFTER the starting index.
def findPeakValue(arr_data, starting_index, arr_time):
    peak_value = 0.0
    peak_value_time = 0
    index = 0
    for i in range(len(arr_data) - starting_index):
        #print(arr[i])
        if peak_value < arr_data[starting_index + i]:
            peak_value = arr_data[starting_index + i]
            peak_value_time = arr_time[starting_index + i]
            index = starting_index + i
    return (peak_value, peak_value_time, index)

# Takes a starting index and returns a tuple containing the through value, the time of the through value and the index of the value BEFORE the starting index.
def findTroughValue(arr_data, starting_index, arr_time):
    trough_value = 0.0
    trough_value_time = 0
    index = 0
    for i in range(starting_index + 1):
        #print(arr[i])
        if trough_value > arr_data[starting_index - i]:
            trough_value = arr_data[starting_index - i]
            trough_value_time = arr_time[starting_index - i]
            index = starting_index - i
    return (trough_value, trough_value_time, index)

# Performs a binary search and returns the indices of the two closest elements
def binarySearch(data, val):
    highIndex = len(data)-1
    lowIndex = 0

    while highIndex > lowIndex:
            index = (highIndex + lowIndex) // 2
            sub = data[index]
            if data[lowIndex] == val:
                    return [lowIndex, lowIndex]
            elif sub == val:
                    return [index, index]
            elif data[highIndex] == val:
                    return [highIndex, highIndex]
            elif sub > val:
                    if highIndex == index:
                            return sorted([highIndex, lowIndex])
                    highIndex = index
            else:
                    if lowIndex == index:
                            return sorted([highIndex, lowIndex])
                    lowIndex = index
    return sorted([highIndex, lowIndex])

# Does a linear search for the closest element to a target value
def searchClosest(data, val):
    current_closest = (0, 0)
    for i in range(len(data) - 1):
        if (val - (data[current_closest[0]] + data[current_closest[1]]) / 2) > (val - (data[i] + data[i + 1]) / 2) :
            current_closest = (i, i + 1)
            

    return current_closest

# Does a linear search for the closest element to a target value starting from a given time
def searchClosestWithTime(data, val, times, startFrom):
    current_closest = (0, 0)

    index = 0
    while times[index] < startFrom:
        index = index + 1

    for item in data[index:]:
        if ((val - (data[current_closest[0]] + data[current_closest[1]]) / 2) > (val - (data[index - 1] + data[index]) / 2)):
            current_closest = (index - 1, index)
        index = index + 1

    return current_closest

# Given the time return the value at that given time
def findValueByTime(time, arr_data, arr_time):
    index1, index2 = binarySearch(arr_time, time)
    value = (arr_data[index1] + arr_data[index2]) / 2

    return value

# Given the time return the index of that given time
def findIndexByTime(time, arr_time):
    index1, index2 = binarySearch(arr_time, time)
    return max(index1, index2)

# Given the value return the first time that has the closest value
def findTimeByValue(value, arr_data, arr_time, startFrom):
    index1, index2 = searchClosestWithTime(arr_data, value, arr_time, startFrom)
    print(arr_time[index1], arr_time[index2])
    value = (arr_time[index1] + arr_time[index2]) / 2

    return value

# Given the index of the peak value find the start and the end of the event
def findRotationInterval(arr, peakIndex):
    startIndex = 0
    endIndex = 0
    for i in range(peakIndex + 1):
        if arr[peakIndex - i] == 0:
            startIndex = peakIndex - i
            break

    for i in range(len(arr) - peakIndex):
        if arr[peakIndex + i] == 0:
            endIndex = peakIndex + i
            break
    return (startIndex, endIndex)

# processes the 6 given signals and return the air time, landing stiffness, the total rotation in degrees, the peak angular velocity and whether the signal is toe or heel heavy
def signalProcessing(d_toe, t_toe, d, t, spin_data, spin_time):
    d_toe.reverse()
    t_toe.reverse()
    t.reverse()
    d.reverse()
    spin_data.reverse()
    spin_time.reverse()

    difference_kernel = [1, 0, -1]
    gaussian = gaussian_filter_1d(11)

    gaussian_smoothed_signal = (scipy.signal.convolve(d, gaussian))[:2500]

    # scale time because of delay added by gaussian
    gaussian_t = list(range(len(t)))
    for i in range(len(t)):
        gaussian_t[i] = t[i] - 0.15

    difference_signal = scipy.signal.convolve(gaussian_smoothed_signal, difference_kernel)

    # This is the index of the time in relation to the gyro signal
    jump_midpoint, jump_midpoint_time, jump_midpoint_index = findPeakValue(spin_data, 0, spin_time)
    
    #Check if there is  rotation
    if(jump_midpoint <= 0):
        return {"air_time":0, "landing_time":0, "total_rotation":0, "jump_midpoint":0, "isToeHeavy":False}

    intervalStart, intervalEnd = findRotationInterval(spin_data, jump_midpoint_index)

    total_rotation = integrate.cumtrapz(spin_data[intervalStart:intervalEnd], spin_time[intervalStart:intervalEnd])[-1]
    print("Total rotation: ", total_rotation)
    print("Jump Mid-point: ", jump_midpoint_time, " ", jump_midpoint )

    #DIFFERENCE PLOT
    # We use the jump_midpoint_time to find the index in the correct time stamp.
    # Here we are looking for the point of landing and therefore must be after the jump_midpoint_time
    highest_derivative, highest_derivative_time, highest_derivative_time_index = findPeakValue(difference_signal, findIndexByTime(jump_midpoint_time, gaussian_t), gaussian_t)

    lowest_derivative, lowest_derivative_time, lowest_derivative_time_index = findTroughValue(difference_signal, findIndexByTime(jump_midpoint_time, gaussian_t), gaussian_t)
    
    print("Start jump: ", lowest_derivative_time)

    landing_peak_value, a, peak_index = findPeakValue(gaussian_smoothed_signal, findIndexByTime(jump_midpoint_time, gaussian_t), gaussian_t)

    takeoff_peak_value, _, takeoff_peak_index = findPeakValue(d_toe[:findIndexByTime(jump_midpoint_time, gaussian_t)], 0, t_toe)
    landToe_peak_value, _, landToe_peak_index = findPeakValue(d_toe, findIndexByTime(jump_midpoint_time, gaussian_t), t_toe)
    
    print("TOE: ", takeoff_peak_value, " ", landToe_peak_value)
    
    isToeHeavy = True if takeoff_peak_value <= landToe_peak_value else False

    finished_landing_point = landing_peak_value * 0.4

    # Find the threshold value which represents the end of the landing
    index = 0
    for point in gaussian_smoothed_signal[peak_index:]:
        if point < finished_landing_point:
            break
        index += 1

    print("Started landing time: ", gaussian_t[peak_index])
    air_time = highest_derivative_time - lowest_derivative_time
    print("Air time: ", air_time)
    print("Finished landing time: ", gaussian_t[peak_index + index - 1])
    landing_time = gaussian_t[peak_index + index -1 ] - gaussian_t[peak_index]
    print("Landing time: ", landing_time)

    total_rotation = total_rotation*57.296
    return {"air_time":air_time, "landing_time":landing_time, "total_rotation":total_rotation, "jump_midpoint":jump_midpoint, "isToeHeavy":isToeHeavy}



##########################################################
#               END OF SIGNAL PROCESSING                 #
##########################################################

# The mqtt stores the messages in this queue and the socket connection gets the first message in the queue and sends it to the front-end or request
messageQueue = []

sio = socketio.Server(cors_allowed_origins='*')

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('msg')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

# Event to handle sending data of the current event
@sio.on('getData')
def getData(sid, data):
    print('message ', messageQueue)
    while len(messageQueue) > 0:
        print(type(messageQueue))
        sio.emit('setData', messageQueue.pop(0))

# Event to handle retrieving data of the database
@sio.on('dbQuery')
def dbQuery(sid, data):
    print(data)
    pulled_data = database_read(data["startDate"],data["endDate"])
    return_dict = {
        "air_time_list": pulled_data[0],
        "landing_time_list": pulled_data[1], 
        "total_rotation_list": pulled_data[2], 
        "peak_rotation_list": pulled_data[3], 
        "toe_heavy_list": pulled_data[4]
    }
    sio.emit('databaseReturn', return_dict)

######################################################
#               START OF MQTT SET UP                 #
######################################################
def on_message(client, userdata, message) :
    msg_decoced = str(message.payload.decode("utf-8", "ignore"))
    data = json.loads(msg_decoced)

    processedData = signalProcessing(data["toe_data"], data["toe_time"], data["heel_data"], data["heel_time"], data["spin_data"], data["spin_time"])

    messageQueue.append(processedData)

    database_write(processedData["air_time"], processedData["landing_time"], processedData["total_rotation"], processedData["jump_midpoint"], processedData["isToeHeavy"])

def on_disconnect(client, userdata,rc=0):
    client.loop_stop()

def on_publish(client, userdata, result):
    #print("published data is: ")
    pass

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")
 
Connected = False   #global variable for the state of the connection

# Creating the mqtt client
client = mqtt.Client()

# Callback functions
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_connect= on_connect

# Provides the private key/certificats needed to make a secure connection
#client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt", keyfile="client.key")

# Connect to port 8884 in order to make a secure connection 8884
client.connect("146.169.153.141",port=1883)

#subscribe to that topic
client.subscribe("IC.embedded/GROUP_NAME/#")

# Starts a new thread, that calls the loop method at regular intervals for you.
# It also handles re-connects automatically.
client.loop_start()

######################################################
#                 END OF MQTT SET UP                 #
######################################################

print("[STARTING] server is starting...")
# start()
if __name__ == '__main__':
    database_init()
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)



connection.close()
