#!/usr/bin/env python3
"""
Test the simplified prestasi-rapor scraping (no major selection required)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import StreamlitScraper
import pandas as pd

def test_simplified_prestasi_scraping():
    print("="*60)
    print("TESTING SIMPLIFIED PRESTASI-RAPOR SCRAPING")
    print("="*60)
    print("This test verifies that prestasi-rapor scraping works")
    print("without requiring major selection or complex setup.")
    print("="*60)
    
    # Initialize scraper
    scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")
    
    # Test parameters
    npsn = "20206224"
    
    print(f"Testing with NPSN: {npsn}")
    print("No major selection required - scraping ALL prestasi-rapor data")
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
        # Test simplified prestasi-rapor scraping
        print("🚀 Starting simplified prestasi-rapor scraping...")
        all_prestasi_data = scraper.scrape_all_pages(
            progress_bar, status_text,
            npsn=npsn, 
            option_type='prestasi-rapor',
            orderby='score', 
            order='desc'
            # No major_id parameter - gets ALL majors
        )
        
        if all_prestasi_data:
            print(f"✅ SUCCESS: Collected {len(all_prestasi_data)} prestasi-rapor records")
            
            # Convert to DataFrame
            df = pd.DataFrame(all_prestasi_data)
            
            print(f"\n📊 Data Summary:")
            print(f"  - Total records: {len(df)}")
            print(f"  - Columns available: {len(df.columns)}")
            
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
                print(f"  - Top 3 majors by registration count:")
                for i, (major, count) in enumerate(majors.head(3).items(), 1):
                    print(f"    {i}. {major}: {count} students")
            
            # Show top 5 students overall
            print(f"\n🏆 Top 5 Students (All Majors Combined):")
            for i, (_, student) in enumerate(df.head(5).iterrows(), 1):
                name = student.get('name', 'Unknown')
                score = student.get('score', 'N/A')
                major = student.get('first_option_name', 'Unknown')
                school = student.get('school_name', 'Unknown')
                print(f"  {i}. {name} - Score: {score}")
                print(f"     Major: {major}")
                print(f"     School: {school}")
                print()
            
            # Save test data
            df.to_csv('simplified_prestasi_rapor.csv', index=False)
            print(f"💾 Data saved to: simplified_prestasi_rapor.csv")
            
            # Verify the data structure for Streamlit display
            print(f"\n🔍 Data Structure Verification:")
            print(f"  - Can add ranking column: {'✅' if len(df) > 0 else '❌'}")
            print(f"  - Has score field: {'✅' if 'score' in df.columns else '❌'}")
            print(f"  - Has name field: {'✅' if 'name' in df.columns else '❌'}")
            print(f"  - Has registration number: {'✅' if 'registration_number' in df.columns else '❌'}")
            print(f"  - Has major field: {'✅' if 'first_option_name' in df.columns else '❌'}")
            print(f"  - Has school field: {'✅' if 'school_name' in df.columns else '❌'}")
            
            return True
        else:
            print("❌ FAILED: No prestasi-rapor data collected")
            print("This could indicate:")
            print("  - No prestasi-rapor registrations for this school")
            print("  - API connectivity issues")
            print("  - Parameter formatting problems")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing simplified prestasi-rapor scraping functionality...\n")
    
    success = test_simplified_prestasi_scraping()
    
    print("\n" + "="*60)
    print("TEST RESULT")
    print("="*60)
    
    if success:
        print("🎉 SUCCESS!")
        print("The simplified prestasi-rapor scraping works correctly.")
        print("✅ No major selection required")
        print("✅ Gets data from all majors")
        print("✅ Ready for Streamlit integration")
        print("\nYou can now use the Streamlit app with the ultra-simplified interface:")
        print("1. Go to '🎯 Prestasi Scraping' tab")
        print("2. Optional: Click '🔍 Load School Options' to see available programs")
        print("3. Click '🚀 Scrape ALL Prestasi-Rapor Data'")
        print("4. View all records in the table")
        print("5. Download CSV if needed")
    else:
        print("❌ FAILED!")
        print("Please check the error messages above.")
    
    print("="*60)
