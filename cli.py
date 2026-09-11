import os
import sys
import argparse
import subprocess
from extractor import extract_frames, get_video_info

def print_progress(saved, total, current_file):
    pct = (saved / total) * 100 if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * saved // total) if total > 0 else 0
    bar = "=" * filled + "-" * (bar_len - filled)
    print(f"\rİlerleme: [{bar}] %{pct:.1f} ({saved}/{total}) -> {current_file}", end="", flush=True)
    return True

def main():
    parser = argparse.ArgumentParser(description="Videoyu fotoğraflara dönüştürücü (CLI)")
    parser.add_argument("video", nargs="?", help="Video dosya yolu")
    parser.add_argument("-o", "--output", help="Fotoğrafların kaydedileceği klasör")
    parser.add_argument("-m", "--mode", choices=["seconds", "every_frame", "interval_frames", "total_count"], default="seconds", help="Kare alma modu")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Aralık değeri (saniye veya kare)")
    parser.add_argument("-f", "--format", choices=["jpg", "png"], default="jpg", help="Resim formatı")
    parser.add_argument("-q", "--quality", type=int, default=95, help="Kalite (1-100)")
    parser.add_argument("--interactive", action="store_true", help="Konsolda etkileşimli soru sor")

    args = parser.parse_args()

    video_path = args.video
    if not video_path:
        print("\n=======================================================")
        print("         VİDEODAN FOTOĞRAF ÇIKARMA ARACI               ")
        print("=======================================================\n")
        video_path = input("Lütfen video dosyasını bu pencereye sürükleyip bırakın (veya yolunu yazın):\n> ").strip()
        video_path = video_path.strip('"').strip("'")
        args.interactive = True

    if not os.path.isfile(video_path):
        print(f"\nHATA: Belirtilen video dosyası bulunamadı: {video_path}")
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)

    try:
        info = get_video_info(video_path)
    except Exception as e:
        print(f"\nHATA: Video dosyası okunamadı: {e}")
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)

    print("\n-------------------------------------------------------")
    print(f"Video Bilgileri:")
    print(f"Dosya: {os.path.basename(video_path)}")
    print(f"Çözünürlük: {info['width']}x{info['height']}")
    print(f"FPS: {info['fps']:.2f}")
    print(f"Toplam Süre: {info['duration_sec']:.1f} saniye ({int(info['duration_sec']//60)} dk {int(info['duration_sec']%60)} sn)")
    print(f"Toplam Kare Sayısı: {info['total_frames']}")
    print("-------------------------------------------------------\n")

    mode = args.mode
    interval = args.interval
    img_format = args.format

    if args.interactive or len(sys.argv) <= 2:
        print("Nasıl fotoğraf almak istersiniz?")
        print(" [1] Her 1 saniyede 1 fotoğraf al (Varsayılan, Hızlı & İdeal)")
        print(" [2] Belirttiğim saniye aralığıyla al (Örn: her 2 saniyede, her 0.5 saniyede)")
        print(" [3] Toplam belirlediğim sayıda eşit aralıklı fotoğraf al (Örn: toplam 50 adet)")
        print(" [4] Videodaki TÜM kareleri al (Dikkat: Çok fazla fotoğraf çıkabilir!)")
        
        choice = input("\nSeçiminiz [1/2/3/4] (Varsayılan 1): ").strip()
        
        if choice == "2":
            mode = "seconds"
            val_str = input("Kaç saniyede bir fotoğraf alınsın? (Örn: 2 veya 0.5): ").strip()
            try:
                interval = float(val_str.replace(",", "."))
            except ValueError:
                interval = 1.0
        elif choice == "3":
            mode = "total_count"
            val_str = input("Videodan toplam kaç fotoğraf alınsın? (Örn: 30): ").strip()
            try:
                interval = float(val_str)
            except ValueError:
                interval = 30.0
        elif choice == "4":
            mode = "every_frame"
            interval = 1.0
        else:
            mode = "seconds"
            interval = 1.0

        fmt_choice = input("\nFormat ne olsun? [1] JPG (Küçük boyut, yüksek kalite) [2] PNG (Kayıpsız) (Varsayılan 1): ").strip()
        if fmt_choice == "2":
            img_format = "png"
        else:
            img_format = "jpg"

    # Default output directory: folder of video / <video_stem>_fotograflar
    if not args.output:
        video_dir = os.path.dirname(os.path.abspath(video_path))
        video_stem = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(video_dir, f"{video_stem}_fotograflar")
    else:
        output_dir = args.output

    print(f"\nFotoğraflar şu klasöre kaydedilecek:")
    print(f"-> {output_dir}\n")
    print("İşlem başlatılıyor...")

    try:
        count = extract_frames(
            video_path=video_path,
            output_dir=output_dir,
            mode=mode,
            interval_value=interval,
            image_format=img_format,
            quality=args.quality,
            progress_callback=print_progress
        )
        print(f"\n\nBAŞARILI! Toplam {count} adet fotoğraf kaydedildi.")
        print(f"Klasör: {output_dir}")
        
        # Open folder in Explorer
        try:
            os.startfile(output_dir)
        except Exception:
            pass

    except Exception as e:
        print(f"\nİşlem sırasında hata oluştu: {e}")

    if args.interactive or len(sys.argv) <= 2:
        input("\nPencereyi kapatmak için Enter'a basın...")

if __name__ == "__main__":
    main()
