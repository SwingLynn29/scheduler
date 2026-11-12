import io, os, io, uuid, datetime as dt
import psycopg
from psycopg.rows import dict_row
from functools import wraps
from flask import *
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '123456')
app.json.default = lambda o: o.isoformat() if isinstance(o, (dt.date, dt.datetime)) else str(o)

DSN = os.environ.get('DATABASE_URL', 'dbname=scheduler user=postgres password=admin123 host=localhost')
UP = os.path.join(app.root_path, 'uploads')
SCHOOL = os.environ.get('SCHOOL_NAME', 'SMKN 1 KOTA BENGKULU'); TAHUN = os.environ.get('TAHUN_AJARAN', '2026/2027'); SEMESTER = os.environ.get('SEMESTER', 'GANJIL')
CATATAN = ['Jam pelajaran yang bertabrakan harap dicatat dan dilaporkan untuk diubah.', 'Mengubah jadwal atau mengadakan pertukaran jam antara sesama guru harap dilaporkan.', "Sholat Jum'at berjamaah di sekolah. Ekskul sesuai jadwal yang ditentukan."]

# Ditetapkan semula: Map role ke tabel database (Admin tunggal & Guru)
T = {'admin': 'admins', 'guru': 'teachers'}

def q(sql, a=(), one=False):
    with psycopg.connect(DSN, row_factory=dict_row) as c:
        cur = c.execute(sql, a)
        return (cur.fetchone() if one else cur.fetchall()) if cur.description else None

S = """SELECT s.id, s.day, s.period, s.class_id, c.name cls, sb.name subject, t.full_name teacher, r.name room, to_char(p.start_t,'HH24:MI') st, to_char(p.end_t,'HH24:MI') en
FROM schedules s JOIN rooms c ON c.id=s.class_id JOIN subjects sb ON sb.id=s.subject_id JOIN teachers t ON t.id=s.teacher_id JOIN rooms r ON r.id=s.room_id JOIN periods p ON p.period=s.period """

def me():
    return q(f"SELECT * FROM {T[session['role']]} WHERE id=%s", (session['uid'],), True) if 'uid' in session and session.get('role') in T else None

def auth(f):
    @wraps(f)
    def w(*a, **k):
        if not me(): return jsonify(error='Silakan login'), 401
        return f(*a, **k)
    return w

# Hak akses khusus Admin (Untuk menambah/menghapus jadwal)
def admin_only(f):
    @wraps(f)
    @auth
    def w(*a, **k):
        if session.get('role') != 'admin': return jsonify(error='Akses ditolak: Khusus Admin'), 403
        return f(*a, **k)
    return w

def teacher(f):
    @wraps(f)
    @auth
    def w(*a, **k):
        if session.get('role') != 'guru': return jsonify(error='Khusus guru'), 403
        return f(*a, **k)
    return w

def notify(role, uid, msg, kind='info'):
    q("INSERT INTO notifications(role,uid,msg,kind) VALUES(%s,%s,%s,%s)", (role, uid, msg, kind))

def save_png(f):
    if not f or not f.filename: return None
    h = f.read(8); f.seek(0)
    if not f.filename.lower().endswith('.png') or h != b'\x89PNG\r\n\x1a\n': raise ValueError('File harus berformat PNG')
    n = uuid.uuid4().hex + '.png'; f.save(os.path.join(UP, n)); return n

@app.route('/')
def index():
    return redirect('/app' if me() else '/login/guru')

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if role not in T: abort(404)
    if request.method == 'POST':
        u = q(f"SELECT * FROM {T[role]} WHERE username=%s", (request.form['username'].strip(),), True)
        if u and ch(u['password_hash'], request.form['password']):
            session.clear()
            session.update(role=role, uid=u['id'])
            return redirect('/app')
        flash('Username atau password salah')
    return render_template('auth.html', role=role, mode='login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/app')
def main():
    return render_template('app.html') if me() else redirect('/')

@app.route('/uploads/<f>')
@auth
def uploads(f):
    return send_from_directory(UP, f)

@app.route('/api/me', methods=['GET', 'POST'])
@auth
def api_me():
    u = me()
    if request.method == 'POST':
        try: ph = save_png(request.files.get('photo')) or u.get('photo')
        except ValueError as e: return jsonify(error=str(e)), 400
        f = request.form
        if session['role'] == 'admin':
            q("UPDATE admins SET full_name=%s WHERE id=%s", (f['full_name'], u['id']))
        else:
            q("UPDATE teachers SET full_name=%s, email=%s, phone=%s, photo=%s WHERE id=%s", (f['full_name'], f.get('email'), f.get('phone'), ph, u['id']))
        u = me()
    u.pop('password_hash', None)
    u['role'] = session['role']
    if session['role'] == 'guru': u['label'] = str(q("SELECT count(*) n FROM teacher_subjects WHERE teacher_id=%s", (u['id'],), True)['n']) + ' mapel'
    else: u['label'] = 'Administrator'
    return jsonify(u)

