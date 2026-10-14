import os
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_super_segura_para_desarrollo")
app.permanent_session_lifetime = timedelta(minutes=30)

# Configuración de subida de archivos
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ==========================================
# ⚙️ CREDENCIALES DE ACCESO DIRECTAS
# ==========================================
CONFIGURED_EMAIL = "scattarregiatiziano@gmail.com"
CONFIGURED_PASSWORD = "Scattarregia@@'1"
CONFIGURED_SECRET_WORD = "Lucario@A'1"

# Sistema de Rate Limiting en memoria
login_attempts = {}

def rate_limit_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        import time
        current_time = time.time()
        
        if ip not in login_attempts:
            login_attempts[ip] = []
        
        login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < 60]
        
        if len(login_attempts[ip]) >= 5:
            return render_template('admin.html', error="Demasiados intentos fallidos. Bloqueado temporalmente por 1 minuto.", locked=True), 429
            
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_panel'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- RUTAS PÚBLICAS ---
@app.route('/')
def index():
    return render_template('index.html', active_page='index')

@app.route('/proyectos')
def proyectos():
    return render_template('proyectos.html', active_page='proyectos')

@app.route('/videos')
def videos():
    return render_template('videos.html', active_page='videos')

@app.route('/contacto')
def contacto():
    formspree_url = os.environ.get("FORMSPREE_URL", "https://formspree.io/f/tu_endpoint_aqui")
    return render_template('contacto.html', active_page='contacto', formspree_url=formspree_url)

@app.route('/experiencia')
def experiencia():
    return render_template('experiencia.html', active_page='experiencia')

# --- ÁREA PRIVADA / ADMIN ---
@app.route('/admin', methods=['GET', 'POST'])
@rate_limit_admin
def admin_panel():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        secret = request.form.get('secret', '').strip()
        
        ip = request.remote_addr
        import time
        login_attempts[ip].append(time.time())
        
        # Validación directa de las 3 credenciales
        email_valid = (email == CONFIGURED_EMAIL)
        password_valid = (password == CONFIGURED_PASSWORD)
        secret_valid = (secret == CONFIGURED_SECRET_WORD)
        
        if email_valid and password_valid and secret_valid:
            session.permanent = True
            session['logged_in'] = True
            if ip in login_attempts:
                del login_attempts[ip]
            return redirect(url_for('admin_panel'))
        else:
            error = "Credenciales incorrectas o acceso no autorizado."
            
    if session.get('logged_in'):
        cv_exists = os.path.exists(os.path.join(UPLOAD_FOLDER, 'cv.pdf'))
        return render_template('admin.html', logged_in=True, cv_exists=cv_exists)
    
    return render_template('admin.html', logged_in=False, error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_panel'))

@app.route('/admin/upload', methods=['POST'])
@login_required
def admin_upload():
    if 'cv_file' not in request.files:
        return redirect(url_for('admin_panel'))
    file = request.files['cv_file']
    if file.filename == '':
        return redirect(url_for('admin_panel'))
    if file and allowed_file(file.filename):
        filename = secure_filename('cv.pdf')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('admin_panel'))

@app.route('/admin/download-cv')
@login_required
def download_cv():
    cv_path = os.path.join(UPLOAD_FOLDER, 'cv.pdf')
    if not os.path.exists(cv_path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, 'cv.pdf', as_attachment=True, download_name='CV_Profesional.pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)