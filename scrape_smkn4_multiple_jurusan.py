#!/usr/bin/env python3
"""
Scrape data prestasi-rapor untuk SMKN 4 PADALARANG yang memiliki multiple jurusan
Kemudian buat tabel top 50 untuk setiap jurusan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import StreamlitScraper
import pandas as pd

def scrape_smkn4_data():
    """Scrape data SMKN 4 PADALARANG"""
    print("="*80)
    print("🎓 SCRAPING DATA SMKN 4 PADALARANG")
    print("="*80)
    
    # Initialize scraper
    scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")
    
    # NPSN untuk SMKN 4 PADALARANG
    npsn = "20206224"
    
    print(f"🏫 Scraping NPSN: {npsn} (SMKN 4 PADALARANG)")
    print("📊 Mengambil semua data prestasi-rapor dari semua jurusan...")
    
    # Mock progress tracking
    class MockProgress:
        def progress(self, value):
            print(f"Progress: {int(value * 100)}%")
    
    class MockStatus:
        def text(self, message):
            print(f"Status: {message}")
    
    progress_bar = MockProgress()
    status_text = MockStatus()
    
    try:
        # Scrape all prestasi-rapor data
        all_prestasi_data = scraper.scrape_all_pages(
            progress_bar, status_text,
            npsn=npsn, 
            option_type='prestasi-rapor',
            orderby='score', 
            order='desc'
        )
        
        if all_prestasi_data:
            print(f"✅ SUCCESS: Collected {len(all_prestasi_data)} prestasi-rapor records")
            
            # Convert to DataFrame
            df = pd.DataFrame(all_prestasi_data)
            
            # Save raw data
            df.to_csv('smkn4_prestasi_rapor_raw.csv', index=False)
            print(f"💾 Raw data saved to: smkn4_prestasi_rapor_raw.csv")
            
            # Show jurusan info
            if 'first_option_name' in df.columns:
                jurusan_counts = df['first_option_name'].value_counts()
                print(f"\n🎓 Ditemukan {len(jurusan_counts)} jurusan:")
                for i, (jurusan, count) in enumerate(jurusan_counts.items(), 1):
                    print(f"  {i}. {jurusan}: {count} siswa")
            
            return df
        else:
            print("❌ FAILED: No prestasi-rapor data collected")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def create_top50_tables(df):
    """Buat tabel top 50 untuk setiap jurusan"""
    
    if df is None or len(df) == 0:
        print("❌ No data to process")
        return
    
    print(f"\n" + "="*80)
    print("📊 MEMBUAT TABEL TOP 50 PER JURUSAN")
    print("="*80)
    
    # Clean data
    df = df.dropna(subset=['first_option_name', 'score'])
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df = df.dropna(subset=['score'])
    
    # Get unique jurusan
    jurusan_list = df['first_option_name'].unique()
    
    summary_data = []
    
    for i, jurusan in enumerate(jurusan_list, 1):
        print(f"\n🎓 {i}. {jurusan}")
        
        # Filter data untuk jurusan ini
        jurusan_df = df[df['first_option_name'] == jurusan].copy()
        
        # Sort berdasarkan score (descending)
        jurusan_df = jurusan_df.sort_values('score', ascending=False)
        
        # Ambil top 50 (atau semua jika kurang dari 50)
        top_50 = jurusan_df.head(50).copy()
        
        # Tambahkan ranking
        top_50['Ranking'] = range(1, len(top_50) + 1)
        
        # Pilih kolom untuk display
        display_cols = ['Ranking', 'registration_number', 'name', 'score']
        if 'school_name' in top_50.columns:
            display_cols.append('school_name')
        if 'created_at' in top_50.columns:
            display_cols.append('created_at')
        
        # Filter kolom yang ada
        available_cols = [col for col in display_cols if col in top_50.columns]
        top_50_display = top_50[available_cols]
        
        # Buat nama file yang bersih
        clean_name = jurusan.replace('SMKN 4 PADALARANG - ', '')
        clean_name = clean_name.replace(' - PRESTASI NILAI RAPOR', '')
        clean_name = clean_name.replace(' ', '_').replace('/', '_').replace('-', '_')
        
        # Simpan ke CSV
        filename = f"top50_{clean_name}.csv"
        top_50_display.to_csv(filename, index=False)
        
        # Statistik
        stats = {
            'Jurusan': jurusan,
            'Total_Siswa': len(jurusan_df),
            'Top_50_Count': len(top_50),
            'Score_Tertinggi': jurusan_df['score'].max(),
            'Score_Terendah': jurusan_df['score'].min(),
            'Rata_Rata_Score': round(jurusan_df['score'].mean(), 2),
            'File_Output': filename
        }
        summary_data.append(stats)
        
        print(f"   📊 Total siswa: {len(jurusan_df)}")
        print(f"   🏆 Top 50: {len(top_50)} siswa")
        print(f"   📈 Score range: {jurusan_df['score'].min():.1f} - {jurusan_df['score'].max():.1f}")
        print(f"   💾 Saved to: {filename}")
        
        # Show top 5 untuk preview
        print(f"   🥇 Top 5 siswa:")
        for idx, (_, student) in enumerate(top_50.head(5).iterrows(), 1):
            name = student.get('name', 'Unknown')
            score = student.get('score', 'N/A')
            print(f"      {idx}. {name} - Score: {score}")
    
    # Simpan summary
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('summary_top50_per_jurusan.csv', index=False)
    
    print(f"\n" + "="*80)
    print("📁 FILE OUTPUT SUMMARY")
    print("="*80)
    print("✅ smkn4_prestasi_rapor_raw.csv - Data mentah semua siswa")
    print("✅ summary_top50_per_jurusan.csv - Ringkasan per jurusan")
    
    for _, row in summary_df.iterrows():
        print(f"✅ {row['File_Output']} - Top {row['Top_50_Count']} siswa {row['Jurusan'].split(' - ')[1]}")
    
    print(f"\n🎉 Selesai! {len(jurusan_list)} jurusan telah dianalisis")
    
    return summary_df

def main():
    print("🎓 ANALISIS TOP 50 SISWA PER JURUSAN - SMKN 4 PADALARANG")
    print("="*80)
    
    # Step 1: Scrape data
    df = scrape_smkn4_data()
    
    if df is not None:
        # Step 2: Create top 50 tables
        summary = create_top50_tables(df)
        
        print(f"\n✅ Analisis berhasil diselesaikan!")
        print(f"📊 Data dari {len(df)} siswa telah dianalisis")
        print(f"📁 File CSV untuk setiap jurusan telah dibuat")
    else:
        print(f"\n❌ Gagal mengambil data. Silakan coba lagi.")

if __name__ == "__main__":
    main()
