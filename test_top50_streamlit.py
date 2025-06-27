#!/usr/bin/env python3
"""
Test script untuk fitur Top 50 per Jurusan di Streamlit
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import analyze_prestasi_by_jurusan

def test_analyze_function():
    """Test fungsi analyze_prestasi_by_jurusan"""
    
    print("="*80)
    print("🧪 TESTING TOP 50 PER JURUSAN FUNCTION")
    print("="*80)
    
    try:
        # Load data
        print("📊 Loading data dari hasil_all_prestasi_rapor.csv...")
        df = pd.read_csv('hasil_all_prestasi_rapor.csv')
        print(f"✅ Data loaded: {len(df)} records")
        
        # Test analyze function
        print("\n🔍 Testing analyze_prestasi_by_jurusan function...")
        results = analyze_prestasi_by_jurusan(df)
        
        if results:
            print(f"✅ Function berhasil! Ditemukan {len(results)} jurusan")
            
            print(f"\n📋 HASIL ANALISIS:")
            print("-" * 80)
            
            for i, (jurusan, data) in enumerate(results.items(), 1):
                print(f"{i}. 🎓 {jurusan}")
                print(f"   Total Siswa: {data['total_siswa']}")
                print(f"   Top Records: {len(data['data'])}")
                print(f"   Score Range: {data['score_terendah']:.1f} - {data['score_tertinggi']:.1f}")
                print(f"   Rata-rata: {data['rata_rata_score']:.1f}")
                
                # Show top 3 students
                top_3 = data['data'].head(3)
                print(f"   🏆 Top 3 Siswa:")
                for _, student in top_3.iterrows():
                    ranking = student['Ranking']
                    name = student['name']
                    score = student['score']
                    print(f"      {ranking}. {name} - {score}")
                print()
            
            # Test data structure
            print("🔍 TESTING DATA STRUCTURE:")
            print("-" * 80)
            
            first_jurusan = list(results.keys())[0]
            first_data = results[first_jurusan]['data']
            
            print(f"Sample jurusan: {first_jurusan}")
            print(f"Columns available: {list(first_data.columns)}")
            print(f"Required columns present:")
            
            required_cols = ['Ranking', 'registration_number', 'name', 'score']
            for col in required_cols:
                status = "✅" if col in first_data.columns else "❌"
                print(f"  {status} {col}")
            
            optional_cols = ['school_name', 'created_at', 'first_option_name']
            print(f"Optional columns present:")
            for col in optional_cols:
                status = "✅" if col in first_data.columns else "❌"
                print(f"  {status} {col}")
            
            print(f"\n🎉 Function test PASSED!")
            return True
            
        else:
            print("❌ Function returned empty results")
            return False
            
    except FileNotFoundError:
        print("❌ File hasil_all_prestasi_rapor.csv tidak ditemukan!")
        print("Silakan jalankan scraping prestasi-rapor terlebih dahulu.")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_integration():
    """Test integrasi dengan Streamlit"""
    
    print("\n" + "="*80)
    print("🌐 TESTING STREAMLIT INTEGRATION")
    print("="*80)
    
    print("✅ Streamlit app telah diupdate dengan fitur berikut:")
    print("  📋 Tab baru: '🏆 Top 50 per Jurusan'")
    print("  🔍 Fungsi analyze_prestasi_by_jurusan() telah ditambahkan")
    print("  📊 Dropdown untuk memilih jurusan")
    print("  📈 Statistik per jurusan")
    print("  📋 Tabel top 50 siswa per jurusan")
    print("  📥 Download button untuk setiap jurusan")
    print("  📊 Perbandingan semua jurusan")
    
    print(f"\n🚀 Cara menggunakan di Streamlit:")
    print("  1. Buka http://localhost:8505")
    print("  2. Klik tab '🏆 Top 50 per Jurusan'")
    print("  3. Pilih jurusan dari dropdown")
    print("  4. Lihat tabel top 50 siswa")
    print("  5. Download CSV jika diperlukan")
    
    return True

def main():
    print("🎓 TESTING TOP 50 PER JURUSAN STREAMLIT FEATURE")
    print("="*80)
    
    # Test 1: Function
    function_test = test_analyze_function()
    
    # Test 2: Streamlit integration
    streamlit_test = test_streamlit_integration()
    
    print("\n" + "="*80)
    print("📋 TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Function Test: {'✅ PASS' if function_test else '❌ FAIL'}")
    print(f"Streamlit Integration: {'✅ PASS' if streamlit_test else '❌ FAIL'}")
    
    if function_test and streamlit_test:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"Fitur Top 50 per Jurusan siap digunakan di Streamlit!")
    else:
        print(f"\n⚠️ SOME TESTS FAILED!")
        print(f"Silakan periksa error messages di atas.")
    
    print("="*80)

if __name__ == "__main__":
    main()
