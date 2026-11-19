# tools/ — editor mind map untuk review manual QA

> Version: 1.24
Editor: **`mindmap-editor.html` v1.19** — versinya tertulis di kepala berkas itu sendiri, dan itu
satu-satunya sumbernya.

## Menjalankan

**Klik dua kali `tools/mindmap-editor.html`.** Itu saja — tidak ada server, tidak ada instalasi.

Diukur di Chrome pada mesin ini (2026-08-28): di `file://`, `isSecureContext` bernilai `true` dan
`showSaveFilePicker` tersedia — jadi tombol **Simpan menimpa berkas `.mm` yang dibuka**, sama seperti
lewat localhost.

| Cara buka | Tombol Simpan | Kapan dipakai |
|---|---|---|
| klik dua kali (`file://`) | **menimpa berkas** (Chrome/Edge) | **default** |
| `python tools/open_editor.py` | menimpa berkas | kalau browser Anda tidak punya File System Access API, atau memang ingin lewat localhost |

`open_editor.py` **opsional**. Dia menyalakan server yang hidup sampai `Ctrl+C`, jadi jangan
dijalankan kalau tidak perlu. Browser tanpa API itu (mis. Firefox) akan mengunduh salinan; editor
menyebutkan mana yang berlaku di status bar-nya.

## Dari dalam IDE

| | VS Code | PyCharm |
|---|---|---|
| Buka di browser | klik kanan berkas → *Open with Live Server* / *Reveal in File Explorer* | klik kanan → *Open in Browser* |
| Preview di dalam tab | ekstensi **Live Preview** (Microsoft), atau `Simple Browser: Show` + `open_editor.py` | built-in preview (JCEF), tergantung versi |
| Paling sederhana | buka berkas HTML-nya langsung di browser — **tidak perlu server** | idem |

**`.mm` sebagai tab editor visual di dalam IDE** (Ctrl+S menimpa berkas) butuh ekstensi VS Code
sendiri (`CustomTextEditorProvider` + webview) atau plugin JetBrains. Belum dibuat, dan sengaja:
jalur browser di atas memberi hasil yang sama tanpa biaya pemeliharaan dua ekstensi.

## Tombol

| | |
|---|---|
| **Buka .mm / .mup** | `.mm` dibaca seperti consumer membacanya (`draft-template.md` §2/§7): `TEXT`, atau `<richcontent TYPE="NODE">` kalau `TEXT` tidak ada, dan icon `button_ok` / `checked` / `yes` di leaf menjadi ✅. `.mup` (MindMup) dibaca dari `title` tiap node, urutan anak seperti di MindMup; peta `.mup` dengan lebih dari satu akar ditolak dengan nama-nama akarnya. Menyimpan `.mm` saja: setelah membuka `.mup`, Simpan meminta nama `.mm` baru dan `.mup` aslinya tidak ditimpa. Berkas yang tidak terbaca ditolak dengan alasannya |
| **Roda mouse** | geser peta · **Ctrl+Roda** zoom · **Shift+Roda** geser mendatar |
| **PgUp / PgDn** | geser satu layar · **Home** rapikan tampilan |
| **Klik 2x** / **F2** | ubah teks |
| **Shift+Enter** | baris baru — inilah cara menulis bundle `INT` (daftar bernomor) |
| **Enter** | node sejajar · **Tab** node anak — di root: sub process · di folder E2E: test case · di sub process, Additional atau Archive: entry point · di entry point: type node |
| **t** | ganti rung type node (UI → INT → SYS → E2E) |
| **r** | tandai ✅ regression — hanya di test case SYS dan E2E; di UI / INT ditolak, ✅ yang sudah ada di sana bisa dilepas |
| **[** **]** | perkecil / perbesar lebar node terpilih — bisa juga ditarik dari pegangan di sisi kanannya |
| **Shift+[** **Shift+]** | lebar default SEMUA node |
| **0** | kembalikan lebar node terpilih |
| **Del** hapus · **Space** lipat · **↑↓←→** pindah · **Ctrl+S** simpan |

## Peta besar

Draft nyata bisa berisi ratusan test case. Yang editor lakukan otomatis:

