from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_mysqldb import MySQL
import pymysql
import re
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "b'?`\x7fN\x10Ty\x9d\xf6\xff\xa3\x08\xde\xe0a\xc2\x1aIAR\xb8\x9d\xa8\x07"
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'plants_care_db'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'plantscaremanagement@gmail.com'
app.config['MAIL_PASSWORD'] = 'plantslogin123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
mysql = MySQL(app)





@app.route('/')
def root():
    return render_template('index.html')

@app.route('/login')
def showlogin():
    return render_template('login.html')

@app.route('/signup')
def showsignup():
    return render_template('signup.html')

@app.route('/forgotpassword')
def showforgotpassword():
    return render_template('forgotpassword.html')

@app.route('/upload')
def home():
    if 'loggedin' in session:
        return render_template('image.html', username = session['username'])

    return redirect(url_for('login'))



### user login 
##
#
##
#
@app.route('/pythonlogin', methods=['GET', 'POST'])
def login():
    cursor = mysql.connection.cursor()
    msg = ''
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
        username = request.form['Username']
        password = request.form['Password']
        cursor.execute('SELECT * FROM user_login WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg = msg, name = session.get('username'))

@app.route('/registeruser', methods=['GET', 'POST'])
def register():
 # connect
    conn = mysql.connection
    cursor = conn.cursor()
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form and 'Email' in request.form:
        # Create variables for easy access
        firstname = request.form['Firstname']
        lastname = request.form['Lastname']
        username = request.form['Username']
        password = request.form['Password']
        email = request.form['Email']
   
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM user_login WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user_login VALUES (NULL, %s, %s, %s, %s, %s)', (username, password, email, firstname, lastname)) 
            msg = 'You have successfully registered!'
            conn.commit()
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('signup.html', msg=msg)

@app.route('/sendpassword', methods=['POST', 'GET'])
def sendpassword():
    cursor = mysql.connection.cursor()
    msg = ''
    if request.method == 'POST' and 'Username' in request.form and 'Email' in request.form:
        username = request.form['Username']
        email = request.form['Email']
        cursor.execute('SELECT password FROM user_login WHERE username = %s AND email = %s', (username, email))
        data = cursor.fetchone()
        if data:
            msg = Message('Plants Care Password', sender = 'plantscaremanagement@gmail.com', recipients = [email])
            msg.body = "Hello User, this is your Plants Care account password: " + str(data[0])
            mail.send(msg)
            msg = "Password sent to your email"
        else:
            msg = 'Incorrect username and email combination'
    return render_template('forgotpassword.html', msg = msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('root'))


## user login over
##
#
#



# admin stuff
###
##
##
#
@app.route('/admin')
def showadmin():
    return render_template('admin_login.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    cursor = mysql.connection.cursor()
    msg = ''
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
        username = request.form['Username']
        password = request.form['Password']
        cursor.execute('SELECT * FROM admin_login WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['adminloggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('admindashboard'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('admin_login.html', msg = msg)






@app.route('/admindashboard')
def admindashboard():
    if 'adminloggedin' in session:
        return render_template('admin_index.html')
    return redirect(url_for('adminlogin'))




@app.route('/adminusers')
def adminusers():
    if 'adminloggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM user_login")
        data = cur.fetchall()
        cur.close()
        return render_template('admin_users.html', users=data)
    return redirect(url_for('adminlogin'))



@app.route('/insertusers', methods = ['POST'])
def insertusers():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user_login (username, password, email, last_name, first_name) VALUES (%s, %s, %s, %s, %s)", (username, password, email, first_name, last_name))
        mysql.connection.commit()
        return redirect(url_for('adminusers'))




@app.route('/deleteusers/<string:id_data>', methods = ['GET'])
def deleteusers(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_login WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('adminusers'))



@app.route('/updateusers',methods=['POST','GET'])
def updateusers():
    if request.method == 'POST':
        id_data = request.form['id']
        username = request.form['user_name']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE user_login
               SET username=%s, password=%s,
               email=%s, first_name=%s, last_name=%s
               WHERE id=%s
            """, (username, password, email, first_name, last_name, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('adminusers'))


@app.route('/adminplants')
def adminplants():
    if 'adminloggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM plant")
        data = cur.fetchall()
        cur.close()
        return render_template('admin_plants.html', plants=data)
    return redirect(url_for('adminlogin'))


@app.route('/insertplants', methods = ['POST'])
def insertplants():

    if request.method == "POST":
        flash("Data Inserted Successfully")
        label = request.form['label']
        plant_name = request.form['plant_name']
        scientific_name = request.form['scientific_name']
        status = request.form['status']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO plant (label, plantName, scientificName, status) VALUES (%s, %s, %s, %s)", (label, plant_name, scientific_name, status))
        mysql.connection.commit()
        return redirect(url_for('adminplants'))


@app.route('/deleteplants/<string:id_data>', methods = ['GET'])
def deleteplants(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM plant WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('adminplants'))

@app.route('/updateplants', methods = ['POST'])
def updateplants():

    if request.method == "POST":    
        id_data = request.form['id']
        label = request.form['label']
        plant_name = request.form['plant_name']
        scientific_name = request.form['scientific_name']
        status = request.form['status']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE plant
               SET label=%s, plantName=%s,
               scientificName=%s, status=%s
               WHERE id=%s
            """, (label, plant_name, scientific_name, status, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('adminplants'))


@app.route('/adminplantdetails')
def adminplantdetails():
    if 'adminloggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM plant_details")
        data = cur.fetchall()
        cur.close()
        return render_template('admin_plant_details.html', plant_details=data)
    return redirect(url_for('adminlogin'))

@app.route('/insertplantdetails', methods = ['POST'])
def insertplantdetails():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        label = request.form['label']
        plant_name = request.form['plant_name']
        fun_fact = request.form['fun_fact']
        tips = request.form['tips']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO plant_details (label, plantName, funFact, tips) VALUES (%s, %s, %s, %s)", (label, plant_name, fun_fact, tips))
        mysql.connection.commit()
        return redirect(url_for('adminplantdetails'))


@app.route('/deleteplantdetails/<string:id_data>', methods = ['GET'])
def deleteplantdetails(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM plant_details WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('adminplantdetails'))

@app.route('/updateplantdetails', methods = ['POST'])
def updateplantdetails():

    if request.method == "POST":    
        id_data = request.form['id']
        label = request.form['label']
        plant_name = request.form['plant_name']
        fun_fact = request.form['fun_fact']
        tips = request.form['tips']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE plant_details
               SET label=%s, plantName=%s,
               funFact=%s, tips=%s
               WHERE id=%s
            """, (label, plant_name, fun_fact, tips, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('adminplantdetails'))





@app.route('/adminsearchdisease')
def adminsearchdisease():
    if 'adminloggedin' in session:
        return render_template('admin_search_disease.html')
    return redirect(url_for('adminlogin'))



@app.route('/admindiseasedetails', methods=['POST'])
def admindiseasedetails():
    error_string = ""
    if 'adminloggedin' in session:
        label = request.form['label']
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM disease_details where label=%s", (label,))
        data = cur.fetchall()
        if len(data) == 0:
            error_string = "you entered wrong label"
            return render_template('admin_search_disease.html', err = error_string)
        cur.close()
        return render_template('admin_disease_details.html', plant_disease=data)
    return redirect(url_for('adminlogin'))



@app.route('/insertdiseasedetails', methods = ['POST'])
def insertdiseasedetails():
    if request.method == "POST":
        flash("Data Inserted Successfully")  
        label = request.form['label']
        disease_name = request.form['disease_name']
        plant_name = request.form['plant_name']
        scientific_name = request.form['scientific_name']
        pathogen = request.form['pathogen']
        symptoms = request.form['symptoms']
        host_name = request.form['host_name']
        trigger_details = request.form['trigger_details']
        bio_controls = request.form['bio_controls']
        chem_controls = request.form['chem_controls']
        measures = request.form['measures']
        cur = mysql.connection.cursor()
        cur.execute("""
               INSERT INTO disease_details (label, diseaseName, plantName, scientificName, type_pathogen, symptoms, hostName, triggerDetails, bio_control, chemical_control, measures) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (label, disease_name, plant_name, scientific_name, pathogen, symptoms, host_name, trigger_details, bio_controls, chem_controls, measures))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM disease_details where label=%s", (label,))
        data = cur.fetchall()
        cur.close()
        return render_template('admin_disease_details.html', plant_disease=data)


@app.route('/updatediseasedetails', methods = ['POST'])
def updatediseasedetails():
    if request.method == "POST":    
        id_data = request.form['id']
        label = request.form['label']
        disease_name = request.form['disease_name']
        plant_name = request.form['plant_name']
        scientific_name = request.form['scientific_name']
        pathogen = request.form['pathogen']
        symptoms = request.form['symptoms']
        host_name = request.form['host_name']
        trigger_details = request.form['trigger_details']
        bio_controls = request.form['bio_controls']
        chem_controls = request.form['chem_controls']
        measures = request.form['measures']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE disease_details
               SET label=%s, diseaseName=%s, plantName=%s,
               scientificName=%s, type_pathogen=%s, symptoms=%s,
               hostName=%s, triggerDetails=%s, bio_control=%s,
               chemical_control=%s, measures=%s
               WHERE id=%s
            """, (label, disease_name, plant_name, scientific_name, pathogen, symptoms, host_name, trigger_details, bio_controls, chem_controls, measures, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM disease_details where label=%s", (label,))
        data = cur.fetchall()
        cur.close()
        return render_template('admin_disease_details.html', plant_disease=data)


@app.route('/deletediseasedetails/<string:id_data>', methods = ['GET'])
def deletediseasedetails(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM disease_details WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('adminsearchdisease'))


@app.route('/adminlogout')
def adminlogout():
    # Remove session data, this will log the user out
   session.pop('adminloggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('adminlogin'))

## admin stuff over
##
##
####

if __name__ == '__main__':
    app.run(debug=True)