@app.route('/api/password', methods=['POST'])
@auth
def api_pw():
    u = me(); d = request.json
    if not ch(u['password_hash'], d['old']) or len(d['new']) < 6: return jsonify(error='Password lama salah / password baru < 6 karakter'), 400
    q(f"UPDATE {T[session['role']]} SET password_hash=%s WHERE id=%s", (gh(d['new']), u['id']))
    return jsonify(ok=1)

@app.route('/api/dashboard')
@auth
def api_dash():
    u = me(); dow = dt.date.today().isoweekday()
    if session['role'] == 'admin':
        tot_teachers = q("SELECT count(*) n FROM teachers", one=True)['n']
        tot_sched = q("SELECT count(*) n FROM schedules", one=True)['n']
        return jsonify(role='admin', teachers_count=tot_teachers, schedules_count=tot_sched)
    
    today = q(S + "WHERE s.teacher_id=%s AND s.day=%s ORDER BY s.period", (u['id'], dow))
    n = q("SELECT count(*) n FROM assignments WHERE teacher_id=%s", (u['id'],), True)['n']
    return jsonify(today=today, tasks=n)

@app.route('/api/schedule')
@auth
def api_sched():
    u = me()
    cid = request.args.get('class_id')
    tid = request.args.get('teacher_id')
    if session['role'] == 'guru' and not cid:
        return jsonify(q(S + "WHERE s.teacher_id=%s ORDER BY s.day,s.period", (u['id'],)))
    if cid:
        return jsonify(q(S + "WHERE s.class_id=%s ORDER BY s.day,s.period", (cid,)))
    if tid:
        return jsonify(q(S + "WHERE s.teacher_id=%s ORDER BY s.day,s.period", (tid,)))
    return jsonify(q(S + "ORDER BY s.day,s.period"))

@app.route('/api/subjects')
@auth
def api_sub():
    return jsonify(q("SELECT s.*, coalesce(string_agg(t.full_name,', ' ORDER BY t.full_name),'-') teachers FROM subjects s LEFT JOIN teacher_subjects ts ON ts.subject_id=s.id LEFT JOIN teachers t ON t.id=ts.teacher_id GROUP BY s.id ORDER BY s.name"))

@app.route('/api/rooms')
@auth
def api_rooms():
    p = q("SELECT period FROM periods WHERE start_t<=localtime AND end_t>localtime", one=True)
    return jsonify(q("""SELECT r.*, c.name used_by, t.full_name used_teacher FROM rooms r LEFT JOIN schedules s ON s.room_id=r.id AND s.day=%s AND s.period=%s
    LEFT JOIN rooms c ON c.id=s.class_id LEFT JOIN teachers t ON t.id=s.teacher_id ORDER BY r.id""", (dt.date.today().isoweekday(), p['period'] if p else 0)))

@app.route('/api/classes')
@auth
def api_classes():
    return jsonify(q("SELECT * FROM rooms WHERE category='Kelas Reguler' ORDER BY id"))

@app.route('/api/teachers')
@auth
def api_teachers():
    return jsonify(q("SELECT id, full_name, subject_id FROM teachers ORDER BY full_name"))

@app.route('/api/periods')
@auth
def api_periods():
    return jsonify(q("SELECT period, to_char(start_t,'HH24:MI') st, to_char(end_t,'HH24:MI') en FROM periods ORDER BY period"))

@app.route('/api/teachers/<int:i>/subjects')
@auth
def api_teacher_subjects(i):
    return jsonify(q("SELECT s.id, s.name FROM teacher_subjects ts JOIN subjects s ON s.id=ts.subject_id WHERE ts.teacher_id=%s ORDER BY s.name", (i,)))

