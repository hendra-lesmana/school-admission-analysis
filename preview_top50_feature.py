#!/usr/bin/env python3
"""
Preview fitur Top 50 per Jurusan yang telah ditambahkan ke Streamlit
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import analyze_prestasi_by_jurusan

def show_feature_preview():
    """Tampilkan preview fitur Top 50 per Jurusan"""
    
    print("="*100)
    print("🎓 PREVIEW FITUR TOP 50 PER JURUSAN DI STREAMLIT")
    print("="*100)
    
    try:
        # Load and analyze data
        df = pd.read_csv('hasil_all_prestasi_rapor.csv')
        results = analyze_prestasi_by_jurusan(df)
        
        print(f"📊 Data berhasil dianalisis untuk {len(results)} jurusan dari {len(df)} siswa total")
        print()
        
        # Show summary statistics
        total_siswa = sum([data['total_siswa'] for data in results.values()])
        highest_score = max([data['score_tertinggi'] for data in results.values()])
        lowest_score = min([data['score_terendah'] for data in results.values()])
        
        print("📈 RINGKASAN STATISTIK:")
        print(f"  🎓 Total Jurusan: {len(results)}")
        print(f"  👥 Total Siswa: {total_siswa}")
        print(f"  📊 Score Range: {lowest_score:.1f} - {highest_score:.1f}")
        print()
        
        # Show each jurusan preview
        print("🏆 PREVIEW TOP 5 SISWA SETIAP JURUSAN:")
        print("="*100)
        
        for i, (jurusan, data) in enumerate(results.items(), 1):
            print(f"\n{i}. 🎓 {jurusan.upper()}")
            print("-" * 80)
            print(f"📊 Total Siswa: {data['total_siswa']} | Top Records: {len(data['data'])} | Rata-rata: {data['rata_rata_score']:.1f}")
            print(f"📈 Score Range: {data['score_terendah']:.1f} - {data['score_tertinggi']:.1f}")
            
            # Show top 5
            top_5 = data['data'].head(5)
            print(f"\n🏆 TOP 5 SISWA:")
            
            for _, student in top_5.iterrows():
                ranking = student['Ranking']
                name = student['name']
                score = student['score']
                school = student.get('school_name', 'Unknown')
                reg_num = student['registration_number']
                
                print(f"  {ranking:2d}. {name:<35} | Score: {score:6.1f} | {school}")
        
        # Show comparison table
        print(f"\n" + "="*100)
        print("📊 TABEL PERBANDINGAN JURUSAN")
        print("="*100)
        
        comparison_data = []
        for jurusan, data in results.items():
            comparison_data.append({
                'Jurusan': jurusan,
                'Total_Siswa': data['total_siswa'],
                'Score_Tertinggi': data['score_tertinggi'],
                'Score_Terendah': data['score_terendah'],
                'Rata_Rata': round(data['rata_rata_score'], 1),
                'Median': round(data['median_score'], 1)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Score_Tertinggi', ascending=False)
        
        print("Ranking berdasarkan Score Tertinggi:")
        print("-" * 100)
        
        for i, (_, row) in enumerate(comparison_df.iterrows(), 1):
            jurusan = row['Jurusan']
            total = row['Total_Siswa']
            max_score = row['Score_Tertinggi']
            min_score = row['Score_Terendah']
            avg_score = row['Rata_Rata']
            
            print(f"{i}. {jurusan}")
            print(f"   Total: {total:2d} siswa | Max: {max_score:5.1f} | Min: {min_score:5.1f} | Avg: {avg_score:5.1f}")
        
        # Show Streamlit features
        print(f"\n" + "="*100)
        print("🌐 FITUR YANG TERSEDIA DI STREAMLIT")
        print("="*100)
        
        features = [
            "📋 Tab khusus 'Top 50 per Jurusan'",
            "📊 Ringkasan statistik semua jurusan",
            "🎓 Dropdown untuk memilih jurusan",
            "📈 Statistik detail per jurusan (total siswa, score range, rata-rata)",
            "🏆 Tabel lengkap top 50 siswa per jurusan",
            "📥 Download button untuk setiap jurusan (format CSV)",
            "📊 Tabel perbandingan semua jurusan",
            "📥 Download perbandingan jurusan (format CSV)",
            "🔍 Kolom lengkap: Ranking, Registration Number, Name, Score, School, Date"
        ]
        
        for feature in features:
            print(f"  ✅ {feature}")
        
        print(f"\n🚀 CARA MENGGUNAKAN:")
        print("  1. Buka browser ke http://localhost:8505")
        print("  2. Klik tab '🏆 Top 50 per Jurusan'")
        print("  3. Lihat ringkasan semua jurusan")
        print("  4. Pilih jurusan dari dropdown")
        print("  5. Lihat tabel top 50 siswa untuk jurusan tersebut")
        print("  6. Download CSV jika diperlukan")
        print("  7. Lihat perbandingan semua jurusan di bagian bawah")
        
        print(f"\n🎉 FITUR SIAP DIGUNAKAN!")
        
    except FileNotFoundError:
        print("❌ File hasil_all_prestasi_rapor.csv tidak ditemukan!")
        print("Silakan jalankan scraping prestasi-rapor terlebih dahulu.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    show_feature_preview()

if __name__ == "__main__":
    main()
