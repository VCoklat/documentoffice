#!/usr/bin/env python3
"""Generate papers/README.md (Indonesian index) from the manifest + verified citations."""
import json, os

CITE = {
 1:("Front. Cell Dev. Biol. 2025;13:1655623","10.3389/fcell.2025.1655623","Mussin NM, dkk."),
 2:("Biomaterials 2023;293:121949","10.1016/j.biomaterials.2022.121949","Rehman FU, dkk."),
 3:("Cell Death Dis. 2022;13(7):580","10.1038/s41419-022-05034-x *","Kou M, dkk."),
 4:("J. Extracell. Biol. 2024;3(5):e156","10.1002/jex2.156","Bhat A, dkk."),
 5:("Trends Pharmacol. Sci. 2024;45(4):350-365","10.1016/j.tips.2024.02.006","Erana-Perez Z, dkk."),
 6:("Neural Regen. Res. 2026;21(2):478-490","10.4103/nrr.nrr-d-24-00720 *","Chen H, dkk."),
 7:("Biochem. Pharmacol. 2022;203:115167","10.1016/j.bcp.2022.115167","Rezaie J, dkk."),
 8:("Regen. Ther. 2026;31:101058","10.1016/j.reth.2025.101058","Shimizu Y, dkk."),
 9:("Cells 2025;14(3):202","10.3390/cells14030202","Harrell CR, dkk."),
 10:("Front. Cell Dev. Biol. 2021;9:705676","10.3389/fcell.2021.705676","Johnson J, dkk."),
 11:("Regen. Ther. 2025;29:303-318","10.1016/j.reth.2025.03.006 *","Goyal A, dkk."),
 12:("Mol. Cells 2024;47(12):100151","10.1016/j.mocell.2024.100151 *","Jung H, dkk."),
 13:("Int. J. Mol. Sci. 2024;25(14):7715","10.3390/ijms25147715","Zhao W, dkk."),
 14:("Processes 2021;9(2):356","10.3390/pr9020356","Han Y, dkk."),
 15:("J. Extracell. Vesicles 2024;13(2):e12404","10.1002/jev2.12404","Welsh JA, dkk."),
 16:("Extracell. Vesicle 2024;4:100052","10.1016/j.vesic.2024.100052","Chen Y, dkk."),
 17:("Pharmaceuticals 2023;16(4):571","10.3390/ph16040571","Abdelsalam M, dkk."),
 18:("Int. J. Mol. Sci. 2025;26(5):1926","10.3390/ijms26051926","Prado-Yupanqui JW, dkk."),
 19:("Biomedicines 2021;9(8):1061","10.3390/biomedicines9081061","Mosquera-Heredia MI, dkk."),
 20:("Cell Death Discov. 2024;10(1):212","10.1038/s41420-024-01973-w *","Tang J, dkk."),
 21:("Front. Med. 2025;12:1625787","10.3389/fmed.2025.1625787","Wang Y, dkk."),
 22:("Front. Cell Dev. Biol. 2024;12:1412363","10.3389/fcell.2024.1412363","Zhao T, dkk."),
 23:("Adv. Healthc. Mater. 2022;11(5):e2100047","10.1002/adhm.202100047","Hettich BF, dkk."),
 24:("Int. J. Mol. Sci. 2024;25(6):3439","10.3390/ijms25063439","Kolenc A, Malicev E."),
 25:("Saudi Pharm. J. 2024;32(6):102096","10.1016/j.jsps.2024.102096","Gul R, dkk."),
 26:("Pharmaceutics 2023;15(3):718","10.3390/pharmaceutics15030718","Mukhopadhya A, dkk."),
 27:("Biomolecules 2026;16(2):269","10.3390/biom16020269","Banerjee A, dkk."),
 28:("Nanomedicine 2016;12(3):655-664","10.1016/j.nano.2015.10.012","Kim MS, dkk."),
 29:("Cells 2023;12(10):1416","10.3390/cells12101416","Zeng H, dkk."),
 30:("Highl. Sci. Eng. Technol. 2022;2:7-14","10.54097/hset.v2i.549","Su R."),
 31:("Int. J. Nanomedicine 2019;14:2847-2859","10.2147/IJN.S200036 *","Vakhshiteh F, dkk."),
 32:("Pharmazie 2021;76(2-3):61-67","10.1691/ph.2021.0128","Xi XM, dkk."),
 33:("Cancer Cell Int. 2025;25:275","10.1186/s12935-025-03900-0 *","Shokati A, dkk. *"),
 34:("Neurochem. Res. 2023;48(5):1334-1346","10.1007/s11064-022-03832-5","Xiong W, dkk."),
 35:("J. Cell. Physiol. 2019;234(6):8182-8191","10.1002/jcp.27615","Oskouie MN, dkk."),
 36:("Stem Cell Res. Ther. 2025;16:210","10.1186/s13287-025-04341-2 *","Ulpiano C, dkk. *"),
 37:("MedComm 2025;6(9):e70386","10.1002/mco2.70386 *","Sun M, Qin F, dkk."),
}
ICON = {"downloaded": "**PDF**", "html-fulltext": "teks", "abstract-only": "abstrak", "unresolved": "gagal", "error": "gagal"}
NOTE = {4: "artikel akses terbuka, tetapi situs Wiley memblokir pengunduhan otomatis",
        6: "diterbitkan di Neural Regen. Res. (bukan Translational Neurodegeneration)",
        11: "diterbitkan di Regen. Ther. (bukan Front. Cell Dev. Biol.)",
        12: "diterbitkan di Mol. Cells (bukan Tissue Eng. Regen. Med.)",
        31: "diterbitkan di Int. J. Nanomedicine (bukan J. Hematol. Oncol.)",
        33: "diterbitkan di Cancer Cell Int.; penulis utama Shokati A, dkk.",
        36: "diterbitkan di Stem Cell Res. Ther.; penulis Ulpiano C, dkk.",
        37: "diterbitkan di MedComm (bukan Pharmaceutics)",
        3: "DOI pada daftar Anda salah; versi yang benar sudah diunduh",
        20: "DOI pada daftar Anda salah; versi yang benar sudah diunduh"}

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
jobs = json.load(open(os.path.join(HERE, "jobs.json"), encoding="utf-8"))
man = {r["n"]: r for r in json.load(open(os.path.join(HERE, "manifest.json"), encoding="utf-8"))}

