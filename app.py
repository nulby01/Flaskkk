from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Folder untuk menyimpan file upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOADS = []  # List untuk menyimpan data upload

@app.route('/')
def home():
    return redirect(url_for('data_diri'))

@app.route('/data_diri', methods=['GET', 'POST'])
def data_diri():
    if request.method == 'POST':
        nama = request.form['nama']
        usia = request.form['usia']
        asal = request.form['hobi']
        if nama and usia and asal:
            flash('Data berhasil disimpan!', 'success')
            return redirect(url_for('challenges'))
        else:
            flash('Harap isi semua kolom!', 'error')
    return render_template('data_diri.html')

@app.route('/challenges')
def challenges():
    today_date = datetime.now().strftime('%d %B %Y')

    challenge_list = [
        {
            "id": 1,
            "title": "Foto/Video Challenge",
            "description": "Upload foto/video 'Sunset terbaik' atau 'Sunrise terbaikmu'.",
            "details": "Bagikan momen terbaikmu sekarang!"
        },
        {
            "id": 2,
            "title": "Daily Challenge",
            "description": f"Tantangan harian untuk hari ini ({today_date}): Unggah sesuatu yang membuatmu bahagia.",
            "details": "Tantangan berubah setiap hari, jadi jangan lewatkan keseruannya!"
        },
        {
            "id": 3,
            "title": "Today's Lesson Challenge",
            "description": "Pelajaran apa yang kamu dapatkan hari ini.",
            "details": "Apa tantangan terbesarmu hari ini, dan bagaimana kamu menghadapinya?"
        },
    ]
    return render_template('challenges.html', challenges=challenge_list)

@app.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge_detail(challenge_id):
    challenge_list = [
        {
            "id": 1,
            "title": "Foto/Video Challenge",
            "description": "Upload foto/video 'Sunset terbaik' atau 'Sunrise terbaikmu'.",
            "details": "Bagikan momen terbaikmu sekarang!"
        },
        {
            "id": 2,
            "title": "Daily Challenge",
            "description": f"Tantangan harian untuk hari ini ({datetime.now().strftime('%d %B %Y')}): Unggah sesuatu yang membuatmu bahagia.",
            "details": "Tantangan berubah setiap hari, jadi jangan lewatkan keseruannya!"
        },
        {
            "id": 3,
            "title": "Today's Lesson Challenge",
            "description": "Pelajaran apa yang kamu dapatkan hari ini.",
            "details": "Apa tantangan terbesarmu hari ini, dan bagaimana kamu menghadapinya?"
        },
    ]

    challenge = next((c for c in challenge_list if c["id"] == challenge_id), None)
    if not challenge:
        flash("Tantangan tidak ditemukan!", "error")
        return redirect(url_for('challenges'))

    if request.method == 'POST':
        # Ambil file yang diupload
        file = request.files['file']
        response = request.form.get('response', '')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Simpan data upload ke dalam sebuah list
            upload_data = {
                'challenge_title': challenge['title'],
                'response': response,
                'image_url': url_for('static', filename=f'uploads/{filename}')
            }

            UPLOADS.append(upload_data)  # Menyimpan data upload

            flash(f"Tantangan '{challenge['title']}' berhasil diikuti! Foto diunggah ke {file_path}.", 'success')
            return redirect(url_for('challenge_uploads'))
        else:
            flash("Gagal mengunggah file. Pastikan formatnya adalah PNG, JPG, atau JPEG.", 'error')

        return redirect(url_for('challenges'))

    return render_template('challenge_detail.html', challenge=challenge)

# Route untuk melihat hasil upload dengan infinite scroll
@app.route('/uploads')
def challenge_uploads():
    page = int(request.args.get('page', 1))  # Ambil halaman dari query string
    per_page = 5  # Tentukan jumlah upload yang ditampilkan per halaman

    # Mengambil data berdasarkan halaman
    start = (page - 1) * per_page
    end = start + per_page
    uploads_to_show = UPLOADS[start:end]

    if request.is_json:
        # Mengembalikan data dalam bentuk JSON untuk AJAX
        return jsonify({
            'uploads': uploads_to_show
        })
    
    return render_template('uploads.html', uploads=uploads_to_show)

if __name__ == '__main__':
    app.run(debug=True, port=6060)
