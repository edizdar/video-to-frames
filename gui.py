import os
import sys
import argparse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QRadioButton, QButtonGroup,
    QDoubleSpinBox, QSpinBox, QProgressBar, QGroupBox, QLineEdit,
    QComboBox, QMessageBox, QFrame, QListWidget, QListWidgetItem,
    QTabWidget, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from extractor import get_video_info, extract_frames

TRANSLATIONS = {
    "tr": {
        "title": "Video Kare Yakalayıcı - Video to Frames Pro",
        "playlist_title": "📋 Video Listesi / Oynatma Listesi",
        "btn_add_videos": "➕ Video(lar) Ekle",
        "btn_clear_list": "🗑️ Listeyi Temizle",
        "drop_hint": "🎬 Videoları buraya sürükleyip bırakın (Çoklu video desteklenir)",
        "output_group": "Kayıt Klasörü",
        "output_placeholder": "Varsayılan: Videonun bulunduğu klasör...",
        "browse_output": "Gözat...",
        "mode_group": "Kare Alma Modu",
        "mode_sec": "Belirli saniye aralığıyla al:",
        "sec_suffix": " saniye (Varsayılan: 1 sn)",
        "mode_total": "Tüm videodan eşit aralıklarla toplam:",
        "total_suffix": " adet fotoğraf al",
        "mode_frames": "Her:",
        "frames_suffix": " karede bir al",
        "mode_every": "Tüm kareleri al (Full FPS - Her tekil kare)",
        "adv_group": "🔍 Yakınlaştırma (Zoom) & Zaman Kırpma",
        "zoom_label": "Yakınlaştırma (Zoom):",
        "zoom_pos_label": "Odak Bölgesi:",
        "zoom_center": "Merkez (Ortala)",
        "zoom_top_left": "Sol Üst",
        "zoom_top_right": "Sağ Üst",
        "zoom_bottom_left": "Sol Alt",
        "zoom_bottom_right": "Sağ Alt",
        "trim_label": "Zaman Aralığı (Saniye):",
        "trim_start": "Başlangıç:",
        "trim_end": "Bitiş (0=Sonuna kadar):",
        "format_group": "Fotoğraf Formatı ve Kalite",
        "format_label": "Format:",
        "format_jpg": "JPG (Küçük boyut, yüksek hız)",
        "format_png": "PNG (Kayıpsız / Yüksek kalite)",
        "quality_label": "JPG Kalitesi (%):",
        "status_ready": "Hazır. Video ekleyin ve başlatın.",
        "btn_start": "🚀 Kareleri Çıkarmaya Başla (Tüm Liste)",
        "btn_cancel": "⏹️ Durdur",
        "btn_open": "📂 Klasörü Aç",
        "dialog_title": "Video Dosyası / Dosyaları Seç",
        "dialog_filter": "Video Dosyaları (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;Tüm Dosyalar (*.*)",
        "dialog_out_title": "Fotoğrafların Kaydedileceği Klasör",
        "warn_no_video": "Lütfen önce listeye en az bir video ekleyin!",
        "status_processing": "[{cur_idx}/{total_videos}] {fname} işleniyor...",
        "status_progress": "Video {cur_idx}/{total_videos}: {saved}/{total_expected} kare -> {file}",
        "status_done": "Tamamlandı! Toplam {v_count} videodan {total_frames} adet fotoğraf başarıyla kaydedildi.",
        "status_error": "Hata oluştu!",
        "status_stopping": "İşlem durduruluyor...",
        "popup_done_title": "Tüm İşlem Tamamlandı",
        "popup_done_msg": "Toplam {v_count} video işlendi ve {total_frames} adet fotoğraf kaydedildi!\n\nKlasörü şimdi açmak ister misiniz?",
        "popup_err_folder": "Klasör açılamadı: {err}"
    },
    "en": {
        "title": "Video to Frames Pro - Batch & Zoom Edition",
        "playlist_title": "📋 Video Playlist / Batch Queue",
        "btn_add_videos": "➕ Add Video(s)",
        "btn_clear_list": "🗑️ Clear List",
        "drop_hint": "🎬 Drag and drop videos here (Multi-video supported)",
        "output_group": "Output Folder",
        "output_placeholder": "Default: Video's parent folder...",
        "browse_output": "Browse...",
        "mode_group": "Frame Extraction Mode",
        "mode_sec": "Extract every specified seconds:",
        "sec_suffix": " seconds (Default: 1s)",
        "mode_total": "Evenly spread across video, total:",
        "total_suffix": " photos",
        "mode_frames": "Every:",
        "frames_suffix": " frames",
        "mode_every": "Extract every frame (Full FPS - All frames)",
        "adv_group": "🔍 Zoom & Time Trimming",
        "zoom_label": "Zoom Factor:",
        "zoom_pos_label": "Focus Region:",
        "zoom_center": "Center",
        "zoom_top_left": "Top-Left",
        "zoom_top_right": "Top-Right",
        "zoom_bottom_left": "Bottom-Left",
        "zoom_bottom_right": "Bottom-Right",
        "trim_label": "Time Range (Seconds):",
        "trim_start": "Start:",
        "trim_end": "End (0=Full):",
        "format_group": "Photo Format & Quality",
        "format_label": "Format:",
        "format_jpg": "JPG (Compact size, high speed)",
        "format_png": "PNG (Lossless / High quality)",
        "quality_label": "JPG Quality (%):",
        "status_ready": "Ready. Add videos to playlist and start.",
        "btn_start": "🚀 Start Extracting (Entire Playlist)",
        "btn_cancel": "⏹️ Stop",
        "btn_open": "📂 Open Folder",
        "dialog_title": "Select Video File(s)",
        "dialog_filter": "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm);;All Files (*.*)",
        "dialog_out_title": "Select Output Folder",
        "warn_no_video": "Please add at least one video to the playlist!",
        "status_processing": "[{cur_idx}/{total_videos}] Processing {fname}...",
        "status_progress": "Video {cur_idx}/{total_videos}: {saved}/{total_expected} frames -> {file}",
        "status_done": "Completed! Successfully saved {total_frames} photos from {v_count} video(s).",
        "status_error": "An error occurred!",
        "status_stopping": "Stopping extraction...",
        "popup_done_title": "Batch Process Completed",
        "popup_done_msg": "Successfully processed {v_count} video(s) and saved {total_frames} photos!\n\nWould you like to open the output folder now?",
        "popup_err_folder": "Could not open folder: {err}"
    }
}

