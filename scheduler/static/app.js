// ============================================================
// app.js - tampilan Scheduler. Admin = pembuat jadwal. Guru = hanya melihat jadwal.
// ============================================================
const $ = s => document.querySelector(s), D = ['', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'];
const api = async (u, o = {}) => { const r = await fetch(u, o), j = await r.json().catch(() => ({})); if (!r.ok) throw j; return j };
const post = (u, d) => api(u, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const modal = h => { $('#modal').innerHTML = `<div class="box">${h}</div>`; $('#modal').classList.add('on') };
const closeModal = () => $('#modal').classList.remove('on');
const fail = e => alert(e.error || 'Terjadi kesalahan');
const mins = t => +t.slice(0, 2) * 60 + +t.slice(3, 5);
const fmt = d => new Date(d).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' });
const opts = (a, v = 'id', l = 'name') => a.map(x => `<option value="${x[v]}">${esc(x[l])}</option>`).join('');
const theme = t => { document.documentElement.dataset.theme = t; localStorage.theme = t };

let ME, isA, isT, HD, PER = [], timer;
const AFTER = {}, PAGES = {};
// Menu: Tugas hanya untuk guru; menu terakhir = Pembuat Jadwal (admin) / Pengaturan (guru)
const NAV = () => [['home', 'Home', '🏠'], ['report', 'Jadwal Pelajaran', '📅'], ['mapel', 'Mata Pelajaran', '📚'], ['tugas', 'Tugas', '📝'], ['ruang', 'Ruang Kelas', '🏫'], ['help', isA ? 'Pembuat Jadwal' : 'Pengaturan', '⚙️']];

async function init() {
    theme(localStorage.theme || 'light');
    ME = await api('/api/me'); isA = ME.role === 'admin'; isT = ME.role === 'guru';
    $('#hello').textContent = 'Halo, ' + ME.full_name + (isA ? ' (Admin)' : '');
    $('#av').outerHTML = `<div id="av" class="av">${ME.photo ? `<img src="/uploads/${ME.photo}" alt="" onerror="this.remove()">` : ''}${esc((ME.full_name || '?')[0].toUpperCase())}</div>`;
    $('#nav').innerHTML = NAV().map(n => `<a data-p="${n[0]}">${n[2]} ${n[1]}</a>`).join('');
    $('#nav').onclick = e => { const p = e.target.closest('a')?.dataset.p; p && go(p) };
    go('home'); loadNotif(); setInterval(loadNotif, 10000);
}

async function go(p) {
    clearInterval(timer);
    document.querySelectorAll('#nav a').forEach(a => a.classList.toggle('on', a.dataset.p === p));
    const title = NAV().find(n => n[0] === p)[1];
    try { $('#view').innerHTML = `<h1>${title}</h1>` + await PAGES[p](); if (AFTER[p]) AFTER[p]() }
    catch (e) { $('#view').innerHTML = `<h1>${title}</h1><p class="err">Gagal memuat data. Coba muat ulang halaman.</p>` }
}

/* ---------- HOME ---------- */
PAGES.home = async () => {
    HD = await api('/api/dashboard');
    if (isA) {
        const kpi = [['Total Guru', HD.teachers_count], ['Jam Terjadwal', HD.schedules_count], ['Peran', 'Admin']];
        return `<div class="grid g3">${kpi.map(k => `<div class="card kpi"><small class="muted">${k[0]}</small><b>${esc(k[1])}</b></div>`).join('')}</div>
        <div class="card"><h3>Pembuat Jadwal</h3><p class="muted">Admin menyusun jadwal lewat menu "Pembuat Jadwal". Guru hanya dapat melihat jadwalnya.</p></div>`;
    }
    const kpi = [['Kelas Hari Ini', (HD.today || []).length], ['Tugas Dibuat', HD.tasks], ['Mapel Diampu', ME.label]];
    return `<div class="grid g3">${kpi.map(k => `<div class="card kpi"><small class="muted">${k[0]}</small><b>${esc(k[1])}</b></div>`).join('')}</div>
    <div class="grid g2"><div class="card"><h3>Kelas Terdekat</h3><div id="live"></div></div><div class="card"><h3>Lini Masa Hari Ini</h3><div class="tl" id="tl"></div></div></div>`;
};
AFTER.home = () => {
    if (isA) return;
    const tick = () => {
        const n = new Date(), m = n.getHours() * 60 + n.getMinutes() + n.getSeconds() / 60, t = HD.today || [];
        const live = t.find(s => mins(s.st) <= m && m < mins(s.en)), next = t.find(s => mins(s.st) > m), s = live || next;
        $('#live').innerHTML = !s ? '<p class="muted">Tidak ada kelas lagi hari ini.</p>' :
            `<div class="live"><small>${live ? 'Sedang berlangsung' : 'Berikutnya'}</small><h2>${esc(s.subject)}</h2><div>${esc(s.cls)} | ${esc(s.room)} | ${s.st}-${s.en}</div><h3 style="color:var(--champ);margin:8px 0 0">${live ? `Selesai ${Math.ceil(mins(s.en) - m)} menit lagi` : `${esc(s.cls)}, ${Math.ceil(mins(s.st) - m)} Menit Lagi`}</h3></div>`;
        $('#tl').innerHTML = t.map(x => `<div class="${mins(x.en) <= m ? 'done' : ''}"><b>${x.st}</b> ${esc(x.subject)} - ${esc(x.cls)} <small class="muted">(${esc(x.room)})</small></div>`).join('') || '<p class="muted">Tidak ada jadwal hari ini.</p>';
    };
    tick(); timer = setInterval(tick, 15000);
};

/* ---------- JADWAL PELAJARAN (hanya melihat) ---------- */
// r = data jadwal, perList = daftar jam dari database, byClass = tampilan satu kelas (tampilkan nama guru)
const matrix = (r, perList, byClass) => {
    let h = '<div class="wrap"><table><tr><th>Jam</th>' + D.slice(1).map(d => `<th>${d}</th>`).join('') + '</tr>';
    for (const p of perList) {
        h += `<tr><td><b>${p.period}</b><br><small class="muted">${p.st}-${p.en}</small></td>`;
        for (let d = 1; d <= 5; d++) {
            const x = r.find(s => s.day == d && s.period == p.period), own = x && isT && x.teacher === ME.full_name;
            h += `<td><div class="cell ${own ? 'mine' : ''}">${x ? `<b>${esc(x.subject)}</b><br><small>${esc(byClass ? x.teacher : x.cls)} | ${esc(x.room)}</small>` : ''}</div></td>`;
        }
        h += '</tr>';
    }
    return h + '</table></div>';
};
PAGES.report = async () => {
    const [cl, per] = await Promise.all([api('/api/classes'), api('/api/periods')]); PER = per;
    return `<div class="card"><div class="row noprint"><select id="cf">${isT ? '<option value="">Jadwal Mengajar Saya</option>' : ''}${opts(cl)}</select><button class="btn ghost" style="flex:none" onclick="print()">Cetak Tampilan</button><a class="btn" style="flex:none;text-decoration:none" href="/api/export-pdf">Unduh Jadwal Keseluruhan (PDF)</a></div><p class="muted noprint">${isT ? '' : ''}</p><div id="mx"></div></div>`;
};
AFTER.report = () => {
    const l = async () => { const v = $('#cf').value; $('#mx').innerHTML = matrix(await api('/api/schedule' + (v ? '?class_id=' + v : '')), PER, !!v) };
    $('#cf').onchange = l; l(); timer = setInterval(l, 15000);
};

/* ---------- PEMBUAT JADWAL (admin) / PENGATURAN (guru) ---------- */
PAGES.help = async () => {
    if (!isA) return `<div class="card"><h3>Pengaturan Tampilan</h3><div class="sw">Mode Gelap<button class="btn sm" onclick="theme(document.documentElement.dataset.theme==='dark'?'light':'dark')">Ganti</button></div></div>`;
    const [cl, rm, tc, pr] = await Promise.all([api('/api/classes'), api('/api/rooms'), api('/api/teachers'), api('/api/periods')]); PER = pr;
    return `<div class="card"><h3>Tambah Jadwal</h3>
    <div class="row"><select id="bt" onchange="loadMapel()">${opts(tc, 'id', 'full_name')}</select><select id="bs"></select></div>
    <div class="row"><select id="bd">${D.slice(1).map((d, i) => `<option value="${i + 1}">${d}</option>`).join('')}</select>
    <select id="bp">${pr.map(p => `<option value="${p.period}">Jam ke-${p.period} (${p.st}-${p.en})</option>`).join('')}</select>
    <select id="bc" onchange="mine()">${opts(cl)}</select>
    <select id="br"><option value="">Ruang kelasnya sendiri</option>${opts(rm.filter(x => x.category !== 'Kelas Reguler'))}</select></div>
    <div class="row"><button class="btn" style="flex:none" onclick="addS()">Simpan Jadwal</button></div><p id="bm" class="err"></p></div>
    <div class="card"><h3>Jadwal kelas yang dipilih</h3><div id="mine"></div></div>`;
};
AFTER.help = () => { if (isA) { loadMapel(); mine() } };
window.loadMapel = async () => {
    const m = await api('/api/teachers/' + $('#bt').value + '/subjects');
    $('#bs').innerHTML = m.length ? opts(m) : '<option value="">(guru ini belum punya mapel)</option>';
};
window.addS = async () => {
    try {
        await post('/api/builder', { teacher_id: $('#bt').value, subject_id: $('#bs').value, day: $('#bd').value, period: $('#bp').value, class_id: $('#bc').value, room_id: $('#br').value });
        $('#bm').textContent = ''; mine();
    } catch (e) { $('#bm').textContent = e.error || 'Gagal menyimpan jadwal' }
};
window.mine = async () => {
    const r = await api('/api/schedule?class_id=' + $('#bc').value);
    $('#mine').innerHTML = `<div class="wrap"><table><tr><th>Hari</th><th>Jam</th><th>Mapel</th><th>Guru</th><th>Ruang</th><th></th></tr>${r.map(x => `<tr><td>${D[x.day]}</td><td>${x.period} (${x.st})</td><td>${esc(x.subject)}</td><td>${esc(x.teacher)}</td><td>${esc(x.room)}</td><td><button class="btn sm red" onclick="delS(${x.id})">Hapus</button></td></tr>`).join('') || '<tr><td colspan=6 class="muted">Belum ada jadwal untuk kelas ini.</td></tr>'}</table></div>`;
};
window.delS = async i => { if (confirm('Hapus jadwal ini?')) { await api('/api/schedule/' + i, { method: 'DELETE' }); mine() } };

/* ---------- MAPEL, RUANG, TUGAS ---------- */
PAGES.mapel = async () => {
    const SUB = await api('/api/subjects');
    return `<div class="card wrap"><table><tr><th>Kode</th><th>Mata Pelajaran</th><th>Pengampu</th><th>Alokasi</th></tr>${SUB.map(s => `<tr><td>${esc(s.code)}</td><td>${esc(s.name)}</td><td>${esc(s.teachers)}</td><td>${s.hours} Jam/Minggu</td></tr>`).join('')}</table></div>`;
};
PAGES.ruang = async () => {
    const r = await api('/api/rooms'), g = {};
    r.forEach(x => (g[x.category] = g[x.category] || []).push(x));
    return Object.entries(g).map(([k, v]) => `<div class="card"><h3>${esc(k)}</h3><div class="grid g4">${v.map(x => `<div class="cell"><b>${esc(x.name)}</b><br>${x.used_by ? `<span class="pill bad">Terpakai (${esc(x.used_by)})</span>` : '<span class="pill ok">Kosong</span>'}</div>`).join('')}</div></div>`).join('');
};
PAGES.tugas = async () => {
    const AS = await api('/api/assignments');
    return `<div class="card">${isT ? '<button class="btn" onclick="newTask()">+ Buat Tugas</button>' : ''}<div class="wrap"><table><tr><th>Judul</th>${isA ? '<th>Guru</th>' : ''}<th>Mapel</th><th>Kelas</th><th>Batas Waktu</th><th></th></tr>${AS.map(a => `<tr><td><b>${esc(a.title)}</b><br><small class="muted">${esc(a.description)}</small></td>${isA ? `<td>${esc(a.guru)}</td>` : ''}<td>${esc(a.mapel)}</td><td>${esc(a.cls)}</td><td>${fmt(a.due_at)}</td><td>${(isA || isT) ? `<button class="btn sm red" onclick="delTask(${a.id})">Hapus</button>` : ''}</td></tr>`).join('') || '<tr><td colspan="6" class="muted">Belum ada tugas.</td></tr>'}</table></div></div>`;
};
window.newTask = async () => {
    const [cl, sb] = await Promise.all([api('/api/classes'), api('/api/teachers/' + ME.id + '/subjects')]);
    modal(`<h3>Buat Tugas</h3><input id="t1" placeholder="Judul"><select id="t2">${opts(cl)}</select><select id="t6">${opts(sb)}</select><input id="t3" type="datetime-local"><textarea id="t4" rows="3" placeholder="Deskripsi"></textarea><div class="row"><button class="btn" id="ok">Simpan</button><button class="btn ghost" onclick="closeModal()">Batal</button></div>`);
    $('#ok').onclick = async () => { try { await post('/api/assignments', { title: $('#t1').value, class_id: $('#t2').value, subject_id: $('#t6').value, due_at: $('#t3').value, description: $('#t4').value }); closeModal(); go('tugas') } catch (e) { fail(e) } };
};
window.delTask = async i => { if (confirm('Hapus tugas ini?')) { try { await api('/api/assignments/' + i, { method: 'DELETE' }); go('tugas') } catch (e) { fail(e) } } };

/* ---------- HEADER: notifikasi, pesan, profil, pencarian ---------- */
const hide = () => document.querySelectorAll('.drop').forEach(d => d.classList.remove('on'));
async function loadNotif() { try { const n = await api('/api/notifications'); $('#bn').textContent = n.filter(x => !x.read).length || '' } catch (e) { } }
document.addEventListener('click', async e => {
    if (e.target.id === 'modal') closeModal();
    if (!e.target.closest('.drop,#bell,#prof,.search')) hide();
    if (e.target.closest('#bell')) {
        hide(); const n = await api('/api/notifications');
        $('#bellp').innerHTML = n.map(x => `<div>${esc(x.msg)}<br><small class="muted">${fmt(x.created)}${x.read ? '' : ' • baru'}</small></div>`).join('') || '<div class="muted">Belum ada notifikasi</div>';
        $('#bellp').classList.add('on'); await post('/api/notifications', {}); $('#bn').textContent = '';
    } else if (e.target.closest('#prof')) {
        hide(); $('#menu').innerHTML = `<a onclick="chPw()">🔐 Ubah Password</a><a onclick="theme(document.documentElement.dataset.theme==='dark'?'light':'dark')">🌙 Mode Gelap/Terang</a><a href="/logout">🚪 Keluar</a>`; $('#menu').classList.add('on');
    } else if (e.target.closest('#mail')) { hide(); mailbox() }
});
let st;
document.addEventListener('input', e => {
    if (e.target.id !== 'q') return; clearTimeout(st);
    st = setTimeout(async () => {
        const v = e.target.value.trim(), d = $('#sres'); if (v.length < 2) return d.classList.remove('on');
        const r = await api('/api/search?q=' + encodeURIComponent(v));
        d.innerHTML = r.map(x => `<div><small>${esc(x.t)}</small><br><b>${esc(x.a)}</b><br><small>${esc(x.b)}</small></div>`).join('') || '<div class="muted">Tidak ditemukan</div>'; d.classList.add('on');
    }, 250);
});
window.chPw = () => {
    modal(`<h3>Ubah Password</h3><input id="p1" type="password" placeholder="Password lama"><input id="p2" type="password" placeholder="Password baru (min. 6)"><div class="row"><button class="btn" id="ok">Simpan</button><button class="btn ghost" onclick="closeModal()">Batal</button></div>`);
    $('#ok').onclick = async () => { try { await post('/api/password', { old: $('#p1').value, new: $('#p2').value }); closeModal(); alert('Password diubah') } catch (e) { fail(e) } };
};
window.mailbox = async () => {
    const r = await api('/api/leaves');
    const pill = st => `<span class="pill ${st === 'Disetujui' ? 'ok' : st === 'Ditolak' ? 'bad' : 'warn'}">${esc(st || 'Menunggu')}</span>`;
    modal(`<h3>Perizinan Guru</h3>${isT ? '<button class="btn" onclick="leaveForm()">+ Ajukan Izin/Sakit</button>' : ''}${r.map(x => `<div class="card" style="margin:10px 0;padding:10px"><b>${esc(x.who)}</b> <span class="pill warn">${esc(x.kind)}</span> ${String(x.date).slice(0, 10)} ${pill(x.status)}<br><small>${esc(x.note)}</small>${x.proof ? `<br><a href="/uploads/${x.proof}" target="_blank">Lihat bukti</a>` : ''}${isA && (x.status || 'Menunggu') === 'Menunggu' ? `<div class="row" style="margin-top:8px"><button class="btn sm" onclick="decide(${x.id},'Disetujui')">Setujui</button><button class="btn sm red" onclick="decide(${x.id},'Ditolak')">Tolak</button></div>` : ''}</div>`).join('') || '<p class="muted">Belum ada pengajuan.</p>'}<button class="btn ghost" onclick="closeModal()">Tutup</button>`);
};
window.decide = async (id, status) => { try { await post('/api/leaves/' + id + '/decision', { status }); await mailbox() } catch (e) { fail(e) } };
window.leaveForm = () => {
    modal(`<h3>Ajukan Izin/Sakit</h3><form id="lf"><select name="kind"><option>Sakit</option><option>Izin</option></select><input type="date" name="date" value="${new Date().toISOString().slice(0, 10)}" required><textarea name="note" rows="3" placeholder="Keterangan"></textarea><label class="muted">Bukti (PNG, opsional)</label><input type="file" name="proof" accept="image/png"></form><div class="row"><button class="btn" id="ok">Kirim</button><button class="btn ghost" onclick="closeModal()">Batal</button></div>`);
    $('#ok').onclick = async () => { try { await api('/api/leaves', { method: 'POST', body: new FormData($('#lf')) }); closeModal(); alert('Terkirim ke admin') } catch (e) { fail(e) } };
};

init();
