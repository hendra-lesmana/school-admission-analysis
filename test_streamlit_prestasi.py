#!/usr/bin/env python3
"""
Quick test to verify prestasi-rapor scraping works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import StreamlitScraper
import pandas as pd

def test_prestasi_scraping():
    print("="*60)
    print("TESTING PRESTASI-RAPOR SCRAPING (WITH MAJOR ID)")
    print("="*60)

    # Initialize scraper
    scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")

    # Test parameters
    npsn = "20206224"
    major_id = "76f45f15-8af2-40fd-a79a-426b46c67649"

    print(f"Testing with NPSN: {npsn}")
    print(f"Testing with Major ID: {major_id}")
    print("-" * 60)
    
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
        # Test prestasi-rapor scraping
        print("🎯 Starting prestasi-rapor scraping test...")
        prestasi_data = scraper.scrape_all_pages(
            progress_bar, status_text,
            npsn=npsn, 
            option_type='prestasi-rapor',
            orderby='score', 
            order='desc',
            major_id=major_id
        )
        
        if prestasi_data:
            print(f"✅ SUCCESS: Collected {len(prestasi_data)} prestasi-rapor records")
            
            # Convert to DataFrame
            df = pd.DataFrame(prestasi_data)
            
            print(f"\n📊 Data Summary:")
            print(f"  - Total records: {len(df)}")
            print(f"  - Columns: {list(df.columns)}")
            
            # Check key fields
            if 'score' in df.columns:
                scores = df['score'].dropna()
                if len(scores) > 0:
                    print(f"  - Score range: {scores.min():.1f} - {scores.max():.1f}")
                    print(f"  - Average score: {scores.mean():.1f}")
                else:
                    print(f"  - No valid scores found")
            
            if 'option_type' in df.columns:
                option_types = df['option_type'].value_counts()
                print(f"  - Option types: {dict(option_types)}")
            
            # Show top 5 students
            print(f"\n🏆 Top 5 Students:")
            for i, (_, student) in enumerate(df.head(5).iterrows(), 1):
                name = student.get('name', 'Unknown')
                score = student.get('score', 'N/A')
                school = student.get('school_name', 'Unknown')
                print(f"  {i}. {name} - Score: {score} - {school}")
            
            # Save test data
            df.to_csv('test_prestasi_rapor.csv', index=False)
            print(f"\n💾 Test data saved to: test_prestasi_rapor.csv")
            
            return True
        else:
            print("❌ FAILED: No prestasi-rapor data collected")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_all_prestasi_scraping():
    print("\n" + "="*60)
    print("TESTING ALL PRESTASI-RAPOR SCRAPING (NO MAJOR ID)")
    print("="*60)

    # Initialize scraper
    scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")

    # Test parameters
    npsn = "20206224"

    print(f"Testing with NPSN: {npsn}")
    print("No Major ID filter - scraping ALL prestasi-rapor data")
    print("-" * 60)

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
        # Test ALL prestasi-rapor scraping (no major_id)
        print("🎯 Starting ALL prestasi-rapor scraping test...")
        all_prestasi_data = scraper.scrape_all_pages(
            progress_bar, status_text,
            npsn=npsn,
            option_type='prestasi-rapor',
            orderby='score',
            order='desc'
            # No major_id parameter
        )

        if all_prestasi_data:
            print(f"✅ SUCCESS: Collected {len(all_prestasi_data)} ALL prestasi-rapor records")

            # Convert to DataFrame
            df = pd.DataFrame(all_prestasi_data)

            print(f"\n📊 Data Summary:")
            print(f"  - Total records: {len(df)}")
            print(f"  - Columns: {list(df.columns)}")

            # Check key fields
            if 'score' in df.columns:
                scores = df['score'].dropna()
                if len(scores) > 0:
                    print(f"  - Score range: {scores.min():.1f} - {scores.max():.1f}")
                    print(f"  - Average score: {scores.mean():.1f}")
                else:
                    print(f"  - No valid scores found")

            # Check majors/options
            if 'first_option_name' in df.columns:
                majors = df['first_option_name'].value_counts()
                print(f"  - Number of different majors: {len(majors)}")
                print(f"  - Top 3 majors:")
                for major, count in majors.head(3).items():
                    print(f"    * {major}: {count} students")

            if 'option_type' in df.columns:
                option_types = df['option_type'].value_counts()
                print(f"  - Option types: {dict(option_types)}")

            # Show top 5 students
            print(f"\n🏆 Top 5 Students (All Majors):")
            for i, (_, student) in enumerate(df.head(5).iterrows(), 1):
                name = student.get('name', 'Unknown')
                score = student.get('score', 'N/A')
                major = student.get('first_option_name', 'Unknown')
                school = student.get('school_name', 'Unknown')
                print(f"  {i}. {name} - Score: {score}")
                print(f"     Major: {major}")
                print(f"     School: {school}")

            # Save test data
            df.to_csv('test_all_prestasi_rapor.csv', index=False)
            print(f"\n💾 Test data saved to: test_all_prestasi_rapor.csv")

            return True
        else:
            print("❌ FAILED: No ALL prestasi-rapor data collected")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_school_options():
    print("\n" + "="*60)
    print("TESTING SCHOOL OPTIONS API")
    print("="*60)
    
    scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")
    npsn = "20206224"
    
    try:
        school_data = scraper.fetch_school_options(npsn)
        
        if school_data:
            school_info = school_data['result']
            print(f"✅ SUCCESS: Retrieved school information")
            print(f"  - School: {school_info.get('name', 'Unknown')}")
            print(f"  - Address: {school_info.get('address', 'Unknown')}")
            
            # Check statistics
            stats = school_info.get('statistics', [])
            if isinstance(stats, list):
                prestasi_options = [s for s in stats if 'PRESTASI NILAI RAPOR' in s.get('option', '')]
                print(f"  - Total program options: {len(stats)}")
                print(f"  - Prestasi-rapor options: {len(prestasi_options)}")
                
                if prestasi_options:
                    print(f"\n📋 Prestasi-Rapor Programs:")
                    for i, option in enumerate(prestasi_options[:3], 1):
                        name = option.get('option', 'Unknown')
                        registrations = option.get('total_registration', 0)
                        print(f"  {i}. {name}")
                        print(f"     Registrations: {registrations}")
            
            return True
        else:
            print("❌ FAILED: Could not retrieve school options")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive prestasi-rapor integration test...\n")

    # Test school options first
    options_success = test_school_options()

    # Test prestasi scraping with major_id
    scraping_success = test_prestasi_scraping()

    # Test ALL prestasi scraping (no major_id)
    all_scraping_success = test_all_prestasi_scraping()

    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    print(f"School Options API: {'✅ PASS' if options_success else '❌ FAIL'}")
    print(f"Prestasi-Rapor Scraping (with major_id): {'✅ PASS' if scraping_success else '❌ FAIL'}")
    print(f"ALL Prestasi-Rapor Scraping (no major_id): {'✅ PASS' if all_scraping_success else '❌ FAIL'}")

    if options_success and scraping_success and all_scraping_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"Both targeted and comprehensive prestasi-rapor scraping work correctly.")
        print(f"You can now use the Streamlit app to scrape prestasi-rapor data with or without major selection.")
    else:
        print(f"\n⚠️ SOME TESTS FAILED!")
        print(f"Please check the error messages above.")

    print("="*60)
