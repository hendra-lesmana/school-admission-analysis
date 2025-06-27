#!/usr/bin/env python3
"""
Analisis Top 50 Siswa per Jurusan dari data Prestasi-Rapor
Membuat tabel ranking untuk setiap jurusan berdasarkan skor
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_and_analyze_data():
    """Load data dan analisis top 50 per jurusan"""
    try:
        # Load data
        print("📊 Loading data dari hasil_all_prestasi_rapor.csv...")
        df = pd.read_csv('hasil_all_prestasi_rapor.csv')
        print(f"✅ Data berhasil dimuat: {len(df)} records")
        
        # Tampilkan info dasar
        print(f"\n📋 Info Dataset:")
        print(f"  - Total siswa: {len(df)}")
        print(f"  - Kolom tersedia: {list(df.columns)}")
        
        # Cek kolom yang diperlukan
        required_cols = ['first_option_name', 'score', 'name', 'registration_number']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Kolom yang hilang: {missing_cols}")
            return None
        
        # Clean data
        df = df.dropna(subset=['first_option_name', 'score'])
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df = df.dropna(subset=['score'])
        
        print(f"  - Data setelah cleaning: {len(df)} records")
        
        return df
        
    except FileNotFoundError:
        print("❌ File hasil_all_prestasi_rapor.csv tidak ditemukan!")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def create_top50_per_jurusan(df):
    """Buat tabel top 50 untuk setiap jurusan"""
    
    # Dapatkan daftar jurusan
    jurusan_list = df['first_option_name'].unique()
    print(f"\n🎓 Ditemukan {len(jurusan_list)} jurusan:")
    
    results = {}
    
    for i, jurusan in enumerate(jurusan_list, 1):
        print(f"  {i}. {jurusan}")
        
        # Filter data untuk jurusan ini
        jurusan_df = df[df['first_option_name'] == jurusan].copy()
        
        # Sort berdasarkan score (descending)
        jurusan_df = jurusan_df.sort_values('score', ascending=False)
        
        # Ambil top 50 (atau semua jika kurang dari 50)
        top_50 = jurusan_df.head(50).copy()
        
        # Tambahkan ranking
        top_50['Ranking'] = range(1, len(top_50) + 1)
        
        # Pilih kolom yang akan ditampilkan
        display_cols = ['Ranking', 'registration_number', 'name', 'score']
        if 'school_name' in top_50.columns:
            display_cols.append('school_name')
        if 'created_at' in top_50.columns:
            display_cols.append('created_at')
        
        # Filter kolom yang ada
        available_cols = [col for col in display_cols if col in top_50.columns]
        top_50_display = top_50[available_cols]
        
        results[jurusan] = {
            'data': top_50_display,
            'total_siswa': len(jurusan_df),
            'score_tertinggi': jurusan_df['score'].max(),
            'score_terendah': jurusan_df['score'].min(),
            'rata_rata_score': jurusan_df['score'].mean()
        }
        
        print(f"     - Total siswa: {len(jurusan_df)}")
        print(f"     - Top 50: {len(top_50)} siswa")
        print(f"     - Score range: {jurusan_df['score'].min():.1f} - {jurusan_df['score'].max():.1f}")
    
    return results

def save_results_to_files(results):
    """Simpan hasil ke file CSV"""

    print(f"\n💾 Menyimpan hasil ke file...")

    # Buat summary data
    summary_data = []
    for jurusan, data in results.items():
        summary_data.append({
            'Jurusan': jurusan,
            'Total_Siswa': data['total_siswa'],
            'Score_Tertinggi': data['score_tertinggi'],
            'Score_Terendah': data['score_terendah'],
            'Rata_Rata_Score': round(data['rata_rata_score'], 2)
        })

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('summary_jurusan.csv', index=False)
    print(f"  ✅ Summary -> summary_jurusan.csv")

    # Simpan data untuk setiap jurusan
    for jurusan, data in results.items():
        # Buat nama file yang valid
        clean_name = jurusan.replace('SMKN 4 PADALARANG - ', '').replace('SMAN 2 PADALARANG - ', '')
        clean_name = clean_name.replace(' - PRESTASI NILAI RAPOR', '')
        clean_name = clean_name.replace(' ', '_').replace('/', '_').replace('-', '_')

        # Simpan ke CSV individual
        csv_filename = f"top50_{clean_name}.csv"
        data['data'].to_csv(csv_filename, index=False)

        print(f"  ✅ {clean_name}: {len(data['data'])} siswa -> {csv_filename}")

    return summary_df

def display_summary(summary_df):
    """Tampilkan ringkasan hasil"""
    
    print(f"\n" + "="*80)
    print("📊 RINGKASAN TOP 50 PER JURUSAN")
    print("="*80)
    
    for _, row in summary_df.iterrows():
        print(f"\n🎓 {row['Jurusan']}")
        print(f"   Total Siswa: {row['Total_Siswa']}")
        print(f"   Score Tertinggi: {row['Score_Tertinggi']}")
        print(f"   Score Terendah: {row['Score_Terendah']}")
        print(f"   Rata-rata Score: {row['Rata_Rata_Score']}")
    
    print(f"\n" + "="*80)
    print("📁 FILE OUTPUT:")
    print("="*80)
    print("✅ summary_jurusan.csv - Ringkasan semua jurusan")
    print("✅ top50_[nama_jurusan].csv - File CSV untuk setiap jurusan")
    print("✅ Setiap file berisi ranking top 50 siswa per jurusan")

def main():
    print("="*80)
    print("🎓 ANALISIS TOP 50 SISWA PER JURUSAN")
    print("="*80)
    print("Menganalisis data prestasi-rapor dan membuat ranking per jurusan")
    print("="*80)
    
    # Load data
    df = load_and_analyze_data()
    if df is None:
        return
    
    # Analisis top 50 per jurusan
    results = create_top50_per_jurusan(df)
    
    # Simpan hasil
    summary_df = save_results_to_files(results)
    
    # Tampilkan ringkasan
    display_summary(summary_df)
    
    print(f"\n🎉 Analisis selesai!")
    print(f"📊 {len(results)} jurusan telah dianalisis")
    print(f"📁 File output telah disimpan")

if __name__ == "__main__":
    main()