# PEMBUAT JADWAL: khusus Admin. Guru hanya melihat jadwal.
@app.route('/api/builder', methods=['POST'])
@admin_only
def api_build():
    d = request.json
    try: day, per, tid, sid, cid = int(d['day']), int(d['period']), int(d['teacher_id']), int(d['subject_id']), int(d['class_id']); rid = int(d.get('room_id') or cid)
    except Exception: return jsonify(error='Data jadwal belum lengkap'), 400
    if not q("SELECT 1 FROM teacher_subjects WHERE teacher_id=%s AND subject_id=%s", (tid, sid), True):
        return jsonify(error='Guru tersebut tidak mengampu mata pelajaran yang dipilih'), 400
    a = (day, per)
    rows = q("""SELECT 'Guru' k, c.name x FROM schedules s JOIN rooms c ON c.id=s.class_id WHERE day=%s AND period=%s AND teacher_id=%s
    UNION ALL SELECT 'Ruangan', c.name FROM schedules s JOIN rooms c ON c.id=s.class_id WHERE day=%s AND period=%s AND room_id=%s
    UNION ALL SELECT 'Kelas', t.full_name FROM schedules s JOIN teachers t ON t.id=s.teacher_id WHERE day=%s AND period=%s AND class_id=%s""", a + (tid,) + a + (rid,) + a + (cid,))
    if rows:
        r = q("SELECT name FROM rooms WHERE id=%s", (rid,), True)['name']; k = rows[0]['k']
        return jsonify(error=f"Bentrok {k}: {r if k == 'Ruangan' else 'jadwal'} sudah terpakai oleh {rows[0]['x']} di Jam ke-{per} hari {['', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'][day]}"), 409
    q("INSERT INTO schedules(day,period,class_id,subject_id,teacher_id,room_id) VALUES(%s,%s,%s,%s,%s,%s)", (day, per, cid, sid, tid, rid))
    c = q("SELECT name FROM rooms WHERE id=%s", (cid,), True)['name']
    notify('guru', tid, f"Jadwal baru: {c}, {['', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'][day]} Jam ke-{per}")
    return jsonify(ok=1)

@app.route('/api/schedule/<int:i>', methods=['DELETE'])
@admin_only
def api_sdel(i):
    r = q("DELETE FROM schedules WHERE id=%s RETURNING teacher_id, day, period", (i,), True)
    if r: notify('guru', r['teacher_id'], f"Jadwal dibatalkan: {['', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'][r['day']]} Jam ke-{r['period']}")
    return jsonify(ok=1)

@app.route('/api/assignments', methods=['GET', 'POST'])
@auth
def api_as():
    # Pastikan tabel tugas tersedia pada instalasi lama maupun baru.
    q("""CREATE TABLE IF NOT EXISTS assignments (
        id SERIAL PRIMARY KEY, teacher_id INT NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
        subject_id INT REFERENCES subjects(id), class_id INT NOT NULL REFERENCES rooms(id),
        title TEXT NOT NULL, description TEXT, due_at TIMESTAMP NOT NULL,
        is_inval BOOLEAN NOT NULL DEFAULT FALSE, created TIMESTAMP NOT NULL DEFAULT now()
    )""")
    u = me()
    if request.method == 'POST':
        if session['role'] != 'guru': return jsonify(error='Khusus guru'), 403
        d = request.json or {}
        if not (d.get('title') or '').strip() or not d.get('class_id') or not d.get('due_at'): return jsonify(error='Judul, kelas, dan batas waktu wajib diisi'), 400
        sid = d.get('subject_id') or None
        if sid and not q("SELECT 1 FROM teacher_subjects WHERE teacher_id=%s AND subject_id=%s", (u['id'], sid), True): return jsonify(error='Mapel tidak sesuai dengan mapel yang diampu'), 400
        q("INSERT INTO assignments(teacher_id,subject_id,class_id,title,description,due_at,is_inval) VALUES(%s,%s,%s,%s,%s,%s,%s)", (u['id'], sid, d['class_id'], d['title'].strip(), d.get('description'), d['due_at'], d.get('inval', False)))
        for ad in q("SELECT id FROM admins"): notify('admin', ad['id'], f"Tugas baru dari {u['full_name']}: {d['title'].strip()}")
        return jsonify(ok=1)
    base = "SELECT a.*, c.name cls, t.full_name guru, sb.name mapel FROM assignments a JOIN rooms c ON c.id=a.class_id JOIN teachers t ON t.id=a.teacher_id LEFT JOIN subjects sb ON sb.id=a.subject_id "
    if session['role'] == 'admin': return jsonify(q(base + "ORDER BY a.due_at DESC"))
    return jsonify(q(base + "WHERE a.teacher_id=%s ORDER BY a.due_at DESC", (u['id'],)))

@app.route('/api/assignments/<int:i>', methods=['DELETE'])
@auth
def api_adel(i):
    if session['role'] == 'admin': q("DELETE FROM assignments WHERE id=%s", (i,))
    else: q("DELETE FROM assignments WHERE id=%s AND teacher_id=%s", (i, session['uid']))
    return jsonify(ok=1)

