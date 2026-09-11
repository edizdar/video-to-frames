# 🎬 Video to Frames / Video Kare Yakalayıcı

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6" />
  <img src="https://img.shields.io/badge/Engine-OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Platform-Windows%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>Extract high-resolution photos and frames from videos with zero quality loss. Free, open-source, and portable tool.</b><br>
  <i>Videolardan yüksek çözünürlüklü fotoğraflar ve kareler çıkarmak için geliştirilmiş ücretsiz, açık kaynaklı ve kurulum gerektirmeyen (portable) masaüstü aracı.</i><br>
  Developed by <a href="https://www.eroldizdar.tr/"><b>Erol Dizdar</b></a>
</p>

---

## 🌐 Official Website & Downloads / Resmi Web Sayfası ve İndirme

All downloads, setup guides, and portable packages are available on the official website:
Tüm indirme seçenekleri, taşınabilir (portable) sürümler ve rehber resmi web sayfasında yer almaktadır:

👉 **[Download Video to Frames / Programı İndir (eroldizdar.tr)](https://www.eroldizdar.tr/p/video-to-frames.html)**

---

## ✨ Features / Özellikler

### 🇬🇧 English
- **🚀 No Installation Required (Portable):** Fully standalone single-file `.exe`. No Python or codecs needed.
- **🎯 4 Extraction Modes:**
  1. *Time Interval:* Capture a frame every $X$ seconds (e.g. every 1s or 0.5s).
  2. *Total Count:* Evenly spread across video duration (e.g. exactly 50 frames).
  3. *Frame Step:* Capture every $N$ frames (e.g. every 30th frame).
  4. *Full FPS:* Export every single individual frame.
- **💎 Zero Quality Loss:**
  - *PNG:* 100% Lossless.
  - *JPG:* High quality with adjustable compression slider (defaults to 95%).
  - Maintains native video resolution (1080p, 2K, 4K).
- **🖱️ Drag & Drop:** Drag any video file directly into the application window.
- **⏱️ Timestamped Filenames:** Each image is named with exact time (e.g., `frame_00001_01m24s_350ms.jpg`).
- **🌐 Bilingual UI:** Switch between English (🇬🇧) and Turkish (🇹🇷) with a single click.

### 🇹🇷 Türkçe
- **🚀 Kurulum Gerektirmez (Portable):** Bağımsız tek dosya `.exe`. Python veya harici kütüphane gerektirmez.
- **🎯 4 Farklı Kare Alma Modu:** Saniye aralığı, eşit aralıklı toplam adet, kare sayısı aralığı ve tüm kareler (Full FPS).
- **💎 Sıfır Kalite Kaybı:** Kayıpsız PNG ve yüksek kaliteli ayarlanabilir JPG (%95). Orijinal çözünürlük korunur.
- **🖱️ Sürükle ve Bırak Desteği:** Videoyu pencereye bırakmanız yeterli.
- **⏱️ Zaman Damgalı İsimlendirme:** Dakika, saniye ve milisaniye bazlı dosya adları.
- **🌐 Çift Dil Desteği:** Türkçe ve İngilizce dilleri arasında tek tıkla geçiş.

---

## 🛠️ Run from Source / Kaynak Koddan Çalıştırma

```bash
# Clone the repository
git clone https://github.com/edizdar/video-to-frames.git
cd video-to-frames

# Install dependencies
pip install -r requirements.txt

# Run in English
python gui.py --lang en

# Run in Turkish
python gui.py --lang tr
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
