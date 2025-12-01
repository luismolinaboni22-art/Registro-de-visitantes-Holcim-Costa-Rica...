from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150))
    person_to_visit = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.String(250))
    check_in = db.Column(db.DateTime, default=datetime.now)
    check_out = db.Column(db.DateTime)

# Decorador para admin
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated and current_user.email == "jorgemolinabonilla@gmail.com":
            return f(*args, **kwargs)
        flash("No tienes permisos para acceder a esta página")
        return redirect(url_for('register_visitor'))
    return wrap

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('register_visitor'))
        flash("Usuario o contraseña incorrectos")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
@login_required
def register_visitor():
    if request.method == 'POST':
        ci = request.form['ci']
        name = request.form['name']
        company = request.form.get('company')
        person_to_visit = request.form['person_to_visit']
        reason = request.form.get('reason')
        visitor = Visitor(ci=ci, name=name, company=company,
                          person_to_visit=person_to_visit, reason=reason)
        db.session.add(visitor)
        db.session.commit()
        flash('Visitante registrado')
        return redirect(url_for('list_visitors'))
    return render_template('register.html')

@app.route('/list')
@login_required
def list_visitors():
    visitors = Visitor.query.order_by(Visitor.id.desc()).all()
    inside_count = Visitor.query.filter_by(check_out=None).count()
    return render_template('list.html', visitors=visitors, inside_count=inside_count)

@app.route('/checkout/<int:visitor_id>')
@login_required
def checkout(visitor_id):
    visitor = Visitor.query.get(visitor_id)
    if visitor and not visitor.check_out:
        visitor.check_out = datetime.now()
        db.session.commit()
        flash(f'Salida registrada para {visitor.name}')
    return redirect(url_for('list_visitors'))

@app.route('/history')
@login_required
def history():
    visitors = Visitor.query.order_by(Visitor.id.desc()).all()
    return render_template('history.html', visitors=visitors)

@app.route('/reports', methods=['GET'])
@login_required
def reports():
    query = Visitor.query
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    nombre = request.args.get('nombre')
    empresa = request.args.get('empresa')

    if fecha_inicio:
        query = query.filter(Visitor.check_in >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Visitor.check_in <= fecha_fin)
    if nombre:
        query = query.filter(Visitor.name.ilike(f"%{nombre}%"))
    if empresa:
        query = query.filter(Visitor.company.ilike(f"%{empresa}%"))

    visitors = query.order_by(Visitor.check_in.desc()).all()
    total_visitors = Visitor.query.count()
    inside_count = Visitor.query.filter_by(check_out=None).count()
    exited_count = Visitor.query.filter(Visitor.check_out.isnot(None)).count()

    return render_template(
        'reports.html',
        visitors=visitors,
        total_visitors=total_visitors,
        inside_count=inside_count,
        exited_count=exited_count,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        nombre=nombre,
        empresa=empresa
    )

# Ruta para crear usuarios (solo admin)
@app.route('/create_user', methods=['GET','POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Usuario ya existe")
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Usuario creado correctamente")
        return redirect(url_for('create_user'))
    return render_template('create_user.html')

# Crear base de datos y admin inicial
@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(email="jorgemolinabonilla@gmail.com").first():
        admin = User(email="jorgemolinabonilla@gmail.com", password="123")
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)


