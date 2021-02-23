# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 02:18:01 2020

@author: atulr
"""

# importing libraries
import pickle
import sqlite3
import warnings
warnings.filterwarnings('ignore')

from flask import Flask, render_template, request


# load the complaint clasification model dumped in pickle format
complaints_class= pickle.load(open("./model/ComplaintClassificationMlModel.pkl",'rb')) 


print('THIS IS A PRINT FUNCTION')

# initalize REST API service
app= Flask(__name__)


# Home page
@app.route('/',methods=['POST','GET'])
def home():
    return render_template('home_page.html')


# Build API to call complaint classification model through web app
@app.route('/application.html', methods=['POST','GET'])
def complaint_submission():
    department_name=""
    message=""
    id_no=""
    if request.method == 'POST':
        try:
            customer_name = request.form['customer_name']
            customer_complaint = request.form['complaint_narrative']
            
            # accessing database complaint.db by conn
            with sqlite3.connect('./DB/complaint.db') as conn:  
                c= conn.cursor()     #create cursor by c name
                c.execute('insert into complaints_tab(cust_name,cust_complaint) values(?,?)',(customer_name,customer_complaint))
                conn.commit()
                c.execute('select MAX(id) from complaints_tab')
                id_no = c.fetchall()
            
            print(customer_complaint)
            department_name = complaints_class.predict([customer_complaint])
            print(department_name)
            message = 'Your complaint is assigned to: '+str(department_name)+' And ID is: '+str(id_no)
    
        except:
            conn.rollback()
            message = 'ERROR!!!'
          
        finally:
            conn.close()
       
    return render_template('application.html', complaint_status = message)

# List page
@app.route('/list_page.html')
def full_list():
    print("list page")
    conn= sqlite3.connect('./DB/complaint.db')
    conn.row_factory = sqlite3.Row
    
    c = conn.cursor()
    c.execute("select * from complaints_tab")
    
    rows = c.fetchall()
    conn.close()
    return render_template("list_page.html",rows = rows)

# check status page
@app.route('/check.html', methods=['POST','GET'])
def complaint_check():
    message_stu=""
    if request.method == 'POST':
        try:
            comp_id = request.form['id']
            # accessing database complaint.db by conn
            with sqlite3.connect('./DB/complaint.db') as conn:
                c = conn.cursor()     #create cursor by c name
                c.execute('select complany_resp from complaints_tab where id = ?',comp_id)
                status = c.fetchall()
                
            print("ID is: "+comp_id)
            message_stu = 'Your complaint status is: '+str(status)
    
        except:
            conn.rollback()
            message_stu = 'Will be updated soon!!!'
          
        finally:
            conn.close()

    return render_template('check.html', complaint_status_message = message_stu)

# admin page
@app.route('/admin.html',methods=['POST','GET'])
def admin():
    return render_template('admin.html')                
             
# Responce page
@app.route('/responce.html')
def null_list():
    print("NULL list page")
    conn= sqlite3.connect('./DB/complaint.db')
    conn.row_factory = sqlite3.Row
    
    c = conn.cursor()
    c.execute('select * from complaints_tab where complany_resp IS NULL')
    rows = c.fetchall()
    conn.close()
    return render_template("responce.html",rows = rows)
  
@app.route('/responce.html',methods=['POST','GET'])  
def responce():           
    mess=""
    if request.method == 'POST':
        try:
            comp_id = request.form['id']
            res= request.form['res']
            # accessing database complaint.db by conn
            with sqlite3.connect('./DB/complaint.db') as conn:  
                c = conn.cursor()     #create cursor by c name
                c.execute('update complaints_tab set complany_resp = ? where id = ?',(res, comp_id))
                conn.commit()
                status = c.fetchall()
            print("ID is: "+comp_id)
            mess = 'Updated: '+str(status)
    
        except:
            conn.rollback()
            mess = 'Not updated!!!'
          
        finally:
            conn.close()

    return render_template('responce.html', update_message = mess)
   

# Run the API
if __name__ == '__main__':
    app.run()