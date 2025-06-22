from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for flash messages

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'acoounts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Initialize SQLALchemy
db = SQLAlchemy(app)
# Define Account model
class tblregister(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Stores encrypted password
    masterPassword = db.Column(db.String(256), nullable=False) 
    mobile = db.Column(db.String(20), nullable=True)
    

    def _repr_(self):
        return f'<register {self.account_name}>'
    
# Define Account model
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    account_url = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Stores encrypted password
    mobile_number = db.Column(db.String(20), nullable=True)
    narration = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False)
    tblregister_id = db.Column(db.Integer, nullable=False)

    def _repr_(self):
        return f'<Account {self.account_name}>'
    
    # Create database tables
with app.app_context():
     db.create_all()

@app.route('/')
def index():
    # credentials = Credential.query.all()
     return render_template('index.html')

# @app.route('/register', methods= ['GET','POST'])
# def register():
#     return render_template('register.html')

@app.route('/account', methods= ['GET','POST'])
def account(): 
    if request.method == 'POST':
        accountName = request.form.get('accountName')
        accountUrl = request.form.get('accountUrl')
        accountType = request.form.get('accountType')
        username = request.form.get('username')
        password = request.form.get('password')
        mobileNumber = request.form.get('mobileNumber')
        priority = request.form.get('priority')
        narration = request.form.get('narration')
        user_id = session['id']
    # Create new account
        add_account = Account(
            account_name=accountName,
            account_url=accountUrl,
            account_type=accountType,
            username=username,
            password=password,
            mobile_number=mobileNumber if mobileNumber else None,
            narration=narration if narration else None,
            priority=priority,
            tblregister_id=user_id
            )
        #     # Save to database
        db.session.add(add_account)
        db.session.commit()
        flash('Form added successfully!', 'success')
        print('save success..........')
        print(accountName)
        print(accountUrl)
        print(accountType)
        print(username)
        print(password)
        print(mobileNumber)
        print(priority)
        print(narration)
        return redirect(url_for('view_accounts1'))

    return render_template('account.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    # print("Hellooooooo.......")
    if request.method == 'POST':
        accountName = request.form.get('accountName')
        username = request.form.get('username')
        password = request.form.get('password')
        mobile = request.form.get('mobile')
        masterPassword = request.form.get('masterPassword')

        existing_user = tblregister.query.filter_by(username=username).first()

        if existing_user:
            flash('username/email already exist','error')
            return render_template('register.html')

        
         # Create new account
        add_account = tblregister(
            account_name=accountName,
            username=username,
            password=password,
            mobile=mobile if mobile else None,
            masterPassword=masterPassword
            )
   
   #     # Save to database
        db.session.add(add_account)
        db.session.commit()
        flash('Form submitted successfully!', 'success')
        print('save success..........')
        print(accountName)
        print(username)
        print(password)
        print(mobile)
        print(masterPassword)
        return redirect(url_for('login'))  # This will redirect to /login
    return render_template('register.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# @app.route('/view_accounts1')
# def view_accounts1():
#     return render_template('view_accounts1.html')

@app.route('/view_accounts1', methods=['GET', 'POST'])
def view_accounts1():
    if 'id' not in session:
        flash('Please Login first', 'errror')
        return redirect(url_for('login'))
    log_name = session['account_name']
    user_id = session['id']
    print(session['account_name'])
    print(session['id'])
    accounts = Account.query.filter_by(tblregister_id=user_id).all()  # Get all account records
    print(accounts)
    for a in accounts:
        print(a.account_name)
    return render_template('view_accounts1.html', accounts=accounts, log_name=log_name)

@app.route('/edit/<int:account_id>', methods=['GET', 'POST'])
def edit_account(account_id):
    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':
        account.account_name = request.form.get('accountName')
        account.account_url = request.form.get('accountUrl')
        account.account_type = request.form.get('accountType')
        account.username = request.form.get('username')
        account.password = request.form.get('password')
        account.mobile_number = request.form.get('mobileNumber')
        account.narration = request.form.get('narration')
        account.priority = request.form.get('priority')

        db.session.commit()
        flash('Account updated successfully.', 'success')
        return redirect(url_for('view_accounts1'))

    return render_template('edit_account.html', account=account)

@app.route('/delete/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    flash('Account deleted successfully.', 'success')
    return redirect(url_for('view_accounts1'))


@app.route('/login', methods=['GET', 'POST'])
# @app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')        
        masterPassword = request.form.get('masterPassword')
        # Select * from tblregister where username = username and password = password
        # ORM(Object Relational Model) flask_sqlalchemy
        user = tblregister.query.filter(
            (tblregister.username == username) & (tblregister.password == password) 
        ).first()
        if user:
            if(user.masterPassword == masterPassword):
                m1 = "Welcome to Account Mgr: " + user.account_name
                m2 = "Your Master Psw: " + user.masterPassword
                
                print(m1,m2)
                print("Login Success.")
            else:
                print("Login Fail.")

        if user:
            session['id'] = user.id
            session['account_name'] = user.account_name
        
            flash(f"Welcome, {user.account_name}!", "success")
            return redirect(url_for("view_accounts1")) # Redirect to account page after login

        else:
            flash("Invalid credentials or master password.", "error")
            return redirect(url_for("login"))                

    return render_template('login.html')

# @app.route('/register')
# def register():
#     print("1234343434343434............")
#     return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/features')
def features():
    return render_template('features.html')

if __name__ == '__main__':
    app.run(debug=True)