from flask import Flask, render_template, request, redirect, url_for, session, flash
from cassandra.cluster import Cluster
from passlib.hash import sha256_crypt
import uuid
import time

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']

cluster = None
session_db = None

# Retry mechanism
while True:
   try:
       cluster = Cluster(['cassandra'], port=9042, connect_timeout=10)
       session_db = cluster.connect()
       break
   except Exception as e:
       print(f"Failed to connect to Cassandra: {e}")
       time.sleep(1)

session_db.set_keyspace('todoapp')

# Create user table if not exists
session_db.execute(
   """
   CREATE TABLE IF NOT EXISTS users (
       id UUID PRIMARY KEY,
       username text,
       password text
   )
   """
)

# Create to-do list table if not exists
session_db.execute(
    """
    CREATE TABLE IF NOT EXISTS todos (
        username text,
        task_id UUID PRIMARY KEY,
        task text
    )
    """
)



# Function to check if the user is loggedin
def is_logged_in():
    return 'username' in session

# Home route
@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('todolist'))
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
       username = request.form['username']
       password_candidate = request.form['password']

       # Fetch user from database
       result = session_db.execute("SELECT id, password FROM users WHERE username = %s ALLOW FILTERING", (username,))
       user_data = result.one()

       if user_data and sha256_crypt.verify(password_candidate, user_data.password):
           session['username'] = username
           flash('You are now logged in', 'success')
           return redirect(url_for('todolist'))
       else:
           flash('Invalid login', 'danger')

   return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
      username = request.form['username']
      password = sha256_crypt.encrypt(request.form['password'])

      # Check if username already exists
      result = session_db.execute("SELECT * FROM users WHERE username = %s ALLOW FILTERING", (username,))
      existing_user = result.one()

      if existing_user:
          flash('Username already exists', 'danger')
          return redirect(url_for('signup'))

      # Generate UUID in Python
      user_id = uuid.uuid4()

      # Insert new user into the database
      session_db.execute("INSERT INTO users (id, username, password) VALUES (%s, %s, %s)", (user_id, username, password))

      flash('You are now registered and can log in', 'success')
      return redirect(url_for('login'))

  return render_template('signup.html')


# To-do list route
@app.route('/todolist')
def todolist():
    if not is_logged_in():
        return redirect(url_for('login'))

    username = session['username']

    # Fetch tasks for the logged-in user
    result = session_db.execute("SELECT * FROM todos WHERE username = %s ALLOW FILTERING", (username,))
    todos = result.all()

    return render_template('todolist.html', todos=todos)

# Add task route
@app.route('/add_task', methods=['POST'])
def add_task():
    if not is_logged_in():
        return redirect(url_for('login'))

    task = request.form['task']
    username = session['username']

    # Insert new task into the database
    task_id = uuid.uuid4()
    session_db.execute("INSERT INTO todos (username, task_id, task) VALUES (%s, %s, %s)", (username, task_id, task))

    flash('Task added', 'success')
    return redirect(url_for('todolist'))

# Delete task route
@app.route('/delete_task/<string:task_id>', methods=['POST'])
def delete_task(task_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    # Delete task from the database
    session_db.execute("DELETE FROM todos WHERE task_id = %s", (uuid.UUID(task_id),))

    flash('Task deleted', 'success')
    return redirect(url_for('todolist'))

if __name__ == '__main__':
    app.run(debug=True)