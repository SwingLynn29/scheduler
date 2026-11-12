\set ON_ERROR_STOP on
-- Jadwal PPLG kelas X, XI, XII untuk DEMO (data contoh, bukan jadwal resmi sekolah).
-- Senin kelas X PPLG mengikuti foto jadwal; selain itu disusun otomatis dari guru dan mapel PPLG di kurikulum, tanpa bentrok.
-- Jalankan: psql -U postgres -d scheduler -f isi_jadwal_pplg.sql
-- Tiap baris data: (hari, jam, kelas, kode guru, nama mapel). hari: 1=Senin ... 5=Jumat.
BEGIN;

-- Jam ke-10 belum ada di tabel jam pelajaran (schema hanya 1-9), jadi ditambahkan.
INSERT INTO periods(period, start_t, end_t) VALUES (10, '15:15', '16:00') ON CONFLICT (period) DO NOTHING;

CREATE TEMP TABLE jp(hari INT, jam INT, kelas TEXT, kode TEXT, mapel TEXT) ON COMMIT DROP;
INSERT INTO jp VALUES
    (1,2,'X PPLG','TK','Bahasa Inggris'),
    (1,3,'X PPLG','TK','Bahasa Inggris'),
    (1,4,'X PPLG','TK','Bahasa Inggris'),
    (1,5,'X PPLG','MI','Proyek Ilmu Pengetahuan Alam dan Sosial'),
    (1,6,'X PPLG','MI','Proyek Ilmu Pengetahuan Alam dan Sosial'),
    (1,7,'X PPLG','MI','Proyek Ilmu Pengetahuan Alam dan Sosial'),
    (1,8,'X PPLG','MI','Proyek Ilmu Pengetahuan Alam dan Sosial'),
    (1,9,'X PPLG','MV','Pendidikan Pancasila'),
    (1,10,'X PPLG','MV','Pendidikan Pancasila'),
    (2,1,'X PPLG','CA','Dasar-dasar PPLG'),
    (2,2,'X PPLG','CA','Dasar-dasar PPLG'),
    (2,3,'X PPLG','CA','Dasar-dasar PPLG'),
    (2,4,'X PPLG','LC','Seni dan Budaya'),
    (2,5,'X PPLG','SH','Bahasa Indonesia'),
    (2,6,'X PPLG','SH','Bahasa Indonesia'),
    (2,7,'X PPLG','NN','Informatika'),
    (2,8,'X PPLG','NN','Informatika'),
    (2,9,'X PPLG','CA','Dasar-dasar PPLG'),
    (2,10,'X PPLG','LN','Matematika'),
    (3,1,'X PPLG','CA','Dasar-dasar PPLG'),
    (3,2,'X PPLG','CA','Dasar-dasar PPLG'),
    (3,3,'X PPLG','CA','Dasar-dasar PPLG'),
    (3,4,'X PPLG','LC','Seni dan Budaya'),
    (3,5,'X PPLG','SH','Bahasa Indonesia'),
    (3,6,'X PPLG','SH','Bahasa Indonesia'),
    (3,7,'X PPLG','NN','Informatika'),
    (3,8,'X PPLG','NN','Informatika'),
    (3,9,'X PPLG','IM','Sejarah'),
    (3,10,'X PPLG','IM','Sejarah'),
    (4,1,'X PPLG','RK','Pendidikan Agama Islam dan Budi Pekerti'),
    (4,2,'X PPLG','RK','Pendidikan Agama Islam dan Budi Pekerti'),
    (4,3,'X PPLG','RK','Pendidikan Agama Islam dan Budi Pekerti'),
    (4,4,'X PPLG','TK','Bahasa Inggris'),
    (4,5,'X PPLG','CA','Dasar-dasar PPLG'),
    (4,6,'X PPLG','CA','Dasar-dasar PPLG'),
    (4,7,'X PPLG','CA','Dasar-dasar PPLG'),
    (4,8,'X PPLG','CA','Dasar-dasar PPLG'),
    (4,9,'X PPLG','CA','Dasar-dasar PPLG'),
    (4,10,'X PPLG','LN','Matematika'),
    (5,2,'X PPLG','RP','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (5,3,'X PPLG','RP','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (5,4,'X PPLG','RP','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (5,5,'X PPLG','LN','Matematika'),
    (5,6,'X PPLG','LN','Matematika'),
    (5,7,'X PPLG','CA','Dasar-dasar PPLG'),
    (5,8,'X PPLG','CA','Dasar-dasar PPLG'),
    (5,9,'X PPLG','CA','Dasar-dasar PPLG'),
    (5,10,'X PPLG','CA','Dasar-dasar PPLG'),
    (1,2,'XI PPLG','EJ','Pendidikan Agama Islam dan Budi Pekerti'),
    (1,3,'XI PPLG','EJ','Pendidikan Agama Islam dan Budi Pekerti'),
    (1,4,'XI PPLG','EJ','Pendidikan Agama Islam dan Budi Pekerti'),
    (1,5,'XI PPLG','EL','Matematika'),
    (1,6,'XI PPLG','EL','Matematika'),
    (1,7,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (1,8,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (1,9,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (1,10,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (2,1,'XI PPLG','RZ','Basis Data'),
    (2,2,'XI PPLG','RZ','Basis Data'),
    (2,3,'XI PPLG','RZ','Basis Data'),
    (2,4,'XI PPLG','MV','Pendidikan Pancasila'),
    (2,5,'XI PPLG','NN','Informatika'),
    (2,6,'XI PPLG','NN','Informatika'),
    (2,7,'XI PPLG','ID','Kreativitas, Inovasi dan Kewirausahaan'),
    (2,8,'XI PPLG','ID','Kreativitas, Inovasi dan Kewirausahaan'),
    (2,9,'XI PPLG','ID','Kreativitas, Inovasi dan Kewirausahaan'),
    (2,10,'XI PPLG','EL','Matematika'),
    (3,1,'XI PPLG','RZ','Pemrograman Web'),
    (3,2,'XI PPLG','RZ','Pemrograman Web'),
    (3,3,'XI PPLG','RZ','Pemrograman Web'),
    (3,4,'XI PPLG','MA','Bahasa Indonesia'),
    (3,5,'XI PPLG','MA','Bahasa Indonesia'),
    (3,6,'XI PPLG','MA','Bahasa Indonesia'),
    (3,7,'XI PPLG','RZ','Basis Data'),
    (3,8,'XI PPLG','RZ','Basis Data'),
    (3,9,'XI PPLG','RZ','Basis Data'),
    (3,10,'XI PPLG','MV','Pendidikan Pancasila'),
    (4,1,'XI PPLG','HP','Bahasa Inggris'),
    (4,2,'XI PPLG','HP','Bahasa Inggris'),
    (4,3,'XI PPLG','HP','Bahasa Inggris'),
    (4,4,'XI PPLG','MA','Bahasa Indonesia'),
    (4,5,'XI PPLG','NN','Informatika'),
    (4,6,'XI PPLG','NN','Informatika'),
    (4,7,'XI PPLG','RZ','Pemrograman Web'),
    (4,8,'XI PPLG','RZ','Pemrograman Web'),
    (4,9,'XI PPLG','RZ','Pemrograman Web'),
    (4,10,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (5,2,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (5,3,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (5,4,'XI PPLG','CA','Pemrograman Berbasis Text & Multimedia (PPLG)'),
    (5,5,'XI PPLG','NT','Sejarah'),
    (5,6,'XI PPLG','NT','Sejarah'),
    (5,7,'XI PPLG','DN','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (5,8,'XI PPLG','DN','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (5,9,'XI PPLG','DN','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (5,10,'XI PPLG','EL','Matematika'),
    (1,2,'XII PPLG','NT','Internet of Things (IoT) (Mapel Pilihan PPLG)'),
    (1,3,'XII PPLG','NT','Internet of Things (IoT) (Mapel Pilihan PPLG)'),
    (1,4,'XII PPLG','NT','Internet of Things (IoT) (Mapel Pilihan PPLG)'),
    (1,5,'XII PPLG','RW','Matematika'),
    (1,6,'XII PPLG','RW','Matematika'),
    (1,7,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (1,8,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (1,9,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (1,10,'XII PPLG','IM','Sejarah'),
    (2,1,'XII PPLG','NT','Pemrograman Web'),
    (2,2,'XII PPLG','NT','Pemrograman Web'),
    (2,3,'XII PPLG','NT','Pemrograman Web'),
    (2,4,'XII PPLG','RZ','Pemrograman Berbasis Text & Multimedia'),
    (2,5,'XII PPLG','IU','Pendidikan Pancasila'),
    (2,6,'XII PPLG','IU','Pendidikan Pancasila'),
    (2,7,'XII PPLG','RZ','Pemrograman Berbasis Text & Multimedia'),
    (2,8,'XII PPLG','RZ','Pemrograman Berbasis Text & Multimedia'),
    (2,9,'XII PPLG','RZ','Pemrograman Berbasis Text & Multimedia'),
    (2,10,'XII PPLG','ET','Bahasa Indonesia'),
    (3,1,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (3,2,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (3,3,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (3,4,'XII PPLG','RZ','Pemrograman Berbasis Text & Multimedia'),
    (3,5,'XII PPLG','RW','Matematika'),
    (3,6,'XII PPLG','RW','Matematika'),
    (3,7,'XII PPLG','SA','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (3,8,'XII PPLG','SA','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (3,9,'XII PPLG','SA','Pendidikan Jasmani, Olahraga dan Kesehatan'),
    (3,10,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (4,1,'XII PPLG','NT','Pemrograman Web'),
    (4,2,'XII PPLG','NT','Pemrograman Web'),
    (4,3,'XII PPLG','NT','Pemrograman Web'),
    (4,4,'XII PPLG','NN','Pemrograman Perangkat Bergerak'),
    (4,5,'XII PPLG','LC','Seni dan Budaya'),
    (4,6,'XII PPLG','LC','Seni dan Budaya'),
    (4,7,'XII PPLG','NT','Internet of Things (IoT) (Mapel Pilihan PPLG)'),
    (4,8,'XII PPLG','NT','Internet of Things (IoT) (Mapel Pilihan PPLG)'),
    (4,9,'XII PPLG','NT','Internet of Things (IoT) (Mapel Pilihan PPLG)'),
    (4,10,'XII PPLG','ET','Bahasa Indonesia'),
    (5,2,'XII PPLG','NA','Pendidikan Agama Islam dan Budi Pekerti'),
    (5,3,'XII PPLG','NA','Pendidikan Agama Islam dan Budi Pekerti'),
    (5,4,'XII PPLG','NA','Pendidikan Agama Islam dan Budi Pekerti'),
    (5,5,'XII PPLG','ET','Bahasa Indonesia'),
    (5,6,'XII PPLG','ET','Bahasa Indonesia'),
    (5,7,'XII PPLG','IY','Bahasa Inggris'),
    (5,8,'XII PPLG','IY','Bahasa Inggris'),
    (5,9,'XII PPLG','IY','Bahasa Inggris'),
    (5,10,'XII PPLG','IM','Sejarah');

-- Jadwal lama ketiga kelas PPLG dihapus dulu supaya skrip aman dijalankan ulang.
DELETE FROM schedules WHERE class_id IN (SELECT id FROM rooms WHERE name IN ('X PPLG','XI PPLG','XII PPLG'));

INSERT INTO schedules(day, period, class_id, subject_id, teacher_id, room_id)
SELECT jp.hari, jp.jam, c.id, s.id, t.id, c.id
FROM jp
JOIN rooms c ON c.name = jp.kelas
JOIN teachers t ON t.code = jp.kode
JOIN subjects s ON s.name = jp.mapel;

-- Baris yang kelas, kode guru, atau mapelnya tidak ditemukan (kalau ada) ditampilkan di sini:
SELECT jp.* FROM jp
LEFT JOIN rooms c ON c.name = jp.kelas LEFT JOIN teachers t ON t.code = jp.kode LEFT JOIN subjects s ON s.name = jp.mapel
WHERE c.id IS NULL OR t.id IS NULL OR s.id IS NULL;

DO $$ BEGIN
  IF (SELECT count(*) FROM jp) <> (SELECT count(*) FROM schedules WHERE class_id IN (SELECT id FROM rooms WHERE name IN ('X PPLG','XI PPLG','XII PPLG'))) THEN
    RAISE EXCEPTION 'Ada baris yang tidak cocok (lihat daftar di atas). Tidak ada yang disimpan.';
  END IF;
END $$;

COMMIT;
SELECT c.name AS kelas, count(*) AS jam_terisi FROM schedules s JOIN rooms c ON c.id = s.class_id WHERE c.name LIKE '%PPLG' GROUP BY c.name ORDER BY c.name;