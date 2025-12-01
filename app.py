from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150))
    reason = db.Column(db.String(300))
    check_in = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

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
def list_visitors():
    visitors = Visitor.query.order_by(Visitor.id.desc()).all()
    return render_template('list.html', visitors=visitors)

if __name__ == '__main__':
    app.run(debug=True)