| | |
|---|---|
| di atas 60 TC | dibuka **ringkas** — cabang di bawah type node dilipat, jumlah TC tetap terlihat |
| zoom autofit | ditahan minimum **35%** supaya teks tetap terbaca, bukan dipaksa memuat semuanya |
| jendela diubah ukurannya | fit ulang otomatis — selama Anda belum menggeser / mem-zoom; sesudahnya tekan **Home** |
| menyusuri | **roda mouse menggeser**; `Ctrl+roda` untuk zoom |
| membuka semuanya | tombol **Buka semua cabang** |

Contoh terukur (draft lama berisi 218 leaf): terbuka pada 59% dengan 25 node terbaca dan 16 rung
dilipat; setelah "Buka semua cabang" jadi 286 node pada 35%.

## Pohon draft

Editor membaca dan menulis pohon yang sama dengan Generate Draft TC
(`.claude/skills/generate-draft-tc/references/draft-template.md` §1):

```
FEATURE (Total: N TCs)
├── <sub process> (n)             <- TIDAK bernomor
│   └── 1. <page / entry point> (n) <- dinomori berlanjut satu feature = jumlah page
│       └── UI · INT · SYS (n)
│           └── test case
├── E2E (n)                        <- hanya case End to End
│   └── test case                  <- LANGSUNG: satu perjalanan penuh melewati semua sub process alur utama
├── Additional (n)                 <- case dependency: FDS, event tracker, …
│   └── <topik> (n) → type → test case
└── Archive (n)                    <- case lama yang tidak kompatibel
    └── <entry point asal> (n) → type → test case
```

E2E, Additional dan Archive dikenali dari POSISINYA (anak langsung root), tidak bernomor, dan
selalu ada — boleh kosong. Peta awal yang dibuka editor tanpa berkas sudah memuat ketiganya.
Folder E2E tidak punya entry point dan type node: test case-nya duduk langsung di dalamnya, dan
folder itu sendiri rung-nya.

## Yang editor ini jaga untuk Anda

Empat kesalahan berikut membuat test case **hilang tanpa laporan** di sub-project hilir. Editor ini
mencegah atau menandainya:

| Kesalahan | Yang dilakukan editor |
|---|---|
| leaf di luar type node | **Tab** di entry point membuat *type node* (`UI`, ganti dengan `t`), bukan node kosong; **Tab** di folder E2E membuat test case langsung — jadi leaf tidak pernah lahir di luar rung-nya |
| hitungan `(n)` dan `(Total: N TCs)` basi | **dihitung ulang setiap kali menyimpan** |
| newline jadi spasi (bundle `INT` hancur) | newline selalu ditulis `&#10;` |
| warna di leaf | tidak pernah ditulis — warna hanya di sub process, folder, entry point dan type node (kosmetik) |

Plus **Pra-periksa**: folder E2E / Additional / Archive yang hilang atau ganda, draft tanpa sub
process, type node tanpa level entry point, entry point di dua sub process, sub process atau entry
point tanpa test case, node di folder E2E yang bukan test case (entry point atau type node), type
node E2E di sub process atau Additional, judul duplikat, leaf
di luar type node, bundle > 10 baris, bundle terlipat, leaf non-INT multi-baris, sub process atau
entry point bernama seperti rung, dan node tanpa teks.

🔴 **Pra-periksa bukan otoritas.** Yang memutuskan tetap
`.claude/scripts/validate_draft.py` (Prove) dan
`.claude/scripts/review_result_draft.py` (Audit). Pra-periksa tidak
memeriksa penamaan, coverage, maupun basis.

🔴 **Setiap edit manual wajib di-Prove dan di-Audit ulang:**

```
python .claude/scripts/validate_draft.py "../Draft to Manual Test Case/requirements/<platform>/Draft_<feature>_v<versi>.mm"
python .claude/scripts/review_result_draft.py --platform <platform> --feature <feature>
```

Alasannya bukan formalitas: mengedit draft membuat `trace` **basi**, dan trace basi berarti angka
coverage dihitung terhadap basis yang salah. Audit melaporkannya sebagai `STALE TRACE` dan menolak
menyatakan COMPLETE.

## Yang editor ini TIDAK lakukan

