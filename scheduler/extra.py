import json, datetime as dt
import psycopg
from flask import request, jsonify, session

def init(app, q, auth, teacher, me, notify, S):
    vf = app.view_functions
    def route(url, ep, methods, dec=auth):
        def d(f): app.add_url_rule(url, ep, dec(f), methods=methods); return f
        return d
    code = lambda r: r[1] if isinstance(r, tuple) else r.status_code
    js = lambda r: (r[0] if isinstance(r, tuple) else r).get_json()

    # Ditetapkan semula: Fitur Booking Ruangan oleh Guru
    @route('/api/bookings', 'api_bk', ['GET', 'POST'], teacher)
    def bk():
        u = me()
        if request.method == 'GET':
            return jsonify(q("SELECT b.id,b.date,b.period,b.purpose,r.name room FROM bookings b JOIN rooms r ON r.id=b.room_id WHERE teacher_id=%s AND date>=CURRENT_DATE ORDER BY date,period", (u['id'],)))
        d = request.json
        try: day = dt.date.fromisoformat(d['date'])
        except Exception: return jsonify(error='Tanggal tidak valid'), 400
        if day < dt.date.today() or day.isoweekday() > 5: return jsonify(error='Pilih hari kerja mulai hari ini'), 400
        if q("SELECT 1 FROM schedules WHERE room_id=%s AND day=%s AND period=%s", (d['room_id'], day.isoweekday(), d['period']), True): return jsonify(error='Ruangan terpakai jadwal rutin pada jam itu'), 409
        try: q("INSERT INTO bookings(room_id,teacher_id,date,period,purpose) VALUES(%s,%s,%s,%s,%s)", (d['room_id'], u['id'], day, d['period'], d.get('purpose')))
        except psycopg.errors.UniqueViolation: return jsonify(error='Ruangan sudah dibooking pada jam itu'), 409
        return jsonify(ok=1)

    @route('/api/bookings/<int:i>', 'api_bkd', ['DELETE'], teacher)
    def bkd(i):
        q("DELETE FROM bookings WHERE id=%s AND teacher_id=%s", (i, session['uid']))
        return jsonify(ok=1)

    # Resolusi bentrok oleh Admin
    @route('/api/resolve', 'api_res', ['GET'])
    def res():
        a = request.args; day, per, cid, rid = a['day'], a['period'], a['class_id'], a['room_id']
        return jsonify(
            rooms=q("SELECT id,name FROM rooms WHERE id NOT IN(SELECT room_id FROM schedules WHERE day=%s AND period=%s) AND (category<>'Kelas Reguler' OR id=%s) ORDER BY id", (day, per, cid)),
            periods=q("SELECT period FROM periods p WHERE NOT EXISTS(SELECT 1 FROM schedules s WHERE s.day=%s AND s.period=p.period AND (s.teacher_id=%s OR s.class_id=%s OR s.room_id=%s)) ORDER BY period", (day, a.get('teacher_id', 0), cid, rid))
        )

    # Ditetapkan semula: Daftar Guru per Mata Pelajaran
    @route('/api/subjects/<int:i>/teachers', 'api_stc', ['GET'])
    def stc(i):
        return jsonify(q("SELECT t.full_name, coalesce(string_agg(DISTINCT c.name,', ' ORDER BY c.name),'') classes FROM teachers t JOIN teacher_subjects ts ON ts.teacher_id=t.id AND ts.subject_id=%s LEFT JOIN schedules s ON s.teacher_id=t.id AND s.subject_id=ts.subject_id LEFT JOIN rooms c ON c.id=s.class_id GROUP BY t.id ORDER BY t.full_name", (i,)))