from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret123'  # Đổi khi deploy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
db = SQLAlchemy(app)

# ===== DATABASE MODELS =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    progress = db.Column(db.String(200), default="")  # Lưu ID task đã hoàn thành

with app.app_context():
    db.create_all()

# ===== ROUTES =====
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('tracker'))
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        flash("Tên tài khoản đã tồn tại!", "danger")
        return redirect(url_for('login'))
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash("Đăng ký thành công, hãy đăng nhập!", "success")
    return redirect(url_for('login'))

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    roadmap = [
        "Cơ bản về Python",
        "Chuỗi, List, Tuple, Set, Dict",
        "Hàm & Tham số",
        "Lập trình hướng đối tượng (OOP)",
        "File I/O + JSON",
        "Xử lý ngoại lệ",
        "Thư viện chuẩn quan trọng",
        "Kỹ thuật nâng cao",
        "Bất đồng bộ & Đa luồng",
        "Quản lý môi trường & Package"
    ]

    completed = set(user.progress.split(',')) if user.progress else set()

    if request.method == 'POST':
        completed = set(request.form.getlist('tasks'))
        user.progress = ','.join(completed)
        db.session.commit()
        flash("Tiến trình đã được lưu!", "success")

    percent = round((len(completed) / len(roadmap)) * 100)
    return render_template('tracker.html', roadmap=roadmap, completed=completed, percent=percent)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
