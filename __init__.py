from flask import Flask, render_template, request, redirect, url_for, make_response, session
import sys
import calendar_lib as evt
import sqlite3
from model import Class
from model_db_create import connect_db, init_db
from Forms import *
import shelve, Transaction
import smtplib
from CreateUsers import *
from flask_bcrypt import Bcrypt
import SupportTicket


# Flask setting 
HOST_NAME = 'localhost'
HOST_PORT = 80
app = Flask(__name__)
app.secret_key = '12345'
app.debug = True
bcrypt = Bcrypt(app)
 
 
def email_checker(email):
    db = shelve.open('Users.db', 'c')
    for key in db:
        value = db[key]
        if value.get_email() == email:
            db.close()
            return value #returns user object
    db.close()
    return None

def id_to_object(id):
    if id == None:
        return None
    db = shelve.open('Users.db', 'c')
    for key in db:
        value = db[str(key)]
        if value == "deleted account":
            continue

        if value.get_id() == id:
            db.close()
            return value #returns user object
    db.close()
    return None
#Makes id_to_object function into globally available in jinja
app.jinja_env.globals.update(id_to_object=id_to_object)

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

@app.route("/dashboard",methods=['GET','POST'] )
def dashboard():
    if session['user']:
        print('session user is valid')
        print(id_to_object(session['user']))
        try:
            user_name = id_to_object(session['user']).get_name()
            return render_template('dashboard.html',user = user_name)
        except:
            print('An error has occurred')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Contact Us
@app.route('/contactUs')
def contact_us():
    return render_template('contactUs.html')

# FAQ
@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

# Ethan's code

#Shop page (user)
@app.route('/shop',methods=['GET','POST'] )
def shop():
    if session['user']:
        db = shelve.open('storage.db.buyer', 'c')
        try:
            products_dict = db['Products']
        except:
            print("Error in retrieving Users from storage.db.")
        
        return render_template('shop.html',products_dict=products_dict)
    else:
        return redirect(url_for('login'))

#Products page (user)
@app.route('/product/<product_id>',methods=['GET'] )
def product(product_id):
    db = shelve.open('storage.db.buyer', 'c')
    try:
        products_dict = db['Products']
    except:
        print("Error in retrieving Users from storage.db.")

    product = products_dict.get(int(product_id))
    return render_template('product.html', product=product, products_dict=products_dict,product_id=product_id)
    
#Credit Card page to purhcase items (user)
@app.route('/creditcard/<product_id>',methods=['GET','POST'] )
def credit_card(product_id):
    db2= shelve.open('storage.db.buyer', 'c')
    try:
        products_dict = db2['Products']
    except:
        print("Error in retrieving Users from storage.db.")

    product = products_dict.get(int(product_id))
    user_id = session['user']
    print(user_id)
    user_cc = CreateCreditCardform(request.form)
    if request.method == 'GET':
        return render_template('cc.html', form=user_cc,products_dict=products_dict,product_id=product_id)
        #Display purchase form
    elif request.method == 'POST' and user_cc.validate():
        tx_dict = {}
        tx_db = shelve.open('tx.db', 'c')
        try:
            tx_dict = tx_db['Tx']
        except:
            tx_db['Tx'] = tx_dict
            print("Error in retrieving Tx")
        
        user = {}
        user_db = shelve.open('Users.db','c')
        try:
            user = user_db[int(user_id)]
        except:
            print(user)
            print("Error in retrieving User")
        
        tx = Transaction.Transaction(
            user_cc.first_name.data + " " + user_cc.last_name.data, 
            user_cc.card_number.data,
            user_id,
            user_cc.phone_number.data,
            user_cc.card_name.data,
            user_cc.exp_date.data,
            user_cc.cvc.data
        )

        tx.set_product_name(product['name'])
        tx.set_cost(product['price'])
        
        tx_dict[tx.get_tx_id()] = tx
        tx_db['Tx'] = tx_dict
        tx_db.close()
        user_db.close()

        return redirect(url_for('success'))

#Success page after submitting credit card details for purchasing a product (user)
@app.route('/success')
def success():
    return render_template('success.html')