class BatchWorker(QThread):
    item_started_signal = Signal(int, int, str)
    progress_signal = Signal(int, int, int, int, str)
    all_finished_signal = Signal(int, int, str)
    error_signal = Signal(str)

    def __init__(self, video_paths, custom_output_dir, mode, interval, start_sec, end_sec, zoom_factor, zoom_pos, img_format, quality):
        super().__init__()
        self.video_paths = video_paths
        self.custom_output_dir = custom_output_dir
        self.mode = mode
        self.interval = interval
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.zoom_factor = zoom_factor
        self.zoom_pos = zoom_pos
        self.img_format = img_format
        self.quality = quality
        self.is_cancelled = False

    def run(self):
        try:
            total_videos = len(self.video_paths)
            grand_total_frames = 0
            last_out_dir = ""

            for idx, vpath in enumerate(self.video_paths):
                if self.is_cancelled:
                    break

                fname = os.path.basename(vpath)
                self.item_started_signal.emit(idx + 1, total_videos, fname)

                if self.custom_output_dir and os.path.isdir(self.custom_output_dir):
                    vstem = os.path.splitext(fname)[0]
                    target_out = os.path.join(self.custom_output_dir, f"{vstem}_frames")
                else:
                    vdir = os.path.dirname(os.path.abspath(vpath))
                    vstem = os.path.splitext(fname)[0]
                    target_out = os.path.join(vdir, f"{vstem}_frames")

                last_out_dir = target_out

                def callback(saved, total, current_file):
                    if self.is_cancelled:
                        return False
                    self.progress_signal.emit(idx + 1, total_videos, saved, total, current_file)
                    return True

                count = extract_frames(
                    video_path=vpath,
                    output_dir=target_out,
                    mode=self.mode,
                    interval_value=self.interval,
                    start_sec=self.start_sec,
                    end_sec=self.end_sec if self.end_sec > 0 else None,
                    image_format=self.img_format,
                    quality=self.quality,
                    zoom_factor=self.zoom_factor,
                    zoom_position=self.zoom_pos,
                    progress_callback=callback
                )
                grand_total_frames += count

            self.all_finished_signal.emit(total_videos, grand_total_frames, last_out_dir)
        except Exception as e:
            self.error_signal.emit(str(e))

    def cancel(self):
        self.is_cancelled = True

