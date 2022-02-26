#DATABASE SUPPORT CODE FOR AXELERATE TRACKER

import time
from sys import getsizeof
import sqlite3 as db
import numpy as np
from datetime import datetime



def database_init():
    ### INITIALISE A NEW TABLE WITH THE FOLLOWING ATTRIBUTES ###

    cursor.execute("""CREATE TABLE IF NOT EXISTS sessions (
                                                date DATE,
                                                time TIME,
                                                air_time FLOAT,
                                                landing_time FLOAT,
                                                total_rotation FLOAT,
                                                peak_rotation FLOAT,
                                                toe_heavy BOOL) """)


def database_write(air_time, landing_time, total_rotation, peak_rotation, toe_heavy):

    ### GET CURRENT TIME TO PAIR WITH INCOMING DATA ###
    current_date = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.today().strftime('%H:%M:%S')

    ### INSERT WHOLE DATA TO DATABASE ###
    data_to_upload = (current_date, current_time, air_time, landing_time, total_rotation, peak_rotation, toe_heavy)
    db_insert_statement = "INSERT INTO sessions VALUES (?,?,?,?,?,?,?)"
    cursor.execute(db_insert_statement, data_to_upload)

    ### SAVE DATABASE STATE ###
    connection.commit()


def database_read(start_date, end_date):
    ### RETRIEVE DATA FROM THE DATABASE ###

    db_select_statement = "SELECT * FROM sessions WHERE date BETWEEN ? AND ?"
    date_range = (start_date, end_date)
    cursor.execute(db_select_statement, date_range)

    ### GET ALL THE ENTRIES RETURNED FROM THE SELECT STATEMENT ###
    results = cursor.fetchall()
    #print(results)

    ### ADD ALL VALUES TO THEIR CORRESPONDING LISTS ###
    for i in range (0, len(results)):
        air_time_list.append(i+1,results[i][2])
        landing_time_list.append(i+1,results[i][3])
        total_rotation_list.append(i+1,results[i][4])
        peak_rotation_list.append(i+1,results[i][5])
        toe_heavy_list.append(i+1,results[i][6])

    return air_time_list, landing_time_list, total_rotation_list, peak_rotation_list, toe_heavy_list



### Test code, check to see how the functions should be called in back-/front-end ###
connection = db.connect("skating_data.db")
cursor = connection.cursor()

air_time_list = []
landing_time_list = []
total_rotation_list = []
peak_rotation_list = []
toe_heavy_list = []
#All of the above needed for proper functionality

#initialise db
database_init()

#write to db
database_write(0,2,4,6,8)
time.sleep(2)
database_write(1,3,5,7,9)

#read from db
(air_time_list, landing_time_list, total_rotation_list, peak_rotation_list, toe_heavy_list) = database_read("2022-02-26", "2022-02-26")
print(air_time_list, landing_time_list, total_rotation_list, peak_rotation_list, toe_heavy_list)


### NOT SURE ATM HOW ESSENTIAL THIS IS, FURTHER READING NEEDED ###
connection.close()
