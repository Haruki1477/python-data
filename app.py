from flask import Flask, render_template, request, redirect
from models import db, User

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')
    return render_template('register.html')

@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)