@app.route('/api/leaves', methods=['GET', 'POST'])
@auth
def api_leaves():
    # Migrasi ringan untuk database lama yang belum memiliki kolom status.
    q("ALTER TABLE leaves ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'Menunggu'")
    u = me(); r = session['role']
    if request.method == 'POST':
        f = request.form
        try: pf = save_png(request.files.get('proof'))
        except ValueError as e: return jsonify(error=str(e)), 400
        q("INSERT INTO leaves(role,uid,kind,date,p_from,p_to,note,proof) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (r, u['id'], f['kind'], f['date'], f.get('p_from') or None, f.get('p_to') or None, f.get('note'), pf))
        for ad in q("SELECT id FROM admins"): notify('admin', ad['id'], f"{u['full_name']} ({f['kind']}) pada {f['date']}")
        return jsonify(ok=1)
    if r == 'admin':
        return jsonify(q("SELECT l.*, t.full_name who FROM leaves l JOIN teachers t ON l.role='guru' AND t.id=l.uid ORDER BY l.created DESC LIMIT 50"))
    return jsonify(q("SELECT l.*,'Saya' who FROM leaves l WHERE role='guru' AND uid=%s ORDER BY created DESC", (u['id'],)))

# Admin menyetujui / menolak pengajuan izin atau sakit guru
@app.route('/api/leaves/<int:i>/decision', methods=['POST'])
@admin_only
def api_leave_decision(i):
    st = (request.json or {}).get('status')
    if st not in ('Disetujui', 'Ditolak'): return jsonify(error='Status tidak valid'), 400
    q("ALTER TABLE leaves ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'Menunggu'")
    r = q("UPDATE leaves SET status=%s WHERE id=%s AND role='guru' AND COALESCE(status,'Menunggu')='Menunggu' RETURNING uid, kind, date", (st, i), True)
    if not r: return jsonify(error='Pengajuan tidak ditemukan atau sudah diproses'), 404
    notify('guru', r['uid'], f"Pengajuan {r['kind']} tanggal {str(r['date'])[:10]} {st.lower()}")
    return jsonify(ok=1)

# Cetak seluruh jadwal sekolah dalam format PDF (satu halaman per kelas).
@app.route('/api/export-pdf')
@auth
def api_export_pdf():
    import exportpdf
    classes = q("SELECT id, name FROM rooms WHERE category='Kelas Reguler' ORDER BY name")
    periods = q("SELECT period, to_char(start_t,'HH24:MI') st, to_char(end_t,'HH24:MI') en FROM periods ORDER BY period")
    rows = q("""SELECT s.class_id, s.day, s.period, sb.name subject, t.full_name teacher, r.name room
               FROM schedules s JOIN subjects sb ON sb.id=s.subject_id
               JOIN teachers t ON t.id=s.teacher_id JOIN rooms r ON r.id=s.room_id
               ORDER BY s.class_id, s.day, s.period""")
    f = exportpdf.build(classes, rows, periods, SCHOOL, TAHUN, SEMESTER)
    return send_file(f, mimetype='application/pdf', as_attachment=True, download_name='jadwal-pelajaran-seluruh-sekolah.pdf')

@app.route('/api/notifications', methods=['GET', 'POST'])
@auth
def api_notif():
    if request.method == 'POST':
        q("UPDATE notifications SET read=TRUE WHERE role=%s AND uid=%s", (session['role'], session['uid']))
        return jsonify(ok=1)
    return jsonify(q("SELECT * FROM notifications WHERE role=%s AND uid=%s ORDER BY created DESC LIMIT 30", (session['role'], session['uid'])))

@app.route('/api/search')
@auth
def api_search():
    s = request.args.get('q', '').strip()
    if len(s) < 2: return jsonify([])
    l = f'%{s}%'; u = me(); o = []
    if session['role'] == 'guru':
        o += [{'t': 'Jadwal', 'a': f"{x['cls']} - {x['subject']}", 'b': f"Hari {x['day']} Jam {x['period']} | {x['room']}"} for x in q(S + "WHERE s.teacher_id=%s AND (c.name ILIKE %s OR r.name ILIKE %s OR sb.name ILIKE %s) LIMIT 6", (u['id'], l, l, l))]
    if session['role'] == 'admin':
        o += [{'t': 'Jadwal', 'a': f"{x['cls']} - {x['subject']}", 'b': f"{x['teacher']} | Hari {x['day']} Jam {x['period']} | {x['room']}"} for x in q(S + "WHERE t.full_name ILIKE %s OR c.name ILIKE %s OR sb.name ILIKE %s LIMIT 8", (l, l, l))]
    o += [{'t': 'Ruangan', 'a': x['name'], 'b': x['category']} for x in q("SELECT name,category FROM rooms WHERE name ILIKE %s LIMIT 5", (l,))]
    o += [{'t': 'Mapel', 'a': x['name'], 'b': x['teachers']} for x in q("SELECT s.name,coalesce(string_agg(t.full_name,', '),'-') teachers FROM subjects s LEFT JOIN teacher_subjects ts ON ts.subject_id=s.id LEFT JOIN teachers t ON t.id=ts.teacher_id WHERE s.name ILIKE %s OR t.full_name ILIKE %s GROUP BY s.id LIMIT 5", (l, l))]
    return jsonify(o)

import extra
extra.init(app, q, auth, teacher, me, notify, S)

if __name__ == '__main__':
    os.makedirs(UP, exist_ok=True)
    app.run(debug=True)