#!/usr/bin/env python3
"""
Test script for the new prestasi-rapor API functionality
This script demonstrates how to:
1. Fetch school options and major IDs
2. Scrape prestasi-rapor data with major_id filtering
"""

import requests
import json
import pandas as pd
from typing import Dict, List, Optional

class PrestasiAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://spmb.jabarprov.go.id/'
        })
    
    def fetch_school_options(self, npsn: str) -> Optional[Dict]:
        """Fetch school options and major IDs from school API"""
        school_url = f"https://spmb.jabarprov.go.id/api/public/school/{npsn}?populate=options"
        
        try:
            print(f"Fetching school options for NPSN: {npsn}")
            response = self.session.get(school_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 200:
                print("✅ Successfully fetched school options")
                return data
            else:
                print(f"❌ School API returned error code: {data.get('code')} - {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching school options: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing school options JSON: {e}")
            return None
    
    def fetch_prestasi_data(self, npsn: str, major_id: str, page: int = 1, limit: int = 10) -> Optional[Dict]:
        """Fetch prestasi-rapor data with major_id filtering"""
        registration_url = "https://spmb.jabarprov.go.id/api/public/registration"

        params = {
            'page': page,
            'limit': limit,
            'orderby': 'score_a1',
            'order': 'desc',
            'pagination': 'true',
            'columns[0][key]': 'name',
            'columns[0][searchable]': 'false',
            'columns[1][key]': 'registration_number',
            'columns[1][searchable]': 'true',
            'npsn': npsn,
            'filters[1][key]': 'option_type',
            'filters[1][value]': 'prestasi-rapor',
            'major_id': major_id
        }

        try:
            print(f"Fetching prestasi-rapor data for NPSN: {npsn}, Major ID: {major_id}")
            print(f"Full URL: {registration_url}")
            print(f"Parameters: {params}")

            response = self.session.get(registration_url, params=params, timeout=15)
            print(f"Response status code: {response.status_code}")
            print(f"Response URL: {response.url}")

            response.raise_for_status()
            data = response.json()

            print(f"API Response code: {data.get('code')}")
            print(f"API Response message: {data.get('message', 'No message')}")

            if data.get('code') == 200:
                result = data.get('result', {})
                items = result.get('itemsList', [])
                pagination = result.get('pagination', {})

                print(f"✅ Successfully fetched prestasi-rapor data")
                print(f"Items found: {len(items)}")
                print(f"Pagination info: {pagination}")

                if len(items) == 0:
                    print("⚠️ No items returned - this might indicate:")
                    print("  1. No prestasi-rapor registrations for this major_id")
                    print("  2. Incorrect major_id")
                    print("  3. Different filtering requirements")

                return data
            else:
                print(f"❌ Registration API returned error code: {data.get('code')} - {data.get('message', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching prestasi-rapor data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing prestasi-rapor JSON: {e}")
            return None

    def fetch_prestasi_data_alternative(self, npsn: str, page: int = 1, limit: int = 10) -> Optional[Dict]:
        """Fetch prestasi-rapor data without major_id to test basic filtering"""
        registration_url = "https://spmb.jabarprov.go.id/api/public/registration"

        params = {
            'page': page,
            'limit': limit,
            'orderby': 'created_date',
            'order': 'desc',
            'pagination': 'true',
            'columns[0][key]': 'name',
            'columns[0][searchable]': 'false',
            'columns[1][key]': 'registration_number',
            'columns[1][searchable]': 'true',
            'npsn': npsn,
            'filters[1][key]': 'option_type',
            'filters[1][value]': 'prestasi-rapor'
            # No major_id parameter
        }

        try:
            print(f"Testing alternative approach - NPSN: {npsn} (no major_id)")
            print(f"Parameters: {params}")

            response = self.session.get(registration_url, params=params, timeout=15)
            print(f"Response status code: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            if data.get('code') == 200:
                result = data.get('result', {})
                items = result.get('itemsList', [])
                print(f"✅ Alternative approach successful - found {len(items)} items")
                return data
            else:
                print(f"❌ Alternative approach failed: {data.get('code')} - {data.get('message', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"❌ Alternative approach error: {e}")
            return None
    
    def display_school_info(self, school_data: Dict):
        """Display school information and statistics"""
        if not school_data or not school_data.get('result'):
            print("❌ No school data to display")
            return
        
        school_info = school_data['result']
        print("\n" + "="*60)
        print("SCHOOL INFORMATION")
        print("="*60)
        print(f"Name: {school_info.get('name', 'Unknown')}")
        print(f"NPSN: {school_info.get('npsn', 'Unknown')}")
        print(f"Address: {school_info.get('address', 'Unknown')}")
        
        # Display statistics if available
        stats = school_info.get('statistics', {})
        if stats and isinstance(stats, dict):
            print("\n📊 SCHOOL STATISTICS:")
            print(f"  Total Registrations: {stats.get('total_registrations', 0)}")
            print(f"  Verified: {stats.get('verified', 0)}")
            print(f"  Not Verified: {stats.get('not_verified', 0)}")
            print(f"  Canceled: {stats.get('canceled', 0)}")
        elif stats:
            print(f"\n📊 SCHOOL STATISTICS: {stats}")
        
        # Display available majors/options
        options = school_info.get('options', [])
        if options:
            print(f"\n🎓 AVAILABLE MAJORS ({len(options)} total):")
            for i, option in enumerate(options, 1):
                major_name = option.get('name', 'Unknown Major')
                major_id = option.get('id', 'No ID')
                print(f"  {i}. {major_name}")
                print(f"     ID: {major_id}")
        else:
            print("\n⚠️ No majors/options found for this school")

        # Also check if there are any prestasi-rapor options in statistics
        stats = school_info.get('statistics', [])
        if isinstance(stats, list):
            prestasi_options = [stat for stat in stats if 'PRESTASI NILAI RAPOR' in stat.get('option', '')]
            if prestasi_options:
                print(f"\n🎯 PRESTASI-RAPOR OPTIONS FOUND ({len(prestasi_options)} total):")
                for i, stat in enumerate(prestasi_options, 1):
                    option_name = stat.get('option', 'Unknown')
                    total_reg = stat.get('total_registration', 0)
                    print(f"  {i}. {option_name}")
                    print(f"     Registrations: {total_reg}")

                # Try to extract major ID from the first prestasi option
                if prestasi_options:
                    print(f"\n💡 Note: Major IDs need to be extracted from the options API response")
                    print("     The statistics show prestasi-rapor data is available for this school")
    
    def display_prestasi_data(self, prestasi_data: Dict):
        """Display prestasi-rapor data"""
        if not prestasi_data or not prestasi_data.get('result'):
            print("❌ No prestasi-rapor data to display")
            return
        
        result = prestasi_data['result']
        items = result.get('itemsList', [])
        pagination = result.get('pagination', {})
        
        print("\n" + "="*60)
        print("PRESTASI-RAPOR DATA")
        print("="*60)
        
        if pagination:
            print(f"Page: {pagination.get('current_page', 1)} of {pagination.get('total_pages', 1)}")
            print(f"Total Records: {pagination.get('total_records', 0)}")
            print(f"Records on this page: {len(items)}")
        
        if items:
            print(f"\n🏆 TOP {len(items)} STUDENTS (by Score A1):")
            print("-" * 60)

            # Show available fields in first record
            if len(items) > 0:
                print(f"📋 Available fields in student record:")
                first_student = items[0]
                for key, value in first_student.items():
                    print(f"  - {key}: {value}")
                print("-" * 60)

            for i, student in enumerate(items, 1):
                name = student.get('name', 'Unknown')
                reg_num = student.get('registration_number', 'Unknown')
                score_a1 = student.get('score_a1', 'N/A')
                score = student.get('score', 'N/A')
                school = student.get('school_name', 'Unknown')
                created_at = student.get('created_at', 'N/A')

                print(f"{i:2d}. {name}")
                print(f"    Registration: {reg_num}")
                print(f"    Score A1: {score_a1}")
                print(f"    Score: {score}")
                print(f"    School: {school}")
                print(f"    Created: {created_at}")
                print()
        else:
            print("⚠️ No prestasi-rapor records found")

def main():
    print("="*60)
    print("PRESTASI-RAPOR API TESTER")
    print("="*60)
    print("This script tests the new prestasi-rapor API functionality")
    print("="*60)
    
    # Initialize tester
    tester = PrestasiAPITester()
    
    # Test with the provided NPSN
    npsn = "20206224"
    
    # Step 1: Fetch school options
    print(f"\n🔍 Step 1: Fetching school options for NPSN {npsn}")
    school_data = tester.fetch_school_options(npsn)
    
    if school_data:
        tester.display_school_info(school_data)

        # Debug: Print the raw structure to understand the API response
        print(f"\n🔍 DEBUG: Raw API response structure:")
        school_info = school_data['result']
        print(f"Keys in school_info: {list(school_info.keys())}")

        # Check edges for options
        edges = school_info.get('edges', [])
        if edges:
            print(f"Found {len(edges)} edges")
            print(f"Edges type: {type(edges)}")
            if isinstance(edges, list) and len(edges) > 0:
                print(f"First edge: {edges[0]}")
            elif isinstance(edges, dict):
                print(f"Edges dict keys: {list(edges.keys())}")

        # Step 2: Try with the major ID from your original URL
        # From your URL: major_id=76f45f15-8af2-40fd-a79a-426b46c67649
        test_major_id = "76f45f15-8af2-40fd-a79a-426b46c67649"

        print(f"\n🎯 Step 2: Testing with provided major ID: {test_major_id}")
        prestasi_data = tester.fetch_prestasi_data(npsn, test_major_id, page=1, limit=10)

        if prestasi_data:
            tester.display_prestasi_data(prestasi_data)
        else:
            print("❌ Failed to fetch prestasi-rapor data with provided major ID")

            # Try alternative approaches
            print(f"\n🔍 Step 2b: Testing without major_id parameter")
            prestasi_data_alt = tester.fetch_prestasi_data_alternative(npsn, page=1, limit=10)

            if prestasi_data_alt:
                tester.display_prestasi_data(prestasi_data_alt)
            else:
                print("❌ Alternative approach also failed")

        # Step 3: Get major ID and fetch prestasi-rapor data from options
        options = school_info.get('options', [])
        
        if options:
            # Use the first available major for testing
            first_major = options[0]
            major_id = first_major.get('id')
            major_name = first_major.get('name', 'Unknown')

            if major_id:
                print(f"\n🎯 Step 3: Fetching prestasi-rapor data for major: {major_name}")
                prestasi_data = tester.fetch_prestasi_data(npsn, major_id, page=1, limit=10)

                if prestasi_data:
                    tester.display_prestasi_data(prestasi_data)
                else:
                    print("❌ Failed to fetch prestasi-rapor data")
            else:
                print("❌ No major ID found for the first major")
        else:
            print("⚠️ No majors in options field - this is expected based on API structure")
    else:
        print("❌ Failed to fetch school options")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()
