import os
import sys
import argparse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QRadioButton, QButtonGroup,
    QDoubleSpinBox, QSpinBox, QProgressBar, QGroupBox, QLineEdit,
    QComboBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from extractor import get_video_info, extract_frames

TRANSLATIONS = {
    "tr": {
        "title": "Video Kare Yakalayıcı - Video to Photos",
        "drop_hint": "🎬 Videoyu buraya sürükleyip bırakın\nveya aşağıdaki butondan seçin",
        "browse_video": "📁 Video Dosyası Seç",
        "video_selected": "Seçilen Video: Henüz video seçilmedi",
        "output_group": "Kayıt Klasörü",
        "output_placeholder": "Fotoğrafların kaydedileceği klasör...",
        "browse_output": "Gözat...",
        "mode_group": "Kare Alma Modu",
        "mode_sec": "Belirli saniye aralığıyla al:",
        "sec_suffix": " saniye (Varsayılan: 1 sn)",
        "mode_total": "Tüm videodan eşit aralıklarla toplam:",
        "total_suffix": " adet fotoğraf al",
        "mode_frames": "Her:",
        "frames_suffix": " karede bir al",
        "mode_every": "Tüm kareleri al (Full FPS - Her kare tek tek)",
        "format_group": "Fotoğraf Formatı ve Kalite",
        "format_label": "Format:",
        "format_jpg": "JPG (Küçük boyut, yüksek hız)",
        "format_png": "PNG (Kayıpsız / Yüksek kalite)",
        "quality_label": "JPG Kalitesi (%):",
        "status_ready": "Hazır",
        "btn_start": "🚀 Fotoğrafları Çıkarmaya Başla",
        "btn_cancel": "⏹️ Durdur",
        "btn_open": "📂 Klasörü Aç",
        "dialog_title": "Video Dosyası Seç",
        "dialog_filter": "Video Dosyaları (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;Tüm Dosyalar (*.*)",
        "dialog_out_title": "Fotoğrafların Kaydedileceği Klasör",
        "warn_no_video": "Lütfen önce bir video dosyası seçin veya sürükleyin!",
        "warn_no_dir": "Lütfen bir çıktı klasörü belirleyin!",
        "status_processing": "Fotoğraflar çıkarılıyor, lütfen bekleyin...",
        "status_progress": "İşleniyor: {saved} / {total} fotoğraf kaydedildi -> {file}",
        "status_done": "Tamamlandı! Toplam {total} adet fotoğraf başarıyla kaydedildi.",
        "status_error": "Hata oluştu!",
        "status_stopping": "İşlem durduruluyor...",
        "popup_done_title": "İşlem Tamamlandı",
        "popup_done_msg": "Toplam {total} adet fotoğraf başarıyla kaydedildi!\n\nKlasörü şimdi açmak ister misiniz?",
        "popup_err_folder": "Klasör açılamadı: {err}",
        "video_info_fmt": "Süre: {mins:02d}:{secs:02d} | Çözünürlük: {w}x{h} | FPS: {fps:.2f} | Toplam Kare: {total}",
        "folder_suffix": "_fotograflar"
    },
    "en": {
        "title": "Video to Frames - Extract Photos from Video",
        "drop_hint": "🎬 Drag and drop video here\nor click the button below to browse",
        "browse_video": "📁 Select Video File",
        "video_selected": "Selected Video: No video selected yet",
        "output_group": "Output Folder",
        "output_placeholder": "Folder where photos will be saved...",
        "browse_output": "Browse...",
        "mode_group": "Frame Extraction Mode",
        "mode_sec": "Extract every specified seconds:",
        "sec_suffix": " seconds (Default: 1s)",
        "mode_total": "Evenly spread across video, total:",
        "total_suffix": " photos",
        "mode_frames": "Every:",
        "frames_suffix": " frames",
        "mode_every": "Extract every frame (Full FPS - All frames)",
        "format_group": "Photo Format & Quality",
        "format_label": "Format:",
        "format_jpg": "JPG (Compact size, high speed)",
        "format_png": "PNG (Lossless / High quality)",
        "quality_label": "JPG Quality (%):",
        "status_ready": "Ready",
        "btn_start": "🚀 Start Extracting Frames",
        "btn_cancel": "⏹️ Stop",
        "btn_open": "📂 Open Folder",
        "dialog_title": "Select Video File",
        "dialog_filter": "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;All Files (*.*)",
        "dialog_out_title": "Select Output Folder",
        "warn_no_video": "Please select or drag & drop a video file first!",
        "warn_no_dir": "Please specify an output folder!",
        "status_processing": "Extracting frames, please wait...",
        "status_progress": "Processing: {saved} / {total} photos saved -> {file}",
        "status_done": "Completed! Successfully saved {total} photos.",
        "status_error": "An error occurred!",
        "status_stopping": "Stopping extraction...",
        "popup_done_title": "Extraction Completed",
        "popup_done_msg": "Successfully saved {total} photos!\n\nWould you like to open the output folder now?",
        "popup_err_folder": "Could not open folder: {err}",
        "video_info_fmt": "Duration: {mins:02d}:{secs:02d} | Resolution: {w}x{h} | FPS: {fps:.2f} | Total Frames: {total}",
        "folder_suffix": "_frames"
    }
}

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
    def __init__(self, default_lang="tr"):
        super().__init__()
        self.current_lang = default_lang
        self.setMinimumSize(740, 700)
        self.setAcceptDrops(True)
        self.video_path = ""
        self.video_info = None
        self.worker = None

        self.apply_stylesheet()
        self.init_ui()
        self.update_language(self.current_lang)

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["tr"]).get(key, key)

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
        main_layout.setContentsMargins(20, 16, 20, 20)
        main_layout.setSpacing(12)

        # Header Bar: Dil Değiştirici & Geliştirici Linki
        top_bar = QHBoxLayout()
        self.dev_label = QLabel("<a href='https://www.eroldizdar.tr/' style='color: #63B3ED; text-decoration: none;'>🌐 eroldizdar.tr</a>")
        self.dev_label.setOpenExternalLinks(True)
        top_bar.addWidget(self.dev_label)
        top_bar.addStretch()

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🇹🇷 Türkçe", "tr")
        self.lang_combo.addItem("🇬🇧 English", "en")
        if self.current_lang == "en":
            self.lang_combo.setCurrentIndex(1)
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)
        top_bar.addWidget(self.lang_combo)
        main_layout.addLayout(top_bar)

        # 1. Video Seçim Alanı
        self.drop_area = QFrame()
        self.drop_area.setObjectName("drop_area")
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setContentsMargins(15, 15, 15, 15)
        drop_layout.setAlignment(Qt.AlignCenter)

        self.drop_label = QLabel()
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #CBD5E0;")
        drop_layout.addWidget(self.drop_label)

        btn_hlayout = QHBoxLayout()
        btn_hlayout.setAlignment(Qt.AlignCenter)
        self.browse_video_btn = QPushButton()
        self.browse_video_btn.clicked.connect(self.choose_video_dialog)
        btn_hlayout.addWidget(self.browse_video_btn)
        drop_layout.addLayout(btn_hlayout)

        main_layout.addWidget(self.drop_area)

        # Video Bilgi Etiketi
        self.video_info_label = QLabel()
        self.video_info_label.setStyleSheet("color: #A0AEC0; font-size: 12px; margin-left: 2px;")
        main_layout.addWidget(self.video_info_label)

        # 2. Çıktı Klasörü Grubu
        self.output_group = QGroupBox()
        output_layout = QHBoxLayout(self.output_group)
        self.output_edit = QLineEdit()
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = QPushButton()
        self.browse_output_btn.clicked.connect(self.choose_output_dialog)
        output_layout.addWidget(self.browse_output_btn)
        main_layout.addWidget(self.output_group)

        # 3. Kare Alma Modu Grubu
        self.mode_group = QGroupBox()
        mode_layout = QVBoxLayout(self.mode_group)
        mode_layout.setSpacing(10)

        self.btn_group = QButtonGroup(self)

        row1 = QHBoxLayout()
        self.radio_sec = QRadioButton()
        self.radio_sec.setChecked(True)
        self.btn_group.addButton(self.radio_sec)
        row1.addWidget(self.radio_sec)

        self.spin_sec = QDoubleSpinBox()
        self.spin_sec.setRange(0.05, 3600.0)
        self.spin_sec.setSingleStep(0.5)
        self.spin_sec.setValue(1.0)
        row1.addWidget(self.spin_sec)
        row1.addStretch()
        mode_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.radio_total = QRadioButton()
        self.btn_group.addButton(self.radio_total)
        row2.addWidget(self.radio_total)

        self.spin_total = QSpinBox()
        self.spin_total.setRange(1, 100000)
        self.spin_total.setValue(50)
        row2.addWidget(self.spin_total)
        row2.addStretch()
        mode_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.radio_interval_frames = QRadioButton()
        self.btn_group.addButton(self.radio_interval_frames)
        row3.addWidget(self.radio_interval_frames)

        self.spin_interval_frames = QSpinBox()
        self.spin_interval_frames.setRange(1, 5000)
        self.spin_interval_frames.setValue(30)
        row3.addWidget(self.spin_interval_frames)
        row3.addStretch()
        mode_layout.addLayout(row3)

        row4 = QHBoxLayout()
        self.radio_every = QRadioButton()
        self.btn_group.addButton(self.radio_every)
        row4.addWidget(self.radio_every)
        row4.addStretch()
        mode_layout.addLayout(row4)

        main_layout.addWidget(self.mode_group)

        # 4. Format ve Kalite Ayarları
        self.fmt_group = QGroupBox()
        fmt_layout = QHBoxLayout(self.fmt_group)

        self.lbl_format = QLabel()
        fmt_layout.addWidget(self.lbl_format)
        self.combo_fmt = QComboBox()
        fmt_layout.addWidget(self.combo_fmt)

        fmt_layout.addSpacing(20)
        self.lbl_quality = QLabel()
        fmt_layout.addWidget(self.lbl_quality)
        self.spin_qual = QSpinBox()
        self.spin_qual.setRange(10, 100)
        self.spin_qual.setValue(95)
        fmt_layout.addWidget(self.spin_qual)
        fmt_layout.addStretch()

        main_layout.addWidget(self.fmt_group)

        # 5. İlerleme ve Durum
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #A0AEC0; font-style: italic;")
        main_layout.addWidget(self.status_label)

        # 6. Kontrol Butonları
        actions_layout = QHBoxLayout()
        self.start_btn = QPushButton()
        self.start_btn.setObjectName("action_btn")
        self.start_btn.clicked.connect(self.start_extraction)
        actions_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_extraction)
        actions_layout.addWidget(self.cancel_btn)

        self.open_folder_btn = QPushButton()
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        actions_layout.addWidget(self.open_folder_btn)

        main_layout.addLayout(actions_layout)
        self.setCentralWidget(central_widget)

    def on_lang_changed(self, index):
        code = self.lang_combo.currentData()
        self.update_language(code)

    def update_language(self, lang_code):
        self.current_lang = lang_code
        self.setWindowTitle(self.t("title"))

        if not self.video_path:
            self.drop_label.setText(self.t("drop_hint"))
            self.video_info_label.setText(self.t("video_selected"))
            self.status_label.setText(self.t("status_ready"))
        else:
            self.update_video_info_text()

        self.browse_video_btn.setText(self.t("browse_video"))
        self.output_group.setTitle(self.t("output_group"))
        self.output_edit.setPlaceholderText(self.t("output_placeholder"))
        self.browse_output_btn.setText(self.t("browse_output"))
        self.mode_group.setTitle(self.t("mode_group"))
        self.radio_sec.setText(self.t("mode_sec"))
        self.spin_sec.setSuffix(self.t("sec_suffix"))
        self.radio_total.setText(self.t("mode_total"))
        self.spin_total.setSuffix(self.t("total_suffix"))
        self.radio_interval_frames.setText(self.t("mode_frames"))
        self.spin_interval_frames.setSuffix(self.t("frames_suffix"))
        self.radio_every.setText(self.t("mode_every"))
        self.fmt_group.setTitle(self.t("format_group"))
        self.lbl_format.setText(self.t("format_label"))

        cur_fmt_idx = self.combo_fmt.currentIndex()
        self.combo_fmt.clear()
        self.combo_fmt.addItems([self.t("format_jpg"), self.t("format_png")])
        if cur_fmt_idx >= 0:
            self.combo_fmt.setCurrentIndex(cur_fmt_idx)

        self.lbl_quality.setText(self.t("quality_label"))
        self.start_btn.setText(self.t("btn_start"))
        self.cancel_btn.setText(self.t("btn_cancel"))
        self.open_folder_btn.setText(self.t("btn_open"))

    def update_video_info_text(self):
        if not self.video_info:
            return
        info = self.video_info
        mins = int(info['duration_sec'] // 60)
        secs = int(info['duration_sec'] % 60)
        self.video_info_label.setText(
            self.t("video_info_fmt").format(
                mins=mins, secs=secs, w=info['width'], h=info['height'],
                fps=info['fps'], total=info['total_frames']
            )
        )

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
            self.t("dialog_title"),
            "",
            self.t("dialog_filter")
        )
        if filepath:
            self.load_video(filepath)

    def load_video(self, path):
        try:
            info = get_video_info(path)
            self.video_path = path
            self.video_info = info

            fname = os.path.basename(path)
            self.drop_label.setText(f"✅ {fname}")
            self.update_video_info_text()

            vdir = os.path.dirname(os.path.abspath(path))
            vstem = os.path.splitext(fname)[0]
            default_out = os.path.join(vdir, f"{vstem}{self.t('folder_suffix')}")
            self.output_edit.setText(default_out)
            self.status_label.setText(self.t("status_ready"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{e}")

    def choose_output_dialog(self):
        d = QFileDialog.getExistingDirectory(self, self.t("dialog_out_title"))
        if d:
            self.output_edit.setText(d)

    def start_extraction(self):
        if not self.video_path or not os.path.isfile(self.video_path):
            QMessageBox.warning(self, "Warning", self.t("warn_no_video"))
            return

        out_dir = self.output_edit.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "Warning", self.t("warn_no_dir"))
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
        self.status_label.setText(self.t("status_processing"))

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
        self.status_label.setText(self.t("status_progress").format(saved=saved, total=total, file=current_file))

    def on_finished(self, total_saved):
        self.progress_bar.setValue(100)
        self.status_label.setText(self.t("status_done").format(total=total_saved))
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(True)
        
        reply = QMessageBox.information(
            self,
            self.t("popup_done_title"),
            self.t("popup_done_msg").format(total=total_saved),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self.open_output_folder()

    def on_error(self, err_msg):
        self.status_label.setText(self.t("status_error"))
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.critical(self, "Error", f"{err_msg}")

    def cancel_extraction(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.setText(self.t("status_stopping"))
            self.cancel_btn.setEnabled(False)

    def open_output_folder(self):
        out_dir = self.output_edit.text().strip()
        if os.path.exists(out_dir):
            try:
                os.startfile(out_dir)
            except Exception as e:
                QMessageBox.warning(self, "Error", self.t("popup_err_folder").format(err=e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["tr", "en"], default="tr", help="Default language")
    args, unknown = parser.parse_known_args()

    # If filename contains 'en' or 'VideoToFrames', default to English
    prog_name = os.path.basename(sys.argv[0]).lower()
    default_lang = args.lang
    if "en" in prog_name or "videotoframes" in prog_name:
        default_lang = "en"

    app = QApplication(sys.argv)
    window = MainWindow(default_lang=default_lang)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
