-- Jalankan: createdb scheduler && psql scheduler -f schema.sql
\set ON_ERROR_STOP on
BEGIN;

-- 1. Pembuatan Tabel Dasar (Fokus Admin & Guru)
CREATE TABLE IF NOT EXISTS admin(
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rooms(
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects(
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    hours INT NOT NULL
);

CREATE TABLE IF NOT EXISTS periods(
    period INT PRIMARY KEY,
    start_t TIME NOT NULL,
    end_t TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers(
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    photo TEXT,
    subject_id INT REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS schedules(
    id SERIAL PRIMARY KEY,
    day INT CHECK(day BETWEEN 1 AND 5),
    period INT REFERENCES periods(period),
    class_id INT REFERENCES rooms(id),
    subject_id INT REFERENCES subjects(id),
    teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE,
    room_id INT REFERENCES rooms(id),
    UNIQUE(day, period, class_id),
    UNIQUE(day, period, teacher_id),
    UNIQUE(day, period, room_id)
);

CREATE TABLE IF NOT EXISTS leaves(
    id SERIAL PRIMARY KEY,
    role TEXT,
    uid INT,
    kind TEXT,
    date DATE,
    p_from INT,
    p_to INT,
    note TEXT,
    proof TEXT,
    created TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications(
    id SERIAL PRIMARY KEY,
    role TEXT,
    uid INT,
    msg TEXT,
    kind TEXT DEFAULT 'info',
    read BOOL DEFAULT FALSE,
    created TIMESTAMP DEFAULT now()
);

-- 2. Data Master: Akun Admin Otomatis (Aman dari pendaftaran bebas)
INSERT INTO admins(username, password_hash, full_name) 
VALUES ('admin', 'pbkdf2:sha256:600000$d15dde923951be0c$04aa9a9f62ce801a0eee324b00e33406a1e4cf5be5b7d499c5d65a2ccfe6da2a', 'Administrator') 
ON CONFLICT (username) DO NOTHING;

-- 3. Data Master: Ruangan & Kelas Reguler
INSERT INTO rooms(name, category) 
SELECT l || ' ' || p, 'Kelas Reguler' 
FROM unnest(ARRAY['X', 'XI', 'XII']) l, 
     unnest(ARRAY['AKL 1', 'AKL 2', 'MPLB 1', 'MPLB 2', 'PM 1', 'PM 2', 'ULW 1', 'ULW 2', 'DKV 1', 'DKV 2', 'TJKT 1', 'TJKT 2', 'PPLG', 'ANM']) p 
ON CONFLICT DO NOTHING;

INSERT INTO rooms(name, category) VALUES
('Lab Komputer 2', 'Laboratorium'),
('Lab Samsung 1', 'Laboratorium'),
('Lab DKV 1', 'Laboratorium'),
('Lab PM 1', 'Laboratorium'),
('Lab ULW 1', 'Laboratorium'),
('Lab MPLB 1', 'Laboratorium'),
('Lab AKL 1', 'Laboratorium'),
('Lab TJKT 1', 'Laboratorium'),
('Lapangan Voli', 'Lapangan'),
('Lapangan Basket', 'Lapangan'),
('Masjid', 'Aula') 
ON CONFLICT DO NOTHING;

-- 4. Data Master: Mata Pelajaran
INSERT INTO subjects(code, name, hours) VALUES
('PAI', 'Pendidikan Agama Islam dan Budi Pekerti', 3),
('PAK', 'Pendidikan Agama Kristen dan Budi Pekerti', 3),
('PANC', 'Pendidikan Pancasila', 2),
('BIN', 'Bahasa Indonesia', 4),
('BIN-L', 'Bahasa Indonesia Lanjutan (Mapel Pilihan DKV)', 2),
('PJK', 'Pendidikan Jasmani, Olahraga dan Kesehatan', 3),
('MTK', 'Matematika', 4),
('MTK-L', 'Matematika Lanjutan (Mapel Pilihan)', 2),
('MTK-LD', 'Matematika Lanjutan (Mapel Pilihan DKV)', 2),
('MTK-LM', 'Matematika Lanjutan (Mapel Pilihan MPLB)', 2),
('BIG', 'Bahasa Inggris', 4),
('BIG-L', 'Bahasa Inggris Lanjutan (Mapel Pilihan ULW)', 2),
('KIK', 'Kreativitas, Inovasi dan Kewirausahaan', 3),
('PIPS', 'Proyek Ilmu Pengetahuan Alam dan Sosial', 4),
('INF', 'Informatika', 3),
('DPP', 'Dasar-Dasar Pemasaran', 3),
('MKT', 'Marketing', 3),
('BSR', 'Bisnis Ritel', 3),
('MGL', 'Manajemen Logistik (Mapel Pilihan MPLB)', 3),
('AKJD', 'Akuntansi Jasa dan Dagang', 3),
('AKLMB', 'Akuntansi Lembaga', 3),
('AKK', 'Akuntansi Keuangan', 3),
('ADP', 'Administrasi Pajak', 3),
('DSA', 'Dasar-dasar Akuntansi', 3),
('KAM', 'Komputer Akuntansi (MYOB)', 3),
('ADU', 'Administrasi Umum (AKL 1)', 3),
('LYP', 'Layanan Perbankan (Mapel Pilihan AKL) (AKL 1)', 3),
('AKM', 'Akuntansi Manufaktur', 3),
('EKB', 'Ekonomi Bisnis', 3),
('POA', 'Pengelolaan Administrasi Umum (MPLB 1)', 3),
('AKLNT', 'Akuntansi Lanjutan (Mapel Pilihan)', 3),
('AKLIP', 'Akuntansi Lembaga/Instansi Pemerintahan', 3),
('PHK', 'Pengelolaan Humas dan Keprotokolan', 3),
('PKS', 'Pengelolaan Keuangan Sederhana', 3),
('PRP', 'Pengelolaan Rapat/Pertemuan', 3),
('TKP', 'Teknologi Perkantoran', 3),
('KTK', 'Komunikasi Tempat Kerja', 3),
('PSP', 'Pengelolaan Sarana Prasarana', 3),
('DDM', 'Dasar-dasar MPLB', 3),
('PKR', 'Pengelolaan Kearsipan', 3),
('PSD', 'Pengelolaan SDM', 3),
('PBR', 'Pengelolaan Bisnis Ritel', 3),
('ADT', 'Administrasi Transaksi', 3),
('PDP', 'Pengemasan dan Pendistribusian Produk', 3),
('KIKPM', 'Kreativitas, Inovasi dan Kewirausahaan (PM2)', 3),
('CSS', 'Customer Service', 3),
('KMB', 'Komunikasi Bisnis', 3),
('BSD', 'Bisnis Digital (Mapel Pilihan PM)', 3),
('SMM', 'Strategi Marketing Visual Merchandising', 3),
('POPW', 'Perencanaan & Pengorganisasian Perjalanan Wisata (POPW)', 3),
('TCK', 'Pemesanan dan Perhitungan Tarif Transportasi Udara, Darat dan Laut (Ticketing)', 3),
('PWM', 'Pemanduan Wisata dan memimpin rombongan wisata', 3),
('DDULW', 'Dasar-Dasar ULW (ULW 2)', 3),
('MICE', 'Pengelolaan Kegiatan MICE secara Luring dan/atau Daring', 3),
('PPWD', 'Pemasaran Produk Wisata Berbasis Digital', 3),
('KPG', 'Komputer Grafis (DKV 1)', 3),
('ANM2D', 'Animasi 2D (ANM)', 3),
('DSP', 'Desain Publikasi', 3),
('VDO', 'Videografi (DKV 2)', 3),
('VDO1', 'Videografi (DKV 1) / Dasar-dasar DKV (DKV 2)', 3),
('FOT', 'Fotografi', 3),
('SBD', 'Seni dan Budaya', 2),
('DDANM', 'Dasar-dasar Animasi', 3),
('DDDKV', 'Dasar-dasar DKV (DKV 1)', 3),
('TJKN', 'Teknologi Jaringan Kabel dan Nirkabel', 3),
('ASJ', 'Administrasi Sistem Jaringan', 3),
('INFTJKT', 'Informatika (TJKT)', 3),
('TKJT-P', 'Teknik Komputer Jaringan (Mapel Pilihan TJKT)', 3),
('KMS', 'Keamanan Jaringan', 3),
('AIJ', 'Administrasi Infrastruktur Jaringan', 3),
('DSTJKT', 'Dasar-dasar TJKT (TJKT 1)', 3),
('PBT', 'Pemrograman Berbasis Text & Multimedia', 3),
('PWEB', 'Pemrograman Web', 3),
('PPB', 'Pemrograman Perangkat Bergerak', 3),
('IOT', 'Internet of Things (IoT) (Mapel Pilihan PPLG)', 3),
('DSPPLG', 'Dasar-dasar PPLG', 3),
('BK', 'Bimbingan Konseling (BK)', 2)
ON CONFLICT (code) DO NOTHING;

-- 5. Data Master: Jam Pembelajaran (Periods) dengan jam fleksibel
INSERT INTO periods (period, start_t, end_t) VALUES 
(1, '07:15', '08:00'),
(2, '08:00', '08:45'),
(3, '08:45', '09:30'),
(4, '09:30', '10:15'),
-- Istirahat Pagi: 10:15 - 10:30
(5, '10:30', '11:15'),
(6, '11:15', '12:00'),
-- Ishoma (Istirahat, Sholat, Makan): 12:00 - 13:00
(7, '13:00', '13:45'),
(8, '13:45', '14:30'),
(9, '14:30', '15:15')
-- Pukul 15:15 - 15:30 waktu persiapan pulang / apel / kebersihan kelas
ON CONFLICT (period) DO UPDATE 
SET start_t = EXCLUDED.start_t, end_t = EXCLUDED.end_t;

COMMIT;