- tidak menulis Steps dan Expected Result — itu milik sub-project hilir;
- tidak tahu requirement index, jadi tidak bisa memberi tahu apakah sebuah leaf punya basis;
- tidak MENYIMPAN format selain `.mm` — format project ini `.mm`. `.mup` hanya dibuka untuk diubah ke `.mm`
  (salinan ini berdiri sendiri; editor di `tools/` pipeline tetap `.mm` saja);
- **pra-periksanya bukan Prove.** Yang Prove (`validate_draft.py`) lakukan dan editor tidak: menolak
  judul duplikat, leaf di luar type node, dan bundle yang terlipat. Draft lama yang QA siapkan di
  sini diproses Review Requirement hanya kalau Prove membacanya sebagai draft lama
  (`validate_draft.py --baseline`);
- tidak menyimpan lebar node ke dalam `.mm` — itu preferensi tampilan, tersimpan di localStorage
  per berkas. Rekan lain yang membuka berkas yang sama memakai lebar default-nya sendiri.

## Diuji

Diuji otomatis di Chrome sungguhan (headless, lewat DevTools Protocol):

| Uji | Hasil |
|---|---|
| edit teks: klik dua kali, ketik, commit | mode edit masuk, caret di dalam teks, ketikan tersimpan |
| lebar node (`[` `]`) | berubah |
| peta besar (`Dashboard`, 218 leaf) | terbuka ringkas 59%, roda menggeser, `Ctrl+roda` mem-zoom |
| **tumpang-tindih node** | **0** — saat ringkas, saat semua terbuka, dan setelah melipat manual |
| fresh clone (folder disalin, profil browser baru) | memuat `.mm` nyata tanpa error JS |
| impor `.mm` berbentuk FreeMind (`richcontent`, icon ✅) — fixture `draft_mm_shapes.mm` milik consumer dan satu bundle `richcontent` | judul, jumlah case, dan regression IDENTIK dengan reader consumer (`parse_draft.py`, dijalankan read-only sebagai pembanding) |
| impor `.mup` (2026-11-18, Chrome headless, fixture **buatan sendiri**: formatVersion 3, 2, tanpa formatVersion, ber-BOM, akar ganda, JSON rusak) | pohon, urutan rank (positif lalu negatif), leaf INT multi-baris dan ✅ terbaca; `.mup` → `.mm` → buka lagi = pohon sama; akar ganda dan JSON rusak ditolak, peta yang sedang terbuka tidak berubah; Simpan setelah `.mup` menyarankan `Draft_x.mm` dan tidak pernah menulis ke `.mup` |
| teks di dalam kotak node (2026-11-18, `Referensi/test mup`, Chrome headless) | sebelum v1.19: 33 dari 48 node meluap saat dibuka ringkas ("N TC tersembunyi" lebih lebar dari kotak `UI`/`INT`/`SYS`). Sesudah: **0** saat ringkas, saat semua cabang terbuka, dan saat node terlipat dipersempit ke 90px; tumpang-tindih tetap **0** |
| fit ulang saat jendela berubah | 1280×700 → 1920×1000: zoom ikut menyesuaikan; setelah roda mouse, mengubah jendela tidak menggeser tampilan; **Home** mengembalikan autofit |
| impor `.mup` nyata dari QA (2026-11-18, `Referensi/test mup` — formatVersion 3, TANPA ekstensi, 231 node, 125 leaf) | 231/231 node dan 125/125 leaf, urutan dan teks IDENTIK dengan JSON-nya; `.mup` → `.mm` → buka lagi = 231 node; tanpa error JS. Yang tidak dibawa ke `.mm`: warna (`#adff2f` di 24 section/type node), catatan root, status lipat MindMup. **Dialog Buka di macOS belum dicoba** |

Fungsi ekspornya diuji headless dengan node (16 uji: escape newline, hitungan dihitung ulang,
penomoran section, tanpa placeholder), lalu hasil `.mm`-nya diumpankan ke `validate_draft.py` →
**PROVEN**, dan round trip reader consumer **5/5 case**.

🔴 **Yang tidak bisa dibuktikan headless:** rasa interaksi — tata letak, fokus saat mengedit, menarik
pegangan lebar — dinilai QA saat memakainya. Kabari kalau ada yang tidak menurut.
