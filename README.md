# 🎬 Video Kare Yakalayıcı (Video to Frames)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6" />
  <img src="https://img.shields.io/badge/Engine-OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Platform-Windows%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>Videolardan yüksek çözünürlüklü fotoğraflar ve kareler çıkarmak için geliştirilmiş ücretsiz, açık kaynaklı ve kurulum gerektirmeyen (portable) masaüstü aracı.</b><br>
  <i>Developed by <a href="https://www.eroldizdar.tr/">Erol Dizdar</a></i>
</p>

---

## ✨ Özellikler

- **🚀 Kurulum Gerektirmez (Portable):** Python veya harici bir kütüphane kurmanıza gerek yoktur. `.exe` dosyasını çift tıklayarak doğrudan çalıştırabilirsiniz.
- **🎯 4 Farklı Kare Alma Modu:**
  1. **Saniye Aralığıyla:** Belirlediğiniz saniyede bir (örn. her 1 saniyede veya 0.5 saniyede 1 kare).
  2. **Eşit Aralıklı Toplam Fotoğraf:** Videonun başından sonuna eşit aralıklarla belirlediğiniz toplam adet (örn. 50 fotoğraf).
  3. **Kare Sayısı Aralığıyla:** Her X karede bir yakalama (örn. her 30 karede bir).
  4. **Tüm Kareler (Full FPS):** Videodaki istisnasız her bir tekil kareyi kaydeder.
- **💎 Sıfır Kalite Kaybı:**
  - **PNG:** %100 kayıpsız (lossless) format desteği.
  - **JPG:** Ayarlanabilir sıkıştırma kalitesi (%10 - %100, varsayılan %95).
  - Video hangi çözünürlükteyse (1080p, 2K, 4K) fotoğraflar da aynı çözünürlükte kaydedilir.
- **🖱️ Sürükle ve Bırak Desteği:** Video dosyasını doğrudan program penceresine sürükleyip bırakmanız yeterlidir.
- **⏱️ Zaman Damgalı İsimlendirme:** Çıkarılan her kare `kare_00001_01m24s_350ms.jpg` formatında dakikası, saniyesi ve milisaniyesiyle adlandırılır.
- **⚡ Arka Planda Hızlı İşleme:** Çok çekirdekli iş parçacığı (QThread) sayesinde işlem yaparken program arayüzü asla donmaz.

---

## 📥 İndirme

Programın derlenmiş, kuruluma ihtiyaç duymayan taşınabilir sürümünü doğrudan indirebilirsiniz:

- 🌐 **Web Sitesi:** [eroldizdar.tr](https://www.eroldizdar.tr/)
- 📦 **GitHub Releases:** [Releases Sayfasından İndir](../../releases)

---

## 🖥️ Kullanım

### Seçenek 1: Görsel Program Arayüzü (GUI)
1. `VideoKareYakalayici.exe` (veya `programi_baslat.bat`) dosyasını açın.
2. Videonuzu pencereye sürükleyin veya **"Video Dosyası Seç"** butonuna basın.
3. Çıkarmak istediğiniz modu ve formatı seçip **"Fotoğrafları Çıkarmaya Başla"** butonuna tıklayın.
4. İşlem bitince açılan bildirimden doğrudan fotoğrafların olduğu klasöre gidebilirsiniz.

### Seçenek 2: Sürükle-Bırak (.BAT)
1. Herhangi bir video dosyasını tutup `surukle_birak.bat` dosyasının üzerine bırakın.
2. Hızlı konsol ekranı üzerinden dilediğiniz ayarla anında fotoğrafları çıkarın.

---

## 🛠️ Kaynak Koddan Çalıştırma ve Geliştirme

Projeyi kaynak koddan çalıştırmak veya kendi ihtiyaçlarınıza göre düzenlemek isterseniz:

```bash
# Depoyu klonlayın
git clone https://github.com/edizdar/video-to-frames.git
cd video-to-frames

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Grafik arayüzü başlatın
python gui.py

# Veya komut satırı arayüzü ile çalıştırın
python cli.py "videonuz.mp4"
```

### Tekrar Portable EXE Derleme:
```bash
pyinstaller --onefile --noconsole --name "VideoKareYakalayici" --clean gui.py
```

---

## 👤 Geliştirici & İletişim

* **Geliştirici:** Erol Dizdar
* **Web Sitesi:** [https://www.eroldizdar.tr/](https://www.eroldizdar.tr/)

Projeyi beğendiyseniz GitHub üzerinde bir yıldız (⭐) vermeyi unutmayın!

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Dilediğiniz gibi ticari veya kişisel projelerinizde kullanabilir ve geliştirebilirsiniz.
