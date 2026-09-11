import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QRadioButton, QButtonGroup,
    QDoubleSpinBox, QSpinBox, QProgressBar, QGroupBox, QLineEdit,
    QComboBox, QMessageBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent

from extractor import get_video_info, extract_frames

class ExtractionWorker(QThread):
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(int)
    error_signal = Signal(str)

    def __init__(self, video_path, output_dir, mode, interval, start_sec, end_sec, img_format, quality):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.mode = mode
        self.interval = interval
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.img_format = img_format
        self.quality = quality
        self.is_cancelled = False

    def run(self):
        try:
            def callback(saved, total, filename):
                if self.is_cancelled:
                    return False
                self.progress_signal.emit(saved, total, filename)
                return True

            count = extract_frames(
                video_path=self.video_path,
                output_dir=self.output_dir,
                mode=self.mode,
                interval_value=self.interval,
                start_sec=self.start_sec,
                end_sec=self.end_sec,
                image_format=self.img_format,
                quality=self.quality,
                progress_callback=callback
            )
            self.finished_signal.emit(count)
        except Exception as e:
            self.error_signal.emit(str(e))

    def cancel(self):
        self.is_cancelled = True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Kare Yakalayıcı - Video to Photos")
        self.setMinimumSize(720, 680)
        self.setAcceptDrops(True)
        self.video_path = ""
        self.video_info = None
        self.worker = None

        self.apply_stylesheet()
        self.init_ui()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121824;
                color: #E2E8F0;
            }
            QWidget {
                color: #E2E8F0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #2D3748;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 14px;
                background-color: #1A202C;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
                color: #63B3ED;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #2D3748;
                border: 1px solid #4A5568;
                border-radius: 6px;
                padding: 6px 10px;
                color: #FFFFFF;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #3182CE;
            }
            QPushButton {
                background-color: #2B6CB0;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3182CE;
            }
            QPushButton:pressed {
                background-color: #2C5282;
            }
            QPushButton:disabled {
                background-color: #4A5568;
                color: #A0AEC0;
            }
            QPushButton#action_btn {
                background-color: #319795;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton#action_btn:hover {
                background-color: #38B2AC;
            }
            QPushButton#cancel_btn {
                background-color: #E53E3E;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton#cancel_btn:hover {
                background-color: #F56565;
            }
            QProgressBar {
                border: 1px solid #2D3748;
                border-radius: 6px;
                background-color: #1A202C;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                height: 22px;
            }
            QProgressBar::chunk {
                background-color: #3182CE;
                border-radius: 5px;
            }
            QRadioButton {
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:checked {
                background-color: #3182CE;
                border: 2px solid #FFFFFF;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #2D3748;
                border: 2px solid #718096;
                border-radius: 8px;
            }
            QFrame#drop_area {
                border: 2px dashed #4A5568;
                border-radius: 10px;
                background-color: #171F2E;
            }
            QFrame#drop_area:hover {
                border-color: #63B3ED;
                background-color: #1C2638;
            }
        """)

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # 1. Video Seçim Alanı (Sürükle - Bırak kutusu)
        self.drop_area = QFrame()
        self.drop_area.setObjectName("drop_area")
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setContentsMargins(15, 15, 15, 15)
        drop_layout.setAlignment(Qt.AlignCenter)

        self.drop_label = QLabel("🎬 Videoyu buraya sürükleyip bırakın\nveya aşağıdaki butondan seçin")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CBD5E0;")
        drop_layout.addWidget(self.drop_label)

        btn_hlayout = QHBoxLayout()
        btn_hlayout.setAlignment(Qt.AlignCenter)
        self.browse_video_btn = QPushButton("📁 Video Dosyası Seç")
        self.browse_video_btn.clicked.connect(self.choose_video_dialog)
        btn_hlayout.addWidget(self.browse_video_btn)
        drop_layout.addLayout(btn_hlayout)

        main_layout.addWidget(self.drop_area)

        # Video Bilgi Etiketi
        self.video_info_label = QLabel("Seçilen Video: Henüz video seçilmedi")
        self.video_info_label.setStyleSheet("color: #A0AEC0; font-size: 12px; margin-left: 2px;")
        main_layout.addWidget(self.video_info_label)

        # 2. Çıktı Klasörü Grubu
        output_group = QGroupBox("Kayıt Klasörü")
        output_layout = QHBoxLayout(output_group)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Fotoğrafların kaydedileceği klasör...")
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = QPushButton("Gözat...")
        self.browse_output_btn.clicked.connect(self.choose_output_dialog)
        output_layout.addWidget(self.browse_output_btn)
        main_layout.addWidget(output_group)

        # 3. Kare Alma Modu Grubu
        mode_group = QGroupBox("Kare Alma Modu")
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(10)

        self.btn_group = QButtonGroup(self)

        # Mod 1: Saniye aralığı
        row1 = QHBoxLayout()
        self.radio_sec = QRadioButton("Belirli saniye aralığıyla al:")
        self.radio_sec.setChecked(True)
        self.btn_group.addButton(self.radio_sec)
        row1.addWidget(self.radio_sec)

        self.spin_sec = QDoubleSpinBox()
        self.spin_sec.setRange(0.05, 3600.0)
        self.spin_sec.setSingleStep(0.5)
        self.spin_sec.setValue(1.0)
        self.spin_sec.setSuffix(" saniye (Varsayılan: 1 sn)")
        row1.addWidget(self.spin_sec)
        row1.addStretch()
        mode_layout.addLayout(row1)

        # Mod 2: Toplam kare sayısı
        row2 = QHBoxLayout()
        self.radio_total = QRadioButton("Tüm videodan eşit aralıklarla toplam:")
        self.btn_group.addButton(self.radio_total)
        row2.addWidget(self.radio_total)

        self.spin_total = QSpinBox()
        self.spin_total.setRange(1, 100000)
        self.spin_total.setValue(50)
        self.spin_total.setSuffix(" adet fotoğraf al")
        row2.addWidget(self.spin_total)
        row2.addStretch()
        mode_layout.addLayout(row2)

        # Mod 3: Her X karede bir
        row3 = QHBoxLayout()
        self.radio_interval_frames = QRadioButton("Her:")
        self.btn_group.addButton(self.radio_interval_frames)
        row3.addWidget(self.radio_interval_frames)

        self.spin_interval_frames = QSpinBox()
        self.spin_interval_frames.setRange(1, 5000)
        self.spin_interval_frames.setValue(30)
        self.spin_interval_frames.setSuffix(" karede bir al")
        row3.addWidget(self.spin_interval_frames)
        row3.addStretch()
        mode_layout.addLayout(row3)

        # Mod 4: Tüm kareleri al
        row4 = QHBoxLayout()
        self.radio_every = QRadioButton("Tüm kareleri al (Full FPS - Her kare tek tek)")
        self.btn_group.addButton(self.radio_every)
        row4.addWidget(self.radio_every)
        row4.addStretch()
        mode_layout.addLayout(row4)

        main_layout.addWidget(mode_group)

        # 4. Format ve Kalite Ayarları
        fmt_group = QGroupBox("Fotoğraf Formatı ve Kalite")
        fmt_layout = QHBoxLayout(fmt_group)

        fmt_layout.addWidget(QLabel("Format:"))
        self.combo_fmt = QComboBox()
        self.combo_fmt.addItems(["JPG (Küçük boyut, yüksek hız)", "PNG (Kayıpsız / Şeffaflık destekli)"])
        fmt_layout.addWidget(self.combo_fmt)

        fmt_layout.addSpacing(20)
        fmt_layout.addWidget(QLabel("JPG Kalitesi (%):"))
        self.spin_qual = QSpinBox()
        self.spin_qual.setRange(10, 100)
        self.spin_qual.setValue(95)
        fmt_layout.addWidget(self.spin_qual)
        fmt_layout.addStretch()

        main_layout.addWidget(fmt_group)

        # 5. İlerleme ve Durum
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("color: #A0AEC0; font-style: italic;")
        main_layout.addWidget(self.status_label)

        # 6. Kontrol Butonları
        actions_layout = QHBoxLayout()
        self.start_btn = QPushButton("🚀 Fotoğrafları Çıkarmaya Başla")
        self.start_btn.setObjectName("action_btn")
        self.start_btn.clicked.connect(self.start_extraction)
        actions_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("⏹️ Durdur")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_extraction)
        actions_layout.addWidget(self.cancel_btn)

        self.open_folder_btn = QPushButton("📂 Klasörü Aç")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        actions_layout.addWidget(self.open_folder_btn)

        main_layout.addLayout(actions_layout)

        self.setCentralWidget(central_widget)

    # Drag & Drop Desteği
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            if os.path.isfile(filepath):
                self.load_video(filepath)

    def choose_video_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Video Dosyası Seç",
            "",
            "Video Dosyaları (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;Tüm Dosyalar (*.*)"
        )
        if filepath:
            self.load_video(filepath)

    def load_video(self, path):
        try:
            info = get_video_info(path)
            self.video_path = path
            self.video_info = info

            mins = int(info['duration_sec'] // 60)
            secs = int(info['duration_sec'] % 60)
            fname = os.path.basename(path)

            self.drop_label.setText(f"✅ Yüklendi: {fname}")
            self.video_info_label.setText(
                f"Süre: {mins:02d}:{secs:02d} | Çözünürlük: {info['width']}x{info['height']} | "
                f"FPS: {info['fps']:.2f} | Toplam Kare: {info['total_frames']}"
            )

            # Auto suggest output directory
            vdir = os.path.dirname(os.path.abspath(path))
            vstem = os.path.splitext(fname)[0]
            default_out = os.path.join(vdir, f"{vstem}_fotograflar")
            self.output_edit.setText(default_out)
            self.status_label.setText("Video hazır. İstediğiniz modu seçip başlatabilirsiniz.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Video açılamadı:\n{e}")

    def choose_output_dialog(self):
        d = QFileDialog.getExistingDirectory(self, "Fotoğrafların Kaydedileceği Klasör")
        if d:
            self.output_edit.setText(d)

    def start_extraction(self):
        if not self.video_path or not os.path.isfile(self.video_path):
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir video dosyası seçin veya sürükleyin!")
            return

        out_dir = self.output_edit.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir çıktı klasörü belirleyin!")
            return

        mode = "seconds"
        interval = 1.0

        if self.radio_sec.isChecked():
            mode = "seconds"
            interval = self.spin_sec.value()
        elif self.radio_total.isChecked():
            mode = "total_count"
            interval = float(self.spin_total.value())
        elif self.radio_interval_frames.isChecked():
            mode = "interval_frames"
            interval = float(self.spin_interval_frames.value())
        elif self.radio_every.isChecked():
            mode = "every_frame"
            interval = 1.0

        fmt = "jpg" if self.combo_fmt.currentIndex() == 0 else "png"
        qual = self.spin_qual.value()

        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(False)
        self.status_label.setText("Fotoğraflar çıkarılıyor, lütfen bekleyin...")

        self.worker = ExtractionWorker(
            video_path=self.video_path,
            output_dir=out_dir,
            mode=mode,
            interval=interval,
            start_sec=0.0,
            end_sec=None,
            img_format=fmt,
            quality=qual
        )
        self.worker.progress_signal.connect(self.on_progress)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    def on_progress(self, saved, total, current_file):
        pct = int((saved / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(pct)
        self.status_label.setText(f"İşleniyor: {saved} / {total} fotoğraf kaydedildi -> {current_file}")

    def on_finished(self, total_saved):
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Tamamlandı! Toplam {total_saved} adet fotoğraf başarıyla kaydedildi.")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(True)
        
        reply = QMessageBox.information(
            self,
            "İşlem Tamamlandı",
            f"Toplam {total_saved} adet fotoğraf başarıyla kaydedildi!\n\nKlasörü şimdi açmak ister misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self.open_output_folder()

    def on_error(self, err_msg):
        self.status_label.setText(f"Hata oluştu!")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu:\n{err_msg}")

    def cancel_extraction(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.setText("İşlem durduruluyor...")
            self.cancel_btn.setEnabled(False)

    def open_output_folder(self):
        out_dir = self.output_edit.text().strip()
        if os.path.exists(out_dir):
            try:
                os.startfile(out_dir)
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Klasör açılamadı: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
