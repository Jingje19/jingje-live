from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/aboutKJJ", methods=['GET','POST'])
def about1():
    return render_template('http://jingje.s3-website-us-east-1.amazonaws.com')


@app.route("/aboutHR", methods=['GET','POST'])
def about2():
    return render_template('http://jingje.s3-website-us-east-1.amazonaws.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    birth_date = request.form['birth_date']
    gender = request.form['gender']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    department = request.form['department']
    job = request.form['job']
    date = request.form['date']
    salary = request.form['salary']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, birth_date, gender, email, phone, address, department, job, date, salary))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id)
        emp_body = "emp id: "+ str(emp_id) + "\nfirst name: "+ str(first_name) + "\nlast name: "+ str(last_name) +"\nBirth Date: "+ str(birth_date) +"\nGender: "+ str(gender) +"\nEmail: "+ str(email) +"\nPhone: "+ str(phone) +"\nAddress: "+ str(address) +"\nDepartment: "+ str(department) +"\nJob Title: "+ str(job) +"\nStart Date: "+ str(date) +"\nSalary: "+ str(salary)
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading files to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_body)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template('GetEmp.html')

@app.route("/fetchdata", methods=['POST'])
def GetEmpOutput():
    ids = request.form['emp_id']
    get_sql = "select * from employee where emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(get_sql, ids)
    myresult = cursor.fetchall()
    
    emp_image_file_name_in_s3 = "emp-id-" + str(ids)
    s3 = boto3.resource('s3')
    s3_client = s3.meta.client

    try:
        print("Data downloading from S3...")
        s3_response = s3_client.get_object(
        Bucket= custombucket,
        Key=emp_image_file_name_in_s3
)

        s3_object_body = s3_response.get('Body')

     
    finally:
        cursor.close()
    return render_template('GetEmpOutput.html',eid = myresult[0][0], fname = myresult[0][1], lname = myresult[0][2], Birth = myresult[0][3], Gender = myresult[0][4]
                          , Email = myresult[0][5], Phone = myresult[0][6], Address = myresult[0][7], Department = myresult[0][8], Job_title = myresult[0][9], Employment_Start = myresult[0][10], salary = myresult[0][11])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

