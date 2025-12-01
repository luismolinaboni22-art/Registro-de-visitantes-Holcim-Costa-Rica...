from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'esta_es_una_clave_secreta'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ===================== MODELOS =====================

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150))
    reason = db.Column(db.String(300))
    check_in = db.Column(db.DateTime, default=datetime.now)
    check_out = db.Column(db.DateTime, nullable=True)  # Salida

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

# Crear tablas y usuario admin automáticamente
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        hashed_pw = generate_password_hash("123", method="sha256")
        new_user = User(username="admin", password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===================== RUTAS LOGIN =====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('list_visitors'))
        else:
            flash("Usuario o contraseña incorrectos")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ===================== RUTAS PRINCIPALES =====================

@app.route('/')
def index():
    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        company = request.form['company']
        reason = request.form['reason']

        new_visitor = Visitor(name=name, company=company, reason=reason)
        db.session.add(new_visitor)
        db.session.commit()
        return redirect('/list')

    return render_template('register.html')

@app.route('/list')
@login_required
def list_visitors():
    visitors = Visitor.query.order_by(Visitor.id.desc()).all()
    inside_count = Visitor.query.filter_by(check_out=None).count()
    return render_template('list.html', visitors=visitors, inside_count=inside_count)

# ===================== RUTA DAR SALIDA =====================

@app.route('/checkout/<int:visitor_id>')
@login_required
def checkout(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)
    if visitor.check_out is None:
        visitor.check_out = datetime.now()
        db.session.commit()
    return redirect('/list')

# ===================== RUTA HISTÓRICO =====================

@app.route('/history')
@login_required
def history():
    visitors = Visitor.query.order_by(Visitor.check_in.desc()).all()
    return render_template('history.html', visitors=visitors)

# ===================== RUN =====================

if __name__ == '__main__':
    app.run(debug=True)