class MainWindow(QMainWindow):
    def __init__(self, default_lang="tr"):
        super().__init__()
        self.current_lang = default_lang
        self.setMinimumSize(860, 760)
        self.setAcceptDrops(True)
        self.video_paths = []
        self.worker = None
        self.last_output_dir = ""

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
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QListWidget {
                background-color: #2D3748;
                border: 1px solid #4A5568;
                border-radius: 6px;
                padding: 6px 10px;
                color: #FFFFFF;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #374151;
            }
            QListWidget::item:selected {
                background-color: #2B6CB0;
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
        """)

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 16, 20, 20)
        main_layout.setSpacing(12)

        # Top Bar: Website Link & Language Dropdown
        top_bar = QHBoxLayout()
        self.dev_label = QLabel("<a href='https://www.eroldizdar.tr/p/video-to-frames.html' style='color: #63B3ED; text-decoration: none; font-weight: bold;'>🌐 eroldizdar.tr / Video to Frames Pro</a>")
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

        # Playlist / Video List Area
        self.playlist_group = QGroupBox()
        pl_layout = QVBoxLayout(self.playlist_group)

        self.video_list_widget = QListWidget()
        self.video_list_widget.setFixedHeight(120)
        pl_layout.addWidget(self.video_list_widget)

        pl_btn_layout = QHBoxLayout()
        self.btn_add = QPushButton()
        self.btn_add.clicked.connect(self.choose_videos_dialog)
        pl_btn_layout.addWidget(self.btn_add)

        self.btn_clear = QPushButton()
        self.btn_clear.clicked.connect(self.clear_playlist)
        pl_btn_layout.addWidget(self.btn_clear)

        self.lbl_drop_hint = QLabel()
        self.lbl_drop_hint.setStyleSheet("color: #A0AEC0; font-style: italic;")
        pl_btn_layout.addWidget(self.lbl_drop_hint)
        pl_btn_layout.addStretch()

        pl_layout.addLayout(pl_btn_layout)
        main_layout.addWidget(self.playlist_group)

        # Output Folder Group
        self.output_group = QGroupBox()
        out_layout = QHBoxLayout(self.output_group)
        self.output_edit = QLineEdit()
        out_layout.addWidget(self.output_edit)

        self.browse_out_btn = QPushButton()
        self.browse_out_btn.clicked.connect(self.choose_output_dialog)
        out_layout.addWidget(self.browse_out_btn)
        main_layout.addWidget(self.output_group)

        # Mode Selection Group
        self.mode_group = QGroupBox()
        mode_layout = QVBoxLayout(self.mode_group)
        mode_layout.setSpacing(8)

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

        # Zoom & Trimming Group
        self.adv_group = QGroupBox()
        adv_layout = QHBoxLayout(self.adv_group)

        self.lbl_zoom = QLabel()
        adv_layout.addWidget(self.lbl_zoom)

        self.combo_zoom = QComboBox()
        self.combo_zoom.addItem("1.0x (Normal)", 1.0)
        self.combo_zoom.addItem("1.25x Zoom", 1.25)
        self.combo_zoom.addItem("1.5x Zoom", 1.5)
        self.combo_zoom.addItem("2.0x (2 Kat)", 2.0)
        self.combo_zoom.addItem("3.0x (3 Kat)", 3.0)
        adv_layout.addWidget(self.combo_zoom)

        adv_layout.addSpacing(10)
        self.lbl_zoom_pos = QLabel()
        adv_layout.addWidget(self.lbl_zoom_pos)

        self.combo_zoom_pos = QComboBox()
        self.combo_zoom_pos.addItem("Merkez", "center")
        self.combo_zoom_pos.addItem("Sol Üst", "top-left")
        self.combo_zoom_pos.addItem("Sağ Üst", "top-right")
        self.combo_zoom_pos.addItem("Sol Alt", "bottom-left")
        self.combo_zoom_pos.addItem("Sağ Alt", "bottom-right")
        adv_layout.addWidget(self.combo_zoom_pos)

        adv_layout.addSpacing(15)
        self.lbl_start = QLabel()
        adv_layout.addWidget(self.lbl_start)
        self.spin_start = QDoubleSpinBox()
        self.spin_start.setRange(0, 86400)
        self.spin_start.setSuffix(" sn")
        adv_layout.addWidget(self.spin_start)

        self.lbl_end = QLabel()
        adv_layout.addWidget(self.lbl_end)
        self.spin_end = QDoubleSpinBox()
        self.spin_end.setRange(0, 86400)
        self.spin_end.setSuffix(" sn")
        adv_layout.addWidget(self.spin_end)

        adv_layout.addStretch()
        main_layout.addWidget(self.adv_group)

        # Format & Quality Group
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

        # Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #A0AEC0; font-style: italic;")
        main_layout.addWidget(self.status_label)

        # Action Buttons
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
        self.playlist_group.setTitle(self.t("playlist_title"))
        self.btn_add.setText(self.t("btn_add_videos"))
        self.btn_clear.setText(self.t("btn_clear_list"))
        self.lbl_drop_hint.setText(self.t("drop_hint"))

        self.output_group.setTitle(self.t("output_group"))
        self.output_edit.setPlaceholderText(self.t("output_placeholder"))
        self.browse_out_btn.setText(self.t("browse_output"))

        self.mode_group.setTitle(self.t("mode_group"))
        self.radio_sec.setText(self.t("mode_sec"))
        self.spin_sec.setSuffix(self.t("sec_suffix"))
        self.radio_total.setText(self.t("mode_total"))
        self.spin_total.setSuffix(self.t("total_suffix"))
        self.radio_interval_frames.setText(self.t("mode_frames"))
        self.spin_interval_frames.setSuffix(self.t("frames_suffix"))
        self.radio_every.setText(self.t("mode_every"))

        self.adv_group.setTitle(self.t("adv_group"))
        self.lbl_zoom.setText(self.t("zoom_label"))
        self.lbl_zoom_pos.setText(self.t("zoom_pos_label"))
        self.lbl_start.setText(self.t("trim_start"))
        self.lbl_end.setText(self.t("trim_end"))

        # Update zoom pos combo
        cur_pos_idx = self.combo_zoom_pos.currentIndex()
        self.combo_zoom_pos.clear()
        self.combo_zoom_pos.addItem(self.t("zoom_center"), "center")
        self.combo_zoom_pos.addItem(self.t("zoom_top_left"), "top-left")
        self.combo_zoom_pos.addItem(self.t("zoom_top_right"), "top-right")
        self.combo_zoom_pos.addItem(self.t("zoom_bottom_left"), "bottom-left")
        self.combo_zoom_pos.addItem(self.t("zoom_bottom_right"), "bottom-right")
        if cur_pos_idx >= 0:
            self.combo_zoom_pos.setCurrentIndex(cur_pos_idx)

        self.fmt_group.setTitle(self.t("format_group"))
        self.lbl_format.setText(self.t("format_label"))
        cur_fmt_idx = self.combo_fmt.currentIndex()
        self.combo_fmt.clear()
        self.combo_fmt.addItems([self.t("format_jpg"), self.t("format_png")])
        if cur_fmt_idx >= 0:
            self.combo_fmt.setCurrentIndex(cur_fmt_idx)

        self.lbl_quality.setText(self.t("quality_label"))
        self.status_label.setText(self.t("status_ready"))
        self.start_btn.setText(self.t("btn_start"))
        self.cancel_btn.setText(self.t("btn_cancel"))
        self.open_folder_btn.setText(self.t("btn_open"))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for u in urls:
            path = u.toLocalFile()
            if os.path.isfile(path):
                self.add_video_to_list(path)

    def choose_videos_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.t("dialog_title"),
            "",
            self.t("dialog_filter")
        )
        for f in files:
            self.add_video_to_list(f)

    def add_video_to_list(self, path):
        if path not in self.video_paths:
            try:
                info = get_video_info(path)
                self.video_paths.append(path)
                mins = int(info['duration_sec'] // 60)
                secs = int(info['duration_sec'] % 60)
                fname = os.path.basename(path)
                item_text = f"🎬 {fname}  ({mins:02d}:{secs:02d} | {info['width']}x{info['height']} | {info['fps']:.1f} fps)"
                self.video_list_widget.addItem(QListWidgetItem(item_text))
            except Exception:
                pass

    def clear_playlist(self):
        self.video_paths.clear()
        self.video_list_widget.clear()

    def choose_output_dialog(self):
        d = QFileDialog.getExistingDirectory(self, self.t("dialog_out_title"))
        if d:
            self.output_edit.setText(d)

    def start_extraction(self):
        if not self.video_paths:
            QMessageBox.warning(self, "Warning", self.t("warn_no_video"))
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
        zoom_factor = self.combo_zoom.currentData()
        zoom_pos = self.combo_zoom_pos.currentData()
        start_sec = self.spin_start.value()
        end_sec = self.spin_end.value()
        custom_out = self.output_edit.text().strip()

        self.progress_bar.setValue(0)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(False)

        self.worker = BatchWorker(
            video_paths=list(self.video_paths),
            custom_output_dir=custom_out,
            mode=mode,
            interval=interval,
            start_sec=start_sec,
            end_sec=end_sec,
            zoom_factor=zoom_factor,
            zoom_pos=zoom_pos,
            img_format=fmt,
            quality=qual
        )
        self.worker.item_started_signal.connect(self.on_item_started)
        self.worker.progress_signal.connect(self.on_progress)
        self.worker.all_finished_signal.connect(self.on_all_finished)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()

    def on_item_started(self, cur_idx, total_v, fname):
        self.status_label.setText(self.t("status_processing").format(cur_idx=cur_idx, total_videos=total_v, fname=fname))

    def on_progress(self, cur_idx, total_v, saved, total_expected, current_file):
        pct = int((saved / total_expected) * 100) if total_expected > 0 else 0
        self.progress_bar.setValue(pct)
        self.status_label.setText(self.t("status_progress").format(
            cur_idx=cur_idx, total_videos=total_v, saved=saved, total_expected=total_expected, file=current_file
        ))

    def on_all_finished(self, v_count, total_frames, last_dir):
        self.last_output_dir = last_dir
        self.progress_bar.setValue(100)
        self.status_label.setText(self.t("status_done").format(v_count=v_count, total_frames=total_frames))
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(True)

        reply = QMessageBox.information(
            self,
            self.t("popup_done_title"),
            self.t("popup_done_msg").format(v_count=v_count, total_frames=total_frames),
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
        target = self.output_edit.text().strip() or self.last_output_dir
        if target and os.path.exists(target):
            try:
                os.startfile(target)
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
