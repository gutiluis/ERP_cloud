#!/bin/env python
import datetime


'''
script to give the user permissions and make the erp_test db
after setting root user and password from the docker-compose.yml environment variables

do not forget datetime rookie

'''

import pymysql

# connection to MySQL container (use forwarded port)
connection = pymysql.connect(
    host="127.0.0.1",
    port=3307, # colima forwarded port from docker.compose.yml
    user="root",         # use root to create DB and grant permissions
    password="root"  # replace with your root password
)

with connection.cursor() as cursor:
    # create test DB
    cursor.execute("CREATE DATABASE IF NOT EXISTS erp_test;")
    
    # grant privileges to user after setting root password
    cursor.execute("GRANT ALL PRIVILEGES ON erp_test.* TO 'erp'@'%';")
    cursor.execute("FLUSH PRIVILEGES;")
    cursor.execute("FLUSH PRIVILEGES;")

print("[INFO]erp_test database created...\n")
print(datetime.datetime.now())
connection.close()