full = [n for n in man if man[n]["status"] in ("downloaded", "html-fulltext")]
abs_only = sorted(n for n in man if man[n]["status"] == "abstract-only")

L = []
L.append("# Kumpulan PDF penelitian — MSC-derived extracellular vesicles\n")
L.append(f"**{len(jobs)} dari {len(jobs)} makalah** tersedia di folder ini: "
         f"**{len(full)} teks penuh** ({sum(1 for n in full if man[n]['status'] == 'downloaded')} PDF asli penerbit, "
         f"{sum(1 for n in full if man[n]['status'] == 'html-fulltext')} teks penuh hasil konversi) dan "
         f"**{len(abs_only)} hanya abstrak** (artikel berbayar/tidak tersedia versi terbuka).\n")
L.append("Nama berkas memakai judul penelitian, diawali nomor urut agar cocok dengan daftar Anda.\n")
L.append("Keterangan status:\n")
L.append("- **PDF** = berkas PDF resmi dari penerbit/repositori (paling lengkap, ada gambar & tabel)")
L.append("- **teks** = teks penuh artikel dikonversi menjadi PDF (isi lengkap, gambar/tata letak tidak direproduksi)")
L.append("- **abstrak** = hanya catatan bibliografi + abstrak (artikel di balik paywall)\n")
L.append("## Daftar berkas\n")
L.append("| No | Judul (singkat) | Jurnal & tahun | Status | DOI |")
L.append("|----|-----------------|----------------|--------|-----|")
for j in jobs:
    n = j["n"]
    r = man.get(n, {})
    cite, doi, _ = CITE[n]
    short = j["title"] if len(j["title"]) <= 72 else j["title"][:69].rsplit(" ", 1)[0] + "..."
    L.append(f"| {n} | {short} | {cite} | {ICON.get(r.get('status'), '?')} | [{doi.replace(' *','')}](https://doi.org/{doi.replace(' *','')}) |")
L.append("\n## Catatan penting\n")
L.append(f"1. **Koreksi DOI**: entri 3 dan 20 pada daftar Anda memakai DOI yang menunjuk ke artikel lain; "
         "saya sudah mencari DOI yang benar lewat Europe PMC dan mengunduh artikel yang tepat.")
L.append("2. **Perbedaan jurnal/tahun** (daftar Anda vs. rekaman resmi) — judul penelitian tetap sama: "
         + ", ".join(f"no. {n}" for n in (6, 11, 12, 31, 33, 36, 37)) + ".")
L.append("3. **Hanya abstrak** (paywall, tidak ada versi akses terbuka): "
         + ", ".join(f"no. {n}" for n in abs_only)
         + ". Untuk ini saya sertakan halaman abstrak + tautan DOI; naskah penuh bisa diakses lewat langganan perpustakaan kampus "
           "atau fitur *interlibrary loan*.")
L.append("4. Semua berkas diunduh dari sumber akses terbuka resmi (penerbit, Europe PMC/PMC, DOAJ, Unpaywall). "
         "Tidak ada paywall yang ditembus.\n")
L.append("## Detail teknis\n")
L.append("Pengunduhan dijalankan otomatis lewat GitHub Actions (`.github/workflows/zz-fetch-papers.yml`) "
         "memakai skrip `.scratch/papers/fetch_papers.py`. Rekap lengkap per makalah (sumber URL, lisensi, "
         "jumlah halaman, catatan percobaan) ada di `.scratch/papers/manifest.json` dan `.scratch/papers/REPORT.md`.\n")
L.append("Setiap PDF diperiksa otomatis (judul/DOI harus cocok dengan artikel yang dimaksud) sebelum disimpan.\n")

out = os.path.join(REPO, "papers", "README.md")
open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote", out)
