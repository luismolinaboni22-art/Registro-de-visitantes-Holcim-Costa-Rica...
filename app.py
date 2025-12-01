from flask import Flask, render_template
app = Flask(__name__)

# ⚡ Recarga automática y sin cache
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Datos de ejemplo para tabla y gráfico
visitors = [
    {"name": "Juan", "company": "Holcim", "check_in": "2025-12-01 09:00"},
    {"name": "Ana", "company": "ALG", "check_in": "2025-12-01 09:30"},
    {"name": "Luis", "company": "GAS", "check_in": "2025-12-01 10:00"},
]

@app.route('/reports')
def reports():
    return render_template('reports.html', visitors=visitors)

if __name__ == "__main__":
    app.run(debug=True)
