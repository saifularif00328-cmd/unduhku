#!/usr/bin/env python3
"""Mesin unduh UnduhKu (by Saiful Arif).

Dijalankan oleh GitHub Actions. Membaca parameter dari environment, mengunduh
dengan yt-dlp + ffmpeg, lalu mengunggah hasilnya ke GitHub Release (tag dl).
Kalau gagal, mengunggah berkas {JOB_ID}.err.txt yang labelnya berisi pesan
singkat supaya aplikasi bisa menampilkannya ke pengunjung.
"""
import ipaddress
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

JOB_ID = os.environ.get("JOB_ID", "")
URL = os.environ.get("MEDIA_URL", "").strip()
KIND = os.environ.get("KIND", "video")
QUALITY = os.environ.get("QUALITY", "1080")
AUDIO = os.environ.get("AUDIO_FORMAT", "mp3")
TAG = os.environ.get("RELEASE_TAG", "dl")
COOKIES = os.environ.get("COOKIES_TXT", "")
MAX_MB = 1900  # batas ukuran satu aset release GitHub adalah 2 GiB

OUT = Path("out")
OUT.mkdir(exist_ok=True)


def sh(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True, text=True)


def short(msg, n=140):
    msg = re.sub(r"\s+", " ", re.sub(r"\x1b\[[0-9;]*m", "", str(msg))).strip().replace("#", "")
    return msg[:n]


def friendly(err):
    t = str(err)
    low = t.lower()
    if "not a bot" in low or "sign in to confirm" in low:
        return "YouTube memblokir server GitHub. Admin perlu menambahkan cookies (secret COOKIES_TXT)."
    if "private video" in low or "login required" in low or "requires login" in low or "log in" in low:
        return "Video bersifat privat atau butuh login."
    if "unsupported url" in low:
        return "Link ini belum didukung."
    if "max-filesize" in low or "larger than" in low:
        return "Ukuran file melebihi 1,9 GB. Pilih resolusi lebih rendah."
    if "requested format is not available" in low:
        return "Resolusi yang dipilih tidak tersedia. Coba resolusi lain."
    if "video unavailable" in low or "not available" in low:
        return "Video tidak tersedia atau diblokir di wilayah server."
    return "Gagal mengunduh: " + short(t, 110)


def check_input():
    if not re.fullmatch(r"[a-z0-9]{4,40}", JOB_ID):
        sys.exit("JOB_ID tidak valid")
    u = urlparse(URL)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ValueError("Link tidak valid")
    host = u.hostname.lower()
    if host == "localhost" or host.endswith((".local", ".internal")):
        raise ValueError("Alamat ini tidak diizinkan")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("Alamat IP langsung tidak diizinkan")
    if KIND not in ("video", "audio"):
        raise ValueError("Jenis unduhan tidak dikenal")


def build_opts():
    o = {
        "outtmpl": str(OUT / f"{JOB_ID}-raw.%(ext)s"),
        "noplaylist": True,
        "playlist_items": "1",
        "max_filesize": MAX_MB * 1024 * 1024,
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
        "restrictfilenames": True,
        "concurrent_fragment_downloads": 4,
    }
    if COOKIES.strip():
        cf = Path("cookies.txt")
        cf.write_text(COOKIES, encoding="utf-8")
        o["cookiefile"] = str(cf)
    if KIND == "audio":
        o["format"] = "ba/b"
        codec = AUDIO if AUDIO in ("mp3", "wav", "best") else "mp3"
        pp = {"key": "FFmpegExtractAudio", "preferredcodec": codec}
        if codec == "mp3":
            pp["preferredquality"] = "0"
        o["postprocessors"] = [pp]
    else:
        q = QUALITY if QUALITY.isdigit() else "1080"
        o["format"] = f"bv*[height<={q}]+ba/b[height<={q}]/bv*+ba/b"
        o["format_sort"] = [f"res:{q}", "vcodec:h264", "acodec:m4a"]
        o["merge_output_format"] = "mp4/mkv"
    return o


def slug(title):
    s = re.sub(r"[^A-Za-z0-9]+", "-", title or "").strip("-")[:50]
    return s or "media"


def ensure_release():
    if sh("gh", "release", "view", TAG, check=False).returncode != 0:
        sh("gh", "release", "create", TAG, "--title", "Hasil unduhan",
           "--notes", "Berkas sementara. Dihapus otomatis setelah sekitar 90 menit.", check=False)


def upload(path, label):
    ensure_release()
    last = None
    for _ in range(4):
        r = sh("gh", "release", "upload", TAG, f"{path}#{label}", "--clobber", check=False)
        if r.returncode == 0:
            return
        last = r.stderr
        time.sleep(3)
        ensure_release()
    raise RuntimeError("Gagal mengunggah ke release: " + short(last or "", 100))


def report_error(message):
    p = OUT / f"{JOB_ID}.err.txt"
    p.write_text(message, encoding="utf-8")
    try:
        upload(p, short(message))
    except Exception as e:  # noqa: BLE001
        print("Gagal mengunggah pesan galat:", e)


def main():
    try:
        check_input()
    except ValueError as e:
        report_error(str(e))
        sys.exit(1)

    try:
        with yt_dlp.YoutubeDL(build_opts()) as ydl:
            info = ydl.extract_info(URL, download=True)
        if info and info.get("_type") == "playlist" and info.get("entries"):
            info = next((e for e in info["entries"] if e), info)
        title = (info or {}).get("title") or "media"

        files = [f for f in OUT.glob(f"{JOB_ID}-raw.*") if f.suffix not in (".part", ".ytdl", ".temp")]
        if not files:
            raise RuntimeError("Tidak ada berkas hasil unduhan")
        raw = max(files, key=lambda f: f.stat().st_size)
        final = OUT / f"{JOB_ID}.{slug(title)}{raw.suffix}"
        raw.rename(final)

        size_mb = final.stat().st_size / 1048576
        print(f"Berkas siap: {final.name} ({size_mb:.1f} MB)")
        if size_mb > MAX_MB:
            raise RuntimeError("max-filesize: berkas melebihi batas")
        upload(final, short(title, 120))
        print("Selesai diunggah")
    except Exception as e:  # noqa: BLE001
        msg = friendly(e)
        print("GAGAL:", e)
        report_error(msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
