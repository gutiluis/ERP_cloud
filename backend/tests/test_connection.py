#!/usr/bin/env python3

'''

filename: test_connection.py
descr: script to check connection of mysql db inside the docker container
# need a venv to install pymysql
# the host is 127.0.0.1:3307 because it's not running in a container
# the host is not db serice name
do not forget to give the permissions to the user rookie

'''
'''
# second test
import pymysql.cursors
connection = pymysql.connect(host="127.0.0.1",
                            user="erp",
                            port=3307,
                            password="erp",
                            database="erp",
                            cursorclass=pymysql.cursors.DictCursor)
with connection:
    with connection.cursor() as cursor:
        sql = "SHOW DATABASES;"
        cursor.execute(sql)
#        result = cursor.fetchone() # return first database returned only
        result = cursor.fetchall()
        print(result)
'''
import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    user="erp",
    password="erp",
    database="erp",
    port=3307,
)

with conn:
    with conn.cursor() as cursor:
        sql = "SHOW DATABASES;"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)