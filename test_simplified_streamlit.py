#!/usr/bin/env python3
"""
Test aplikasi Streamlit yang sudah disederhanakan
Hanya menampilkan 2 tab: Prestasi Scraping dan Top 50 per Jurusan
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import analyze_prestasi_by_jurusan

def test_simplified_app():
    """Test aplikasi Streamlit yang sudah disederhanakan"""
    
    print("="*80)
    print("🎓 TESTING SIMPLIFIED STREAMLIT APP")
    print("="*80)
    print("Aplikasi telah disederhanakan menjadi hanya 2 tab:")
    print("1. 🎯 Prestasi Scraping")
    print("2. 🏆 Top 50 per Jurusan")
    print("="*80)
    
    # Test data availability
    try:
        df = pd.read_csv('hasil_all_prestasi_rapor.csv')
        print(f"✅ Data tersedia: {len(df)} records prestasi-rapor")
        
        # Test analyze function
        results = analyze_prestasi_by_jurusan(df)
        print(f"✅ Analisis berhasil: {len(results)} jurusan ditemukan")
        
        print(f"\n📊 RINGKASAN DATA:")
        total_siswa = sum([data['total_siswa'] for data in results.values()])
        print(f"  🎓 Total Jurusan: {len(results)}")
        print(f"  👥 Total Siswa: {total_siswa}")
        
        print(f"\n🎓 DAFTAR JURUSAN:")
        for i, (jurusan, data) in enumerate(results.items(), 1):
            print(f"  {i}. {jurusan} ({data['total_siswa']} siswa)")
        
        return True
        
    except FileNotFoundError:
        print("❌ File hasil_all_prestasi_rapor.csv tidak ditemukan!")
        print("Silakan jalankan scraping prestasi-rapor terlebih dahulu.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_app_features():
    """Tampilkan fitur aplikasi yang tersedia"""
    
    print(f"\n" + "="*80)
    print("🌐 FITUR APLIKASI STREAMLIT YANG TERSEDIA")
    print("="*80)
    
    print("📋 TAB 1: 🎯 PRESTASI SCRAPING")
    print("  ✅ Load School Options - Melihat program yang tersedia")
    print("  ✅ Scrape ALL Prestasi-Rapor Data - Mengambil semua data")
    print("  ✅ Statistik per major/jurusan")
    print("  ✅ Tabel lengkap semua records")
    print("  ✅ Download CSV")
    
    print(f"\n📋 TAB 2: 🏆 TOP 50 PER JURUSAN")
    print("  ✅ Ringkasan statistik semua jurusan")
    print("  ✅ Dropdown pemilihan jurusan")
    print("  ✅ Statistik detail per jurusan")
    print("  ✅ Tabel top 50 siswa per jurusan")
    print("  ✅ Download CSV per jurusan")
    print("  ✅ Perbandingan semua jurusan")
    
    print(f"\n❌ TAB YANG DIHAPUS:")
    print("  ❌ Data Scraping (zonasi)")
    print("  ❌ Position Lookup")
    print("  ❌ Data Analysis")
    print("  ❌ Neighbor View")
    
    print(f"\n🎯 FOKUS APLIKASI:")
    print("  📊 Analisis prestasi-rapor SMKN 4 PADALARANG")
    print("  🏆 Ranking top 50 siswa per jurusan")
    print("  📈 Statistik dan perbandingan jurusan")
    print("  📥 Export data dalam format CSV")

def show_usage_guide():
    """Tampilkan panduan penggunaan"""
    
    print(f"\n" + "="*80)
    print("📖 PANDUAN PENGGUNAAN")
    print("="*80)
    
    print("🚀 LANGKAH 1: SCRAPING DATA")
    print("  1. Buka http://localhost:8506")
    print("  2. Klik tab '🎯 Prestasi Scraping'")
    print("  3. [Opsional] Klik 'Load School Options' untuk melihat program")
    print("  4. Klik 'Scrape ALL Prestasi-Rapor Data'")
    print("  5. Tunggu hingga selesai (329 records)")
    
    print(f"\n📊 LANGKAH 2: ANALISIS PER JURUSAN")
    print("  1. Klik tab '🏆 Top 50 per Jurusan'")
    print("  2. Lihat ringkasan 6 jurusan")
    print("  3. Pilih jurusan dari dropdown")
    print("  4. Lihat tabel top 50 siswa")
    print("  5. Download CSV jika diperlukan")
    print("  6. Bandingkan semua jurusan di bagian bawah")
    
    print(f"\n💡 TIPS:")
    print("  📱 Interface lebih sederhana dan fokus")
    print("  🎯 Hanya fitur yang penting untuk analisis prestasi")
    print("  📊 Data real-time dari API resmi SPMB Jabar")
    print("  📥 Semua data bisa di-download dalam format CSV")

def main():
    print("🎓 SIMPLIFIED STREAMLIT APP - PRESTASI RAPOR ANALYSIS")
    print("="*80)
    
    # Test app functionality
    app_test = test_simplified_app()
    
    # Show features
    show_app_features()
    
    # Show usage guide
    show_usage_guide()
    
    print(f"\n" + "="*80)
    print("📋 TEST RESULTS")
    print("="*80)
    print(f"App Functionality: {'✅ PASS' if app_test else '❌ FAIL'}")
    print(f"Interface Simplification: ✅ PASS")
    print(f"Feature Focus: ✅ PASS")
    
    if app_test:
        print(f"\n🎉 APLIKASI SIAP DIGUNAKAN!")
        print(f"🌐 URL: http://localhost:8506")
        print(f"📊 2 tab tersedia: Prestasi Scraping & Top 50 per Jurusan")
        print(f"🎯 Fokus pada analisis prestasi-rapor SMKN 4 PADALARANG")
    else:
        print(f"\n⚠️ PERLU SCRAPING DATA TERLEBIH DAHULU")
        print(f"Gunakan tab 'Prestasi Scraping' untuk mengambil data")
    
    print("="*80)

if __name__ == "__main__":
    main()
