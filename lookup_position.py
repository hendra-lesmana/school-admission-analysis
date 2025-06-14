import csv
import sys

def find_registration_position(registration_number: str, csv_file: str = "hasil_zonasi_only.csv", quota: int = 139):
    """Find position and calculate acceptance probability for a registration number"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        # Data is already filtered to zonasi only
        zonasi_data = data

        for i, record in enumerate(zonasi_data):
            if record['registration_number'] == registration_number:
                position = i + 1
                
                # Calculate acceptance probability based on quota of 139
                if position <= quota:
                    if position <= quota * 0.3:  # Top 30% of quota
                        probability = 95.0
                        status = "SANGAT TINGGI"
                        color = "🟢"
                    elif position <= quota * 0.6:  # Top 60% of quota
                        probability = 85.0
                        status = "TINGGI"
                        color = "🟢"
                    elif position <= quota * 0.8:  # Top 80% of quota
                        probability = 75.0
                        status = "SEDANG-TINGGI"
                        color = "🟡"
                    else:  # Within quota but lower position
                        probability = 65.0
                        status = "SEDANG"
                        color = "🟡"
                else:
                    # Beyond quota
                    excess = position - quota
                    if excess <= 20:
                        probability = 40.0
                        status = "RENDAH"
                        color = "🔴"
                    elif excess <= 50:
                        probability = 20.0
                        status = "SANGAT RENDAH"
                        color = "🔴"
                    else:
                        probability = 5.0
                        status = "SANGAT RENDAH"
                        color = "🔴"
                
                return {
                    'found': True,
                    'position': position,
                    'total_zonasi': len(zonasi_data),
                    'total_all': len(data),
                    'quota': quota,
                    'probability': probability,
                    'status': status,
                    'color': color,
                    'student_data': record
                }
        
        return {'found': False}
        
    except FileNotFoundError:
        print(f"File {csv_file} tidak ditemukan. Pastikan sudah menjalankan scraper terlebih dahulu.")
        return {'found': False}
    except Exception as e:
        print(f"Error: {e}")
        return {'found': False}

def display_position_report(registration_number: str, quota: int = 139):
    """Display simplified position report - position and total only for zonasi"""
    result = find_registration_position(registration_number, quota=quota)

    if not result['found']:
        print(f"\n❌ Nomor registrasi {registration_number} tidak ditemukan dalam data.")
        return

    student = result['student_data']

    print(f"\n{'='*60}")
    print(f"📊 POSISI ZONASI")
    print(f"{'='*60}")
    print(f"📋 Nomor Registrasi: {registration_number}")
    print(f"👤 Nama: {student.get('name', 'Unknown')}")
    print(f"🎯 Posisi: #{result['position']} dari {result['total_zonasi']} siswa zonasi")
    print(f"🎓 Kuota: {quota} siswa")

    # Position status
    if result['position'] <= quota:
        status_icon = "✅"
        status_text = "DALAM KUOTA"
    else:
        excess = result['position'] - quota
        status_icon = "⚠️"
        status_text = f"DI LUAR KUOTA (+{excess})"

    print(f"{status_icon} Status: {status_text}")
    print(f"{result['color']} Kemungkinan: {result['probability']}% ({result['status']})")
    print(f"📏 Jarak: {student.get('distance_1', 'N/A')} meter")
    print(f"{'='*60}\n")

def main():
    print("🔍 PENCARIAN POSISI PENERIMAAN SISWA")
    print("Data berdasarkan hasil scraping terbaru (sudah diurutkan berdasarkan jarak)")
    print("="*80)
    
    # Check if registration number provided as argument
    if len(sys.argv) > 1:
        registration_number = sys.argv[1]
        quota = int(sys.argv[2]) if len(sys.argv) > 2 else 139
        display_position_report(registration_number, quota)
        return
    
    # Interactive mode
    while True:
        print("\nMasukkan nomor registrasi untuk melihat posisi dan kemungkinan diterima")
        registration_number = input("Nomor registrasi (atau 'quit' untuk keluar): ").strip()
        
        if registration_number.lower() in ['quit', 'exit', 'q', 'keluar']:
            print("Terima kasih! 👋")
            break
        
        if not registration_number:
            print("❌ Silakan masukkan nomor registrasi yang valid.")
            continue
        
        # Ask for quota (optional)
        quota_input = input("Kuota penerimaan (tekan Enter untuk default 139): ").strip()
        try:
            quota = int(quota_input) if quota_input else 139
        except ValueError:
            quota = 139
            print("Input tidak valid, menggunakan kuota default: 139")
        
        display_position_report(registration_number, quota)

if __name__ == "__main__":
    main()
