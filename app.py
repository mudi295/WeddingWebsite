import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Invitation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-wedding'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Konfigurasi Folder Upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ROUTE 1: Landing Page
@app.route('/')
def index():
    return render_template('index.html')

# ROUTE: Register User Baru
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cek apakah username sudah ada di database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username sudah digunakan, pilih yang lain.')
            return redirect(url_for('register'))
            
        # Simpan user baru ke database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Akun berhasil dibuat! Silakan login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal, cek username/password')
    # Sekarang kita panggil file html, bukan teks mentah lagi
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil keluar.')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    inv = Invitation.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Ambil data teks
        l_name = request.form.get('location_name')
        m_url = request.form.get('maps_url')
        g_parents = request.form.get('groom_parents')
        b_parents = request.form.get('bride_parents')
        
        # Dictionary untuk memproses upload foto secara dinamis
        photo_fields = {
            'hero_img_file': 'hero_img',
            'couple_img_file': 'couple_img',
            'groom_img_file': 'groom_img',
            'bride_img_file': 'bride_img'
        }
        
        # Simpan URL lama atau default kosong
        image_urls = {
            'hero_img': inv.hero_img if inv else '',
            'couple_img': inv.couple_img if inv else '',
            'groom_img': inv.groom_img if inv else '',
            'bride_img': inv.bride_img if inv else ''
        }

        # Loop proses upload
        for form_name, db_column in photo_fields.items():
            file = request.files.get(form_name)
            if file and allowed_file(file.filename):
                filename = secure_filename(f"user_{current_user.id}_{db_column}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_urls[db_column] = f"/static/uploads/{filename}"

        if inv:
            # Update data yang sudah ada
            inv.groom_name = request.form.get('groom')
            inv.bride_name = request.form.get('bride')
            inv.groom_parents = g_parents
            inv.bride_parents = b_parents
            inv.wedding_date = request.form.get('wedding_date')
            inv.wedding_time = request.form.get('wedding_time')
            inv.slug = request.form.get('slug')
            inv.location_name = l_name
            inv.maps_url = m_url
            # Update Foto
            inv.hero_img = image_urls['hero_img']
            inv.couple_img = image_urls['couple_img']
            inv.groom_img = image_urls['groom_img']
            inv.bride_img = image_urls['bride_img']
        else:
            # Buat baru
            new_inv = Invitation(
                user_id=current_user.id,
                groom_name=request.form.get('groom'),
                bride_name=request.form.get('bride'),
                groom_parents=g_parents,
                bride_parents=b_parents,
                wedding_date=request.form.get('wedding_date'),
                wedding_time=request.form.get('wedding_time'),
                location_name=l_name,
                maps_url=m_url,
                slug=request.form.get('slug'),
                theme_name=request.form.get('luxury'),
                hero_img=image_urls['hero_img'],
                couple_img=image_urls['couple_img'],
                groom_img=image_urls['groom_img'],
                bride_img=image_urls['bride_img']
            )
            db.session.add(new_inv)
        
        db.session.commit()
        flash('Undangan berhasil diperbarui dengan foto terbaru!')
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', inv=inv)

# Route untuk Preview (Bisa diakses siapa saja)
@app.route('/preview/<theme_id>')
def preview_theme(theme_id):
    # Kita buat data dummy supaya halaman tidak kosong
    dummy_data = {
        'groom_name': 'Romeo',
        'bride_name': 'Juliet',
        'wedding_date': '12 Desember 2026',
        'theme_name': theme_id
    }
    return render_template(f'themes/{theme_id}.html', data=dummy_data)

@app.route('/catalog')
def catalog():
    # Daftar 50 tema bisa ditaruh di list atau database
    # Untuk sementara kita buat list manual dulu
    all_themes = [
    {'id': 'luxury', 'name': 'Luxury Gold', 'tag': 'Elegant', 'img': '...'},
    {'id': 'minimal', 'name': 'Minimalist', 'tag': 'Modern', 'img': '...'},
    {'id': 'nature', 'name': 'Nature Leaf', 'tag': 'Organic', 'img': '...'},
    {'id': 'royal', 'name': 'Royal Blue', 'tag': 'Classic', 'img': '...'},
    {'id': 'vintage', 'name': 'Old School', 'tag': 'Retro', 'img': '...'},
    {'id': 'romantic', 'name': 'Sweet Love', 'tag': 'Soft', 'img': '...'},
    {'id': 'modern-dark', 'name': 'Industrial', 'tag': 'Bold', 'img': '...'},
    {'id': 'boho', 'name': 'Teracotta', 'tag': 'Boho', 'img': '...'},
    {'id': 'traditional', 'name': 'Heritage', 'tag': 'Ethnic', 'img': '...'},
    {'id': 'spring', 'name': 'Morning Dew', 'tag': 'Fresh', 'img': '...'},
]
    return render_template('catalog.html', themes=all_themes)

@app.route('/select-theme/<theme_id>')
@login_required
def select_theme(theme_id):
    inv = Invitation.query.filter_by(user_id=current_user.id).first()
    if not inv:
        inv = Invitation(user_id=current_user.id, slug=f"user-{current_user.id}")
    
    inv.theme_name = theme_id
    db.session.commit()
    flash(f'Tema {theme_id} berhasil dipilih!')
    return redirect(url_for('dashboard'))

# ROUTE 4: Display Undangan (Public)
@app.route('/to/<slug>')
def view_wedding(slug):
    inv = Invitation.query.filter_by(slug=slug).first_or_404()
    # Mengambil template berdasarkan pilihan user
    return render_template(f'themes/{inv.theme_name}.html', data=inv)

with app.app_context():
    db.create_all()
    # Buat akun dummy jika belum ada
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)