# 🎬 Video to Frames Pro / Video Kare Yakalayıcı

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6" />
  <img src="https://img.shields.io/badge/Engine-OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Platform-Windows%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>Extract high-resolution photos and frames from videos with zero quality loss. Features multi-video playlist batch processing, smart zoom/crop focus, and precise trimming. Free, open-source, and portable tool.</b><br>
  <i>Çoklu video oynatma listesi (playlist/batch), akıllı yakınlaştırma (zoom) ve zaman kırpma özellikli ücretsiz, açık kaynaklı ve portable video kare yakalayıcı.</i><br>
  Developed by <a href="https://www.eroldizdar.tr/"><b>Erol Dizdar</b></a>
</p>

---

## 🌐 Official Website & Downloads / Resmi Web Sayfası ve İndirme

All downloads, setup guides, and portable packages are available on the official website:
Tüm indirme seçenekleri, taşınabilir (portable) sürümler ve detaylı rehber resmi web sayfasında yer almaktadır:

👉 **[Download Video to Frames Pro / Programı İndir (eroldizdar.tr)](https://www.eroldizdar.tr/p/video-to-frames.html)**

---

## ✨ Features / Özellikler

### 🇬🇧 English
- **📋 Playlist & Batch Processing:** Add multiple videos (1, 10, or 100) to the queue and extract frames sequentially with one click.
- **🔍 Smart Zoom & Focus:** Zoom into details with 1.25x, 1.5x, 2.0x, or 3.0x magnification. Choose focus regions: Center, Top-Left, Top-Right, Bottom-Left, or Bottom-Right with Lanczos-4 high-fidelity scaling.
- **✂️ Time Trimming:** Specify Start Time and End Time in seconds to extract stills exclusively from your desired segment.
- **🎯 4 Extraction Modes:**
  1. *Time Interval:* Extract every X seconds (e.g. every 1s or 0.5s).
  2. *Total Count:* Evenly spread across duration (e.g. exactly 50 photos).
  3. *Frame Step:* Capture every N frames (e.g. every 30th frame).
  4. *Full FPS:* Export every single frame.
- **💎 Zero Quality Loss:** 100% Lossless PNG or high-quality JPG (95% default). Original 1080p, 2K, 4K, 8K resolutions preserved.
- **⏱️ Precise Timestamps:** Files named as `frame_00001_01m24s_350ms.jpg`.
- **🚀 100% Portable:** Single-file `.exe`. No Python or FFmpeg installation required.
- **🌐 Bilingual UI:** Switch between English (🇬🇧) and Turkish (🇹🇷) with a single click.

### 🇹🇷 Türkçe
- **📋 Oynatma Listesi ve Toplu İşlem:** Onlarca videoyu listeye ekleyip tek tıkla arka planda sırayla işleme.
- **🔍 Akıllı Yakınlaştırma (Zoom):** 1.25x, 1.5x, 2.0x (2 Kat) ve 3.0x (3 Kat) zoom seçenekleri. Merkez, Sol Üst, Sağ Üst, Sol Alt, Sağ Alt odak bölgeleri.
- **✂️ Zaman Kırpma (Trim):** Başlangıç ve bitiş saniyelerini belirleyerek videonun sadece istenen kısmını çıkarma.
- **🎯 4 Farklı Mod:** Saniye aralığı, toplam adet, kare adımı ve Full FPS (tüm kareler).
- **💎 Sıfır Kalite Kaybı:** Kayıpsız PNG veya yüksek kaliteli JPG (%95). 4K ve 8K çözünürlük desteği.
- **⏱️ Zaman Damgalı İsimlendirme:** Dakika, saniye ve milisaniye bazlı dosya adları.
- **🚀 Kurulumsuz Portable:** Tek dosya `.exe`, Python veya ek yazılım gerektirmez.

---

## 🛠️ Run from Source / Kaynak Koddan Çalıştırma

```bash
# Clone the repository
git clone https://github.com/edizdar/video-to-frames.git
cd video-to-frames

# Install dependencies
pip install -r requirements.txt

# Run
python gui.py
```

### Build Standalone Executables / Yeniden Derleme:
```bash
# Build English edition
pyinstaller --onefile --noconsole --name "VideoToFrames" --clean gui.py

# Build Turkish edition
pyinstaller --onefile --noconsole --name "VideoKareYakalayici" --clean gui.py
```

---

## 👤 Author & Contact / Geliştirici

* **Author:** Erol Dizdar
* **Website:** [https://www.eroldizdar.tr/](https://www.eroldizdar.tr/)
* **Project Page:** [https://www.eroldizdar.tr/p/video-to-frames.html](https://www.eroldizdar.tr/p/video-to-frames.html)

Licensed under the [MIT License](LICENSE).
