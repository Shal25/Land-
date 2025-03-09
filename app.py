from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import hashlib

app =Flask(__name__)
app.secret_key = "1234"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Qwerty@25"
app.config["MYSQL_DB"] = "property_db"

mysql = MySQL(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup_member', methods = ["GET","POST"])
def signup_member():
    if request.method =="POST":
        email = request.form["email"]
        password = hash_password(request.form["password"])

        cur = mysql.connection.cursor() 
        cur.execute("INSERT INTO member (email, password) VALUES (%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()
        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for('home'))

    return render_template('signup_member.html')

@app.route('/signup_user', methods=['GET', 'POST'])
def signup_user():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user (email, password) VALUES (%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()
        
        flash("User signup successful! You can now log in.", "success")
        return redirect(url_for('home'))

    return render_template('signup_user.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])

        cur = mysql.connection.cursor()

        # Check in member table
        cur.execute("SELECT * FROM member WHERE email = %s AND password = %s", (email, password))
        member = cur.fetchone()

        # Check in user table
        cur.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()

        cur.close()

        if member:
            session['email'] = email
            session['role'] = 'Member'
            flash("Login successful as Member!", "success")
            return redirect(url_for('dashboard'))
        elif user:
            session['email'] = email
            session['role'] = 'User'
            flash("Login successful as User!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')

# Dashboard after login
@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return f"Welcome {session['email']}! You are logged in as a {session['role']}."
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)