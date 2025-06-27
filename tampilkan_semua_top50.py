#!/usr/bin/env python3
"""
Tampilkan semua tabel top 50 per jurusan dalam format yang rapi
"""

import pandas as pd
import os

def tampilkan_top50_jurusan():
    """Tampilkan top 50 untuk semua jurusan"""
    
    # Daftar file top 50
    files = [
        ('top50_PENGEMBANGAN_PERANGKAT_LUNAK_DAN_GIM.csv', 'PENGEMBANGAN PERANGKAT LUNAK DAN GIM'),
        ('top50_PEMASARAN.csv', 'PEMASARAN'),
        ('top50_TEKNIK_KIMIA_INDUSTRI.csv', 'TEKNIK KIMIA INDUSTRI'),
        ('top50_TEKNIK_JARINGAN_KOMPUTER_DAN_TELEKOMUNIKASI.csv', 'TEKNIK JARINGAN KOMPUTER DAN TELEKOMUNIKASI'),
        ('top50_TEKNIK_ELEKTRONIKA.csv', 'TEKNIK ELEKTRONIKA'),
        ('top50_AGRIBISNIS_TANAMAN.csv', 'AGRIBISNIS TANAMAN')
    ]
    
    print("="*100)
    print("🎓 TABEL TOP 50 SISWA PER JURUSAN - SMKN 4 PADALARANG")
    print("="*100)
    
    for i, (filename, jurusan_name) in enumerate(files, 1):
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                
                print(f"\n{i}. 🎓 JURUSAN: {jurusan_name}")
                print("="*100)
                print(f"📊 Total siswa dalam ranking: {len(df)}")
                
                if len(df) > 0:
                    # Tampilkan top 10 untuk preview
                    print(f"\n🏆 TOP 10 SISWA:")
                    print("-" * 100)
                    
                    top_10 = df.head(10)
                    for _, row in top_10.iterrows():
                        ranking = row['Ranking']
                        name = row['name']
                        score = row['score']
                        school = row.get('school_name', 'Unknown')
                        reg_num = row['registration_number']
                        
                        print(f"{ranking:2d}. {name:<30} | Score: {score:6.1f} | {school}")
                    
                    # Statistik
                    scores = df['score']
                    print(f"\n📈 STATISTIK JURUSAN:")
                    print(f"   Score Tertinggi: {scores.max():.1f}")
                    print(f"   Score Terendah:  {scores.min():.1f}")
                    print(f"   Rata-rata Score: {scores.mean():.1f}")
                    print(f"   Median Score:    {scores.median():.1f}")
                    
                    # Info file
                    print(f"\n📁 File lengkap: {filename}")
                    
                    if len(df) > 10:
                        print(f"💡 Menampilkan 10 dari {len(df)} siswa. Lihat file CSV untuk data lengkap.")
                
            except Exception as e:
                print(f"❌ Error membaca {filename}: {e}")
        else:
            print(f"❌ File {filename} tidak ditemukan")
    
    print(f"\n" + "="*100)
    print("📋 RINGKASAN SEMUA JURUSAN")
    print("="*100)
    
    # Load summary
    try:
        summary_df = pd.read_csv('summary_top50_per_jurusan.csv')
        
        print(f"🎓 Total Jurusan: {len(summary_df)}")
        print(f"👥 Total Siswa Semua Jurusan: {summary_df['Total_Siswa'].sum()}")
        print(f"📈 Score Tertinggi Keseluruhan: {summary_df['Score_Tertinggi'].max():.1f}")
        print(f"📉 Score Terendah Keseluruhan: {summary_df['Score_Terendah'].min():.1f}")
        
        # Ranking jurusan berdasarkan score tertinggi
        print(f"\n🏆 RANKING JURUSAN BERDASARKAN SCORE TERTINGGI:")
        summary_sorted = summary_df.sort_values('Score_Tertinggi', ascending=False)
        
        for i, (_, row) in enumerate(summary_sorted.iterrows(), 1):
            jurusan = row['Jurusan'].replace('SMKN 4 PADALARANG - ', '').replace(' - PRESTASI NILAI RAPOR', '')
            score_max = row['Score_Tertinggi']
            total_siswa = row['Total_Siswa']
            avg_score = row['Rata_Rata_Score']
            
            print(f"{i}. {jurusan}")
            print(f"   Score Tertinggi: {score_max:.1f} | Total Siswa: {total_siswa} | Rata-rata: {avg_score:.1f}")
        
    except FileNotFoundError:
        print("❌ File summary tidak ditemukan")
    
    print(f"\n🎉 Semua tabel top 50 per jurusan telah ditampilkan!")
    print(f"📁 File CSV tersedia untuk analisis lebih lanjut")

def main():
    tampilkan_top50_jurusan()

if __name__ == "__main__":
    main()
