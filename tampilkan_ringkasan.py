#!/usr/bin/env python3
"""
Tampilkan ringkasan hasil analisis top 50 per jurusan
"""

import pandas as pd

def main():
    try:
        # Load summary data
        df = pd.read_csv('summary_top50_per_jurusan.csv')
        
        print("="*80)
        print("📊 RINGKASAN TOP 50 PER JURUSAN - SMKN 4 PADALARANG")
        print("="*80)
        
        total_siswa_all = df['Total_Siswa'].sum()
        print(f"🎓 Total Siswa Semua Jurusan: {total_siswa_all}")
        print(f"📚 Jumlah Jurusan: {len(df)}")
        print()
        
        for i, (_, row) in enumerate(df.iterrows(), 1):
            jurusan_name = row['Jurusan'].replace('SMKN 4 PADALARANG - ', '').replace(' - PRESTASI NILAI RAPOR', '')
            
            print(f"{i}. 🎓 {jurusan_name}")
            print(f"   👥 Total Siswa: {row['Total_Siswa']}")
            print(f"   🏆 Top Siswa: {row['Top_50_Count']}")
            print(f"   📈 Score Tertinggi: {row['Score_Tertinggi']}")
            print(f"   📉 Score Terendah: {row['Score_Terendah']}")
            print(f"   📊 Rata-rata Score: {row['Rata_Rata_Score']}")
            print(f"   📁 File Output: {row['File_Output']}")
            print()
        
        print("="*80)
        print("📁 FILE YANG TELAH DIBUAT:")
        print("="*80)
        print("✅ smkn4_prestasi_rapor_raw.csv - Data mentah semua 329 siswa")
        print("✅ summary_top50_per_jurusan.csv - Ringkasan statistik per jurusan")
        print()
        
        for _, row in df.iterrows():
            jurusan_short = row['Jurusan'].replace('SMKN 4 PADALARANG - ', '').replace(' - PRESTASI NILAI RAPOR', '')
            print(f"✅ {row['File_Output']} - Top {row['Top_50_Count']} siswa {jurusan_short}")
        
        print()
        print("🎉 Semua tabel top 50 per jurusan telah berhasil dibuat!")
        
    except FileNotFoundError:
        print("❌ File summary_top50_per_jurusan.csv tidak ditemukan!")
        print("Silakan jalankan script scrape_smkn4_multiple_jurusan.py terlebih dahulu.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
