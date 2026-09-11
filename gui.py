import os
import sys
import argparse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QRadioButton, QButtonGroup,
    QDoubleSpinBox, QSpinBox, QProgressBar, QGroupBox, QLineEdit,
    QComboBox, QMessageBox, QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent

from extractor import get_video_info, extract_frames

TRANSLATIONS = {
    "tr": {
        "title": "Video Kare Yakalayıcı - Video to Frames",
        "drop_hint": "🎬 Videoyu buraya sürükleyip bırakın\nveya aşağıdaki butondan seçin",
        "browse_video": "📁 Video Dosyası Seç",
        "video_selected": "Seçilen Video: Henüz video seçilmedi",
        "output_group": "Kayıt Klasörü",
        "output_placeholder": "Fotoğrafların kaydedileceği klasör...",
        "browse_output": "Gözat...",
        "mode_group": "Kare Alma Modu",
        "mode_sec": "Belirli saniye aralığıyla al:",
        "unit_sec": "saniye",
        "hint_sec": "(Önerilen: 1.0 sn)",
        "mode_total": "Tüm videodan eşit aralıklarla:",
        "unit_total": "adet fotoğraf",
        "hint_total": "(Tüm videoya yayılır)",
        "mode_frames": "Belirli kare adımıyla:",
        "unit_frames": "karede bir",
        "hint_frames": "(Örn: Her 30 kare)",
        "mode_every": "Tüm kareleri al (Full FPS - Her tekil kare)",
        "format_group": "Fotoğraf Formatı ve Kalite",
        "format_label": "Format:",
        "format_jpg": "JPG (Hızlı ve hafif)",
        "format_png": "PNG (Kayıpsız / Orijinal piksel)",
        "quality_label": "JPG Kalitesi (%):",
        "status_ready": "Hazır. Videonuzu seçip başlayabilirsiniz.",
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
        "unit_sec": "seconds",
        "hint_sec": "(Recommended: 1.0s)",
        "mode_total": "Evenly spread across video:",
        "unit_total": "total photos",
        "hint_total": "(Spread start to end)",
        "mode_frames": "Extract every frame step:",
        "unit_frames": "frames",
        "hint_frames": "(e.g. every 30th frame)",
        "mode_every": "Extract every frame (Full FPS - All frames)",
        "format_group": "Photo Format & Quality",
        "format_label": "Format:",
        "format_jpg": "JPG (Fast & compact size)",
        "format_png": "PNG (100% Lossless quality)",
        "quality_label": "JPG Quality (%):",
        "status_ready": "Ready. Load a video to start.",
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

    def __init__(self, video_path, output_dir, mode, interval, img_format, quality):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.mode = mode
        self.interval = interval
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
        self.resize(760, 680)
        self.setMinimumSize(660, 520)
        self.setAcceptDrops(True)
        self.video_path = ""
        self.video_info = None
        self.worker = None

        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.apply_stylesheet()
        self.init_ui(base_dir)
        self.update_language(self.current_lang)

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["tr"]).get(key, key)

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
                color: #F1F5F9;
            }
            QWidget {
                color: #F1F5F9;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QGroupBox {
                border: 1px solid #334155;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                background-color: #1E293B;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #38BDF8;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #0F172A;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 4px 10px;
                color: #F8FAFC;
                min-height: 28px;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #0F172A;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 2px 6px;
                color: #38BDF8;
                font-weight: bold;
                font-size: 13px;
                min-height: 28px;
                max-height: 32px;
            }
            QComboBox {
                background-color: #0F172A;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 4px 10px;
                color: #F8FAFC;
                min-height: 28px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #38BDF8;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 600;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #3B82F6;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
            QPushButton#action_btn {
                background-color: #0D9488;
                font-size: 14px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton#action_btn:hover {
                background-color: #14B8A6;
            }
            QPushButton#cancel_btn {
                background-color: #DC2626;
                font-size: 14px;
                padding: 8px 18px;
            }
            QPushButton#cancel_btn:hover {
                background-color: #EF4444;
            }
            QProgressBar {
                border: 1px solid #334155;
                border-radius: 6px;
                background-color: #0F172A;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                height: 22px;
            }
            QProgressBar::chunk {
                background-color: #0284C7;
                border-radius: 5px;
            }
            QRadioButton {
                spacing: 8px;
                font-weight: 500;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:checked {
                background-color: #38BDF8;
                border: 3px solid #0F172A;
                outline: 1px solid #38BDF8;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #1E293B;
                border: 2px solid #64748B;
                border-radius: 8px;
            }
            QFrame#drop_area {
                border: 2px dashed #475569;
                border-radius: 10px;
                background-color: #1E293B;
            }
            QFrame#drop_area:hover {
                border-color: #38BDF8;
                background-color: #24344D;
            }
        """)

    def init_ui(self, base_dir):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(18, 12, 18, 14)
        main_layout.setSpacing(10)

        # Header Bar: Logo + App Title + Website Link + Language
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        logo_path = os.path.join(base_dir, "logo.png")
        self.logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        header_layout.addWidget(self.logo_label)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self.header_title = QLabel("Video to Frames / Video Kare Yakalayıcı")
        self.header_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        title_box.addWidget(self.header_title)

        self.dev_link = QLabel("<a href='https://www.eroldizdar.tr/p/video-to-frames.html' style='color: #38BDF8; text-decoration: none; font-size: 12px;'>🌐 eroldizdar.tr</a>")
        self.dev_link.setOpenExternalLinks(True)
        title_box.addWidget(self.dev_link)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🇹🇷 Türkçe", "tr")
        self.lang_combo.addItem("🇬🇧 English", "en")
        if self.current_lang == "en":
            self.lang_combo.setCurrentIndex(1)
        self.lang_combo.currentIndexChanged.connect(self.on_lang_changed)
        header_layout.addWidget(self.lang_combo)

        main_layout.addLayout(header_layout)

        # 1. Video Seçim Alanı (Drag & Drop)
        self.drop_area = QFrame()
        self.drop_area.setObjectName("drop_area")
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setContentsMargins(12, 12, 12, 12)
        drop_layout.setAlignment(Qt.AlignCenter)

        self.drop_label = QLabel()
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #E2E8F0;")
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
        self.video_info_label.setStyleSheet("color: #94A3B8; font-size: 12px; margin-left: 2px;")
        main_layout.addWidget(self.video_info_label)

        # 2. Çıktı Klasörü Grubu
        self.output_group = QGroupBox()
        output_layout = QHBoxLayout(self.output_group)
        output_layout.setContentsMargins(12, 8, 12, 8)
        self.output_edit = QLineEdit()
        output_layout.addWidget(self.output_edit)

        self.browse_output_btn = QPushButton()
        self.browse_output_btn.clicked.connect(self.choose_output_dialog)
        output_layout.addWidget(self.browse_output_btn)
        main_layout.addWidget(self.output_group)

        # 3. Kare Alma Modu Grubu (QGridLayout İLE ASLA ÇAKIŞMAZ VE TAŞMAZ)
        self.mode_group = QGroupBox()
        grid = QGridLayout(self.mode_group)
        grid.setContentsMargins(14, 12, 14, 12)
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(10)

        self.btn_group = QButtonGroup(self)

        # Satır 0: Saniye Aralığı
        self.radio_sec = QRadioButton()
        self.radio_sec.setChecked(True)
        self.btn_group.addButton(self.radio_sec)
        grid.addWidget(self.radio_sec, 0, 0, Qt.AlignVCenter)

        self.spin_sec = QDoubleSpinBox()
        self.spin_sec.setRange(0.05, 3600.0)
        self.spin_sec.setSingleStep(0.5)
        self.spin_sec.setValue(1.0)
        self.spin_sec.setAlignment(Qt.AlignCenter)
        self.spin_sec.setFixedWidth(85)
        grid.addWidget(self.spin_sec, 0, 1, Qt.AlignVCenter)

        self.lbl_unit_sec = QLabel()
        self.lbl_unit_sec.setStyleSheet("font-weight: 500; color: #F1F5F9;")
        grid.addWidget(self.lbl_unit_sec, 0, 2, Qt.AlignVCenter)

        self.lbl_hint_sec = QLabel()
        self.lbl_hint_sec.setStyleSheet("color: #94A3B8; font-size: 12px;")
        grid.addWidget(self.lbl_hint_sec, 0, 3, Qt.AlignVCenter)

        # Satır 1: Toplam Kare Sayısı
        self.radio_total = QRadioButton()
        self.btn_group.addButton(self.radio_total)
        grid.addWidget(self.radio_total, 1, 0, Qt.AlignVCenter)

        self.spin_total = QSpinBox()
        self.spin_total.setRange(1, 100000)
        self.spin_total.setValue(50)
        self.spin_total.setAlignment(Qt.AlignCenter)
        self.spin_total.setFixedWidth(85)
        grid.addWidget(self.spin_total, 1, 1, Qt.AlignVCenter)

        self.lbl_unit_total = QLabel()
        self.lbl_unit_total.setStyleSheet("font-weight: 500; color: #F1F5F9;")
        grid.addWidget(self.lbl_unit_total, 1, 2, Qt.AlignVCenter)

        self.lbl_hint_total = QLabel()
        self.lbl_hint_total.setStyleSheet("color: #94A3B8; font-size: 12px;")
        grid.addWidget(self.lbl_hint_total, 1, 3, Qt.AlignVCenter)

        # Satır 2: Her X Karede Bir
        self.radio_interval_frames = QRadioButton()
        self.btn_group.addButton(self.radio_interval_frames)
        grid.addWidget(self.radio_interval_frames, 2, 0, Qt.AlignVCenter)

        self.spin_interval_frames = QSpinBox()
        self.spin_interval_frames.setRange(1, 5000)
        self.spin_interval_frames.setValue(30)
        self.spin_interval_frames.setAlignment(Qt.AlignCenter)
        self.spin_interval_frames.setFixedWidth(85)
        grid.addWidget(self.spin_interval_frames, 2, 1, Qt.AlignVCenter)

        self.lbl_unit_frames = QLabel()
        self.lbl_unit_frames.setStyleSheet("font-weight: 500; color: #F1F5F9;")
        grid.addWidget(self.lbl_unit_frames, 2, 2, Qt.AlignVCenter)

        self.lbl_hint_frames = QLabel()
        self.lbl_hint_frames.setStyleSheet("color: #94A3B8; font-size: 12px;")
        grid.addWidget(self.lbl_hint_frames, 2, 3, Qt.AlignVCenter)

        # Satır 3: Tüm Kareleri Al
        self.radio_every = QRadioButton()
        self.btn_group.addButton(self.radio_every)
        grid.addWidget(self.radio_every, 3, 0, 1, 4, Qt.AlignVCenter)

        grid.setColumnStretch(4, 1)
        main_layout.addWidget(self.mode_group)

        # 4. Format ve Kalite Ayarları
        self.fmt_group = QGroupBox()
        fmt_layout = QHBoxLayout(self.fmt_group)
        fmt_layout.setContentsMargins(14, 10, 14, 10)

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
        self.spin_qual.setAlignment(Qt.AlignCenter)
        self.spin_qual.setFixedWidth(75)
        fmt_layout.addWidget(self.spin_qual)
        fmt_layout.addStretch()

        main_layout.addWidget(self.fmt_group)

        # 5. İlerleme ve Durum
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #94A3B8; font-style: italic;")
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

        scroll_area.setWidget(container)
        self.setCentralWidget(scroll_area)

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
        self.lbl_unit_sec.setText(self.t("unit_sec"))
        self.lbl_hint_sec.setText(self.t("hint_sec"))

        self.radio_total.setText(self.t("mode_total"))
        self.lbl_unit_total.setText(self.t("unit_total"))
        self.lbl_hint_total.setText(self.t("hint_total"))

        self.radio_interval_frames.setText(self.t("mode_frames"))
        self.lbl_unit_frames.setText(self.t("unit_frames"))
        self.lbl_hint_frames.setText(self.t("hint_frames"))

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