# View more details about the transaction (staff)
@app.route('/tx/<tx_id>')
def database_by_id(tx_id):
    tx_db = shelve.open('tx.db', 'r')
    tx = None
    try:
        tx_dict = tx_db['Tx']
        tx = tx_dict[int(tx_id)]
    except:
        print("Error in retrieving Tx")
    
    return render_template('database_by_id.html',tx=tx)

# Edit the transaction from the database (staff)
@app.route('/tx/<tx_id>/edit', methods=["GET", "POST"])
def cannot_edit(tx_id):
    tx_db = shelve.open('tx.db', 'c')
    tx = None
    tx_dict = {}
    try:
        tx_dict = tx_db['Tx']
        tx = tx_dict[int(tx_id)]
    except:
        print("Error in retrieving Tx")

    if tx.get_status() == 'Complete':
        return render_template('cannot_edit.html')
        # render a page that says "transaction already confirmed" 

    if request.method == 'GET':
        user_cc = EditCreditCardform(
            name=tx.get_name(),
            phone_number=tx.get_pn(),
            card_name=tx.get_card_name(),
            card_number=tx.get_cc(),
            exp_date=tx.get_exp_date(),
            cvc=tx.get_cvc(),
            status=tx.get_status()
        )
        return render_template('edit.html', form=user_cc,tx=tx)
        #Display purchase form
    elif request.method == 'POST':

        user_cc = EditCreditCardform(request.form)
        if user_cc.validate():
            tx.set_name(user_cc.name.data)
            tx.set_pn(user_cc.phone_number.data)
            tx.set_card_name(user_cc.card_name.data)
            tx.set_cc(user_cc.card_number.data)
            tx.set_exp_date(user_cc.exp_date.data)
            tx.set_cvc(user_cc.cvc.data)
            tx.set_status(user_cc.status.data)

            tx_dict[int(tx_id)] = tx

            tx_db['Tx'] = tx_dict
            tx_db.close()

        return redirect(url_for('database'))

#Delete transaction from database (staff)
@app.route('/tx/<tx_id>/delete', methods=["GET", "POST"])
def delete_tx(tx_id):
    tx_db = shelve.open('tx.db', 'c')
    tx = None
    tx_dict = {}
    try:
        tx_dict = tx_db['Tx']
        tx = tx_dict[int(tx_id)]
    except:
        print("Error in retrieving Tx")
    
    if request.method == 'GET':
        return render_template('delete.html', tx=tx)

    elif request.method == 'POST':
        del tx_dict[int(tx_id)]
        tx_db['Tx'] = tx_dict
        tx_db.close()

        return redirect(url_for('database'))

#Cancel transaction (user) 
@app.route('/user/tx/<tx_id>/cancel', methods=["GET", "POST"])
def cancel_tx(tx_id):
    sess_user_id = session['user']

    tx_db = shelve.open('tx.db', 'c')
    tx = None
    tx_dict = {}
    try:
        tx_dict = tx_db['Tx']
        tx = tx_dict[int(tx_id)]
    except:
        print("Error in retrieving Tx")
    
    if sess_user_id != tx.get_user_id():
        return
    
    if tx.get_status == "Confirm":
        return

    if request.method == 'GET':
        return render_template('cancel.html', tx=tx)

    elif request.method == 'POST':
        del tx_dict[int(tx_id)]
        tx_db['Tx'] = tx_dict
        tx_db.close()

        return redirect(url_for('view_tx'))

# View more details about the transaction (user)
@app.route('/user/tx/<tx_id>')
def userview_tx(tx_id):
    tx_db = shelve.open('tx.db', 'r')
    tx = None
    try:
        tx_dict = tx_db['Tx']
        tx = tx_dict[int(tx_id)]
    except:
        print("Error in retrieving Tx")
    
    return render_template('database_by_id.html',tx=tx)

@app.route('/viewtx')
def view_tx():
    if session['user']:
        tx_db = shelve.open('tx.db', 'r')
        tx_dict = tx_db['Tx']
        user_id = session['user']
        transactions = []
        for tx_id in tx_dict:
            if tx_dict[tx_id].get_user_id() == int(user_id):
                transactions.append(tx_dict[tx_id])
        return render_template('tx.html', transactions=transactions)
    else:
        return redirect(url_for('login'))
    

# kaixuan's code
# (B) ROUTES
# (B1) CALENDAR PAGE
@app.route("/viewCalendar", methods=["GET", "POST"])
def index():
    if session['user']:
        return render_template("calendar.html")
    else:
        return redirect(url_for('login'))
# (B2) ENDPOINT - GET EVENTS
@app.route("/get/", methods=["POST"])
def get():
  data = dict(request.form)
  events = evt.get(int(data["month"]), int(data["year"]))
  return "{}" if events is None else events

# (B3) ENDPOINT - SAVE EVENT
@app.route("/save/", methods=["POST"])
def save():
  data = dict(request.form)
  ok = evt.save(data["s"], data["e"], data["t"], data["c"], data["b"], data["id"] if "id" in data else None)
  msg = "OK" if ok else sys.last_value
  return make_response(msg, 200)

# (B4) ENDPOINT - DELETE EVENT
@app.route("/delete/", methods=["POST"])
def delete():
  data = dict(request.form)
  ok = evt.delete(data["id"])
  msg = "OK" if ok else sys.last_value
  return make_response(msg, 200)

got_first_request = False

def initialize_database():
    init_db()

@app.before_request
def before_request():
    global got_first_request
    if not got_first_request:
        initialize_database()
        got_first_request = True

@app.route('/viewClasses')
def view_classes():
    if session['user']:
        if (id_to_object(session['user']).get_admin() == 1) or (id_to_object(session['user']).get_admin() == "1"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('SELECT id, title, description, date, time, duration FROM classes')
            rows = cur.fetchall()
            classes = [{'id': row[0], 'title': row[1], 'description': row[2], 'date': row[3], 'time': row[4], 'duration': row[5]} for row in rows]
            conn.close()
            return render_template('classes.html', classes=classes)
        else:
            return redirect(url_for('view_only_classes'))
    else:
        return redirect(url_for('login'))

@app.route('/add_class', methods=['POST'])
def add_class():
    if session['user']:
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO classes (title, description, date, time, duration) VALUES (?, ?, ?, ?, ?)', (title, description, date, time, duration))
        conn.commit()
        conn.close()
        return redirect(url_for('view_classes'))
    else:
        return redirect(url_for('login'))

@app.route('/update_class/<int:id>', methods=['POST'])
def update_class(id):
    title = request.form['title']
    description = request.form['description']
    date = request.form['date']
    time = request.form['time']
    duration = request.form['duration']
    
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        UPDATE classes
        SET title = ?, description = ?, date = ?, time = ?, duration = ?,
        WHERE id = ?
    ''', (title, description, date, time, duration, id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_classes'))


@app.route('/delete_class/<int:id>', methods=['POST'])
def delete_class(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM classes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_classes'))

@app.route('/viewOnlyClasses')
def view_only_classes():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, title, description, date, time, duration FROM classes')
    rows = cur.fetchall()
    classes = [{'id': row[0], 'title': row[1], 'description': row[2], 'date': row[3], 'time': row[4], 'duration': row[5]} for row in rows]
    conn.close()
    return render_template('view_only_classes.html', classes=classes)


# Shawn's Code
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db = shelve.open('Users.db','c')

    #Check if Users.db contains valid accounts
    try:
        for i in db:
            db[i].get_name()
    except AttributeError:
        return redirect(url_for('register'))
    
    if form.validate_on_submit():
        user = email_checker(form.email.data)
        if user:
            if bcrypt.check_password_hash(user.get_password(), form.password.data):
                print('correct password')
                
                session['user'] = user.get_id()
                print(session['user'])
                print('Sucessfully Logged In!')
                return redirect(url_for('dashboard'))
            else:
                print('wrong pass')
        else:
            print('user not found')
    else:
        print('did not validate')

    return render_template("login.html", form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db = shelve.open('Users.db', 'c')
        db[str(User.count)] = new_user
        db.close()
        print('Account Successfully Created!')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

#Ethan 5
@app.route("/view_profile", methods=['GET', 'POST'])
def view_profile():
    if session['user']:
        user = id_to_object(session['user'])

        return render_template("view_profile.html", name = user.get_name(), email = user.get_email(), password = user.get_password())
    else:
        return redirect(url_for('login'))

@app.route("/edit_profile", methods=['GET', 'POST'])
def edit_profile():
    if session['user']:
        form = EditProfileForm()
        current_user = id_to_object(session['user'])
        if request.method == 'POST':
            if form.validate_on_submit():
                if form.cancel.data:
                    return redirect(url_for('view_profile'))
                new_name =  request.form.get('name')
                new_email =  request.form.get('email')
                new_password =  request.form.get('password')
                if request.form.get('name'):
                    new_name =  request.form.get('name')
                else:
                    new_name = current_user.get_name()
                if request.form.get('email'):
                    new_email = request.form.get('email')
                else:
                    new_email = current_user.get_email()
                if request.form.get('password'):
                    new_password = bcrypt.generate_password_hash(request.form.get('password'))
                else:
                    new_password = current_user.get_password()
                
                current_user.set_name(new_name)
                current_user.set_email(new_email)
                current_user.set_password(new_password)


                #Update Shelve
                db = shelve.open('Users.db', 'c')
                db[str(session['user'])] = current_user
                session['user'] = current_user.get_id()
                print('Updated User information in position: ',session['user'])
                db.close()
                return redirect(url_for('view_profile'))
            else:
                print("Password must match")
        else:
            db = shelve.open('Users.db', 'w')
            user = db.get(str(session['user']))
            form.name.data = user.get_name()
            form.email.data = user.get_email()
            db.close()
        return render_template('edit_profile.html',form=form)
    else:
        return redirect(url_for('login'))


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if session['user']:
        if request.method == 'POST':
            user_id = str(session['user'])
            db = shelve.open('Users.db', 'c')
            db[user_id] = "deleted account"
            db.close()
            session['user'] = None
            print('Your account has been deleted.', 'success')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    
@app.route('/manage_accounts')
def manage_accounts():
    if session['user']:
        if str(id_to_object(session['user']).get_admin()) == "1":
            db = shelve.open('Users.db','c')
            users = []
            for key in db:
                value = db[key]
                users.append([key,value])
            db.close()

            if session['user']:
                return render_template('manage_accounts.html',users = users)
            else:
                print('Unauthorised')
                return redirect(url_for('home'))
        else:
            return(redirect(url_for('dashboard')))
    else:
        return redirect(url_for('login'))

@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    if request.method == 'POST':
        db = shelve.open('Users.db', 'c')
        db[str(id)] = "deleted account"
        db.close()
        print('Account has been deleted.', 'success')
        return redirect(url_for('manage_accounts'))
    
@app.route('/updateUser/<int:id>/', methods=['GET', 'POST'])
def update_user(id):
    form = EditProfileForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for('manage_accounts'))
        db = shelve.open('Users.db', 'w')
        user = db.get(str(id))
        if form.name.data:
            user.set_name(form.name.data)
        if form.email.data:
            user.set_email(form.email.data)
        if form.password.data:
            user.set_password(bcrypt.generate_password_hash(form.password.data))
        if form.admin.data:
            user.set_admin(form.admin.data)
        db[str(id)] = user
        db.close()
        return redirect(url_for('manage_accounts'))
    else:
        db = shelve.open('Users.db', 'w')
        user = db.get(str(id))
        form.name.data = user.get_name()
        form.email.data = user.get_email()
        form.admin.data = user.get_admin()
        db.close()
        return render_template('edit_accounts.html',form=form)

@app.route('/logout')
def logout():
    if session['user']:
        session['user'] = None
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

#ZhiNing's codes
@app.route('/completedST')
def completedST():
    ticket_number = request.args.get('ticket_number', 'Not available')
    return render_template('completedST.html', ticket_number=ticket_number)

@app.route('/createSupportTicket', methods=['GET', 'POST'])
def createSupportTicket():
    create_SupportTicket_form = createSupportTicketform(request.form)
    if request.method == 'POST' and create_SupportTicket_form.validate():
        support_ticket_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            support_ticket_dict = db['support_ticket']
        except:
            print("Error in retrieving support tickets from storage.db.")

        support_ticket = SupportTicket.SupportTicket(create_SupportTicket_form.first_name.data, create_SupportTicket_form.last_name.data, create_SupportTicket_form.email.data, create_SupportTicket_form.subject.data, create_SupportTicket_form.message.data)
        ticket_number = support_ticket.get_support_id()
        support_ticket_dict[ticket_number] = support_ticket
        db['support_ticket'] = support_ticket_dict

        db.close()
        return redirect(url_for('completedST', ticket_number = ticket_number))
    return render_template('createSupportTicket.html', form=create_SupportTicket_form)

@app.route('/viewpastST', methods=['GET', 'POST'])
def viewpastST():
    if request.method == 'POST':  
        ticket_number = request.form.get('ticket_number')
        if ticket_number:
            db = shelve.open('storage.db', 'r')
            support_ticket_dict = db.get('support_ticket', {})
            db.close()
            
            if ticket_number in support_ticket_dict:
                return redirect(url_for('ST_details', ticket_number=ticket_number))
            else:
                return render_template('viewpastST.html', error="Support ticket does not exist.")
    return render_template('viewpastST.html')


@app.route('/support_ticket_details/<ticket_number>')
def ST_details(ticket_number):
    db = shelve.open('storage.db', 'r')
    support_ticket_dict = db.get('support_ticket', {})
    db.close()
    
    support_ticket = support_ticket_dict.get(ticket_number)
    if not support_ticket:
        return redirect(url_for('viewpastST', error="Support ticket does not exist."))

    return render_template('support_ticket_details.html', support_ticket=support_ticket)


@app.route('/update_ST/<stn>/', methods=['GET', 'POST'])
def update_ST(stn):
    update_support_ticket_form = createSupportTicketform(request.form)
    if request.method == 'POST' and update_support_ticket_form.validate():
        db = shelve.open('storage.db', 'w')
        support_ticket_dict = db.get('support_ticket', {})

        ST = support_ticket_dict.get(stn)
        if ST:
            ST.set_first_name(update_support_ticket_form.first_name.data)
            ST.set_last_name(update_support_ticket_form.last_name.data)
            ST.set_email(update_support_ticket_form.email.data)
            ST.set_subject(update_support_ticket_form.subject.data)
            ST.set_message(update_support_ticket_form.message.data)

            db['support_ticket'] = support_ticket_dict
        db.close()

        return redirect(url_for('ST_details', ticket_number=stn))
    else:
        db = shelve.open('storage.db', 'r')
        support_ticket_dict = db.get('support_ticket', {})
        db.close()

        ST = support_ticket_dict.get(stn)
        if ST:
            update_support_ticket_form.first_name.data = ST.get_first_name()
            update_support_ticket_form.last_name.data = ST.get_last_name()
            update_support_ticket_form.email.data = ST.get_email()
            update_support_ticket_form.subject.data = ST.get_subject()
            update_support_ticket_form.message.data = ST.get_message()

        return render_template('updateST.html', form=update_support_ticket_form, support_id=stn)


@app.route('/archive_ST/<id>', methods=['POST'])
def archive_ST(id):
    support_ticket_dict = {}
    db1 = shelve.open('storage.db', 'w')
    support_ticket_dict = db1.get('support_ticket', {})
    
    archived_ticket_dict = {}
    db2 = shelve.open('archives.db', 'c')
    archived_ticket_dict = db2.get('archive', {})
    
    support_ticket_record = support_ticket_dict.get(id)
    if support_ticket_record:
        support_ticket_record.set_status('Archived')
        archived_ticket_dict[id] = support_ticket_record
        db2['archive'] = archived_ticket_dict
        support_ticket_dict.pop(id)
        db1['support_ticket'] = support_ticket_dict

    db2.close()
    db1.close()
    return redirect(url_for('home'))

@app.route('/batch_archive_ST', methods=['POST'])
def batch_archive_ST():
    ticket_ids = request.form.getlist('ticket_ids')
    
    support_ticket_dict = {}
    db1 = shelve.open('storage.db', 'w')
    support_ticket_dict = db1.get('support_ticket', {})
    
    archived_ticket_dict = {}
    db2 = shelve.open('archives.db', 'c')
    archived_ticket_dict = db2.get('archive', {})
    
    for ticket_id in ticket_ids:
        support_ticket_record = support_ticket_dict.get(ticket_id)
        if support_ticket_record:
            support_ticket_record.set_status('Archived')
            archived_ticket_dict[ticket_id] = support_ticket_record
            support_ticket_dict.pop(ticket_id)
    
    db2['archive'] = archived_ticket_dict
    db1['support_ticket'] = support_ticket_dict
    
    db2.close()
    db1.close()
    
    return redirect(url_for('S_retrieveST', tab='SR'))


@app.route('/unarchive_ST/<id>', methods=['POST'])
def unarchive_ST(id):
    archived_ticket_dict = {}
    db1 = shelve.open('archives.db', 'w')
    archived_ticket_dict = db1.get('archive', {})
    
    db2 = shelve.open('storage.db', 'c')
    support_ticket_dict = db2.get('support_ticket', {})
    
    archived_ticket_record = archived_ticket_dict.get(id)
    if archived_ticket_record:
        archived_ticket_record.set_status('Completed')
        support_ticket_dict[id] = archived_ticket_record
        db2['support_ticket'] = support_ticket_dict
        archived_ticket_dict.pop(id)
        db1['archive'] = archived_ticket_dict

    db2.close()
    db1.close()
    return redirect(url_for('S_retrieveST', tab='SR'))

@app.route('/S_retrieveST')
def S_retrieveST():
    current_tab = request.args.get('tab', 'SR')
    status_filter = request.args.get('status', '')

    support_ticket_dict = {}
    archived_ticket_dict = {}

    db1 = shelve.open('storage.db', 'c')
    support_ticket_dict = db1.get('support_ticket', {})

    db2 = shelve.open('archives.db', 'c')
    archived_ticket_dict = db2.get('archive', {})

    db1.close()
    db2.close()
    
    support_ticket_list = []
    archived_ticket_list = []
    support_ticket_count = 0
    archived_ticket_count = 0

    if current_tab == 'SR':
        for key in support_ticket_dict:
            support_ticket = support_ticket_dict.get(key)
            if not status_filter or support_ticket.get_status() == status_filter:
                support_ticket_list.append(support_ticket)
        support_ticket_count = len(support_ticket_list)
    else:
        for key in archived_ticket_dict:
            archived_ticket = archived_ticket_dict.get(key)
            archived_ticket_list.append(archived_ticket)
        archived_ticket_count = len(archived_ticket_list)

    return render_template('S_retrieveST.html', support_ticket_count=support_ticket_count, archived_ticket_count=archived_ticket_count, support_ticket_list=support_ticket_list, archived_ticket_list=archived_ticket_list, current_tab=current_tab)

@app.route('/STReply/<ticket_number>', methods=['GET', 'POST'])
def STReply(ticket_number):
    db = shelve.open('storage.db', 'r')
    support_ticket_dict = db.get('support_ticket', {})
    db.close()

    support_ticket = support_ticket_dict.get(ticket_number)
    if not support_ticket:
        return redirect(url_for('viewpastST', error="Support ticket does not exist."))

    receiver_email = support_ticket.get_email()
    sender_email = "sparkleminds.webapp@gmail.com"

    reply_form = replySupportTicketform(request.form)
    if request.method == 'POST' and reply_form.validate():
        replies_dict = {}
        replies_db = shelve.open('replies.db', 'c')

        try:
            replies_dict = replies_db['replies']
        except:
            print("Error in retrieving replies from replies.db.")

        reply_data = {
            'receiver_email': reply_form.receiver_email.data,
            'sender_email': reply_form.sender_email.data,
            'reply_subject': reply_form.reply_subject.data,
            'reply_message': reply_form.reply_message.data
        }

        replies_dict[ticket_number] = reply_data
        replies_db['replies'] = replies_dict
        replies_db.close()
        

        db1 = shelve.open('storage.db', 'w')
        support_ticket_dict = db1.get('support_ticket', {})
        if ticket_number in support_ticket_dict:
            support_ticket = support_ticket_dict[ticket_number]
            support_ticket.set_status('Completed')
            db1['support_ticket'] = support_ticket_dict
        db1.close()

        text = f"Subject: {reply_form.reply_subject.data}\n\n{reply_form.reply_message.data}"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, 'mulfvtdreaqlwaox')
        server.sendmail(sender_email, receiver_email, text)

        return redirect(url_for('ST_details', ticket_number=ticket_number))
    
    reply_form.receiver_email.data = receiver_email
    reply_form.sender_email.data = sender_email

    return render_template('STReply.html', form=reply_form, ticket_number=ticket_number)

@app.route('/view_reply/<ticket_number>')
def view_reply(ticket_number):
    db = shelve.open('replies.db', 'c')
    replies_dict = db.get('replies', {})
    db.close()

    reply_data = replies_dict.get(ticket_number)
    if reply_data:
        return render_template('view_reply.html', reply=reply_data)
    else:
        return render_template('view_reply.html', error="Reply has yet to be made.")

@app.route('/archived_ticket_details/<ticket_number>')
def archived_ticket_details(ticket_number):
    db_archived = shelve.open('archives.db', 'r')
    archived_ticket_dict = db_archived.get('archive', {})
    db_archived.close()

    db_reply = shelve.open('replies.db', 'r')
    reply_dict = db_reply.get('replies', {})
    db_reply.close()

    archived_ticket = archived_ticket_dict.get(ticket_number)
    reply = reply_dict.get(ticket_number)
    
    if not archived_ticket:
        return redirect(url_for('S_retrieveST', tab='AR', error="Archived support ticket does not exist."))

    return render_template('archived_ticket_details.html', archived_ticket=archived_ticket, reply=reply)

# Ethan 6
@app.route("/database", methods=['GET'])
def database():
    tx_db = shelve.open('tx.db', 'r')
    tx_dict = tx_db['Tx']

    # tx_db = shelve.open('tx.db', 'r')
    # tx_dict = tx_db['Tx']
    # user_id = session['user']
    # transactions = []
    # for tx_id in tx_dict:
    #     if tx_dict[tx_id].get_user_id() == int(user_id):
    #         transactions.append(tx_dict[tx_id])

    print("Hello")
    return render_template("database.html",tx_dict=tx_dict)

#Ethan 1

if __name__ == '__main__':
    product_dict = {
        1: {
            "name": "Product Name 1",
            "url": "/product/1",
            "price": 75,
            "src": "../static/pic.jpg"
        },
        2: {
            "name": "Service Name 1",
            "url":"/product/2",
            "price": 80,
            "src": "../static/pic2.jpg"},
        3: {
            "name": "Product Name 2",
            "url": "/product/3",
            "price": 65,
            "src": "../static/pic.jpg"
        },
        4: {
            "name": "Service Name 2",
            "url": "/product/4",
            "price": 50,
            "src": "../static/pic2.jpg"
        },
        5: {
            "name": "Product Name 3",
            "url": "/product/5",
            "price": 100,
            "src": "../static/pic.jpg"
        },
        6: {
            "name": "Service Name 3",
            "url": "/product/6",
            "price": 35,
            "src": "../static/pic2.jpg"
        }
    }

    db = shelve.open('storage.db.buyer', 'c')
    db['Products'] = product_dict
    db.close()

    tx_dict = {}
    db = shelve.open('tx.db','c')
    db['Tx'] = tx_dict
    db.close()

    #Create admin account
    db = shelve.open('Users.db')
    db.clear()
    new_user = User('Admin', 'admin@gmail.com', bcrypt.generate_password_hash('123123'), admin = 1)
    db[str(new_user.get_id())] = new_user
    db.close()
    
    app.run('localhost', port=5001)

