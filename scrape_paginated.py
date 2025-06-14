import requests
import csv
import json
import time
from typing import Dict, List, Optional

class PaginatedScraper:
    def __init__(self, base_url: str, output_file: str = "hasil_paginated_sorted.csv", zonasi_only_file: str = "hasil_zonasi_only.csv"):
        self.base_url = base_url
        self.output_file = output_file
        self.zonasi_only_file = zonasi_only_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://spmb.jabarprov.go.id/'
        })
    
    def fetch_page(self, page: int = 1, limit: int = 100) -> Optional[Dict]:
        """Fetch a single page of data from the API"""
        params = {
            'page': page,
            'limit': limit,
            'orderby': 'distance_1',
            'order': 'asc',
            'npsn': '20227910'
        }
        
        try:
            print(f"Fetching page {page}...")
            response = self.session.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 200:
                return data
            else:
                print(f"API returned error code: {data.get('code')} - {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for page {page}: {e}")
            return None
    
    def scrape_all_pages(self, limit_per_page: int = 100, delay: float = 1.0) -> List[Dict]:
        """Scrape all pages of data"""
        all_data = []
        page = 1
        total_pages = None
        
        print("Starting paginated scraping...")
        print(f"API URL: {self.base_url}")
        print(f"Parameters: NPSN=20227910, option_type=zonasi, sorted by distance_1 ascending")
        
        while True:
            # Fetch current page
            page_data = self.fetch_page(page, limit_per_page)
            
            if page_data is None:
                print(f"Failed to fetch page {page}. Stopping.")
                break
            
            # Extract data from API response
            result = page_data.get('result', {})
            data_items = result.get('itemsList', [])

            # For this API, we need to check if we got fewer items than requested
            # which indicates we've reached the end
            
            if total_pages is None and data_items:
                # Estimate total pages based on first response
                print(f"Starting pagination (will continue until no more data)")
            
            # Add data from this page
            if data_items:
                all_data.extend(data_items)
                print(f"✓ Page {page}: Found {len(data_items)} records (Total so far: {len(all_data)})")

                # If we got fewer items than requested, we've reached the end
                if len(data_items) < limit_per_page:
                    print(f"Reached end of data (got {len(data_items)} < {limit_per_page} requested)")
                    break
            else:
                print(f"No data found on page {page}")
                break
            
            # Move to next page
            page += 1
            
            # Rate limiting
            time.sleep(delay)
        
        print(f"\nScraping completed! Total records collected: {len(all_data)}")
        return all_data
    
    def save_to_csv(self, data_list: List[Dict]):
        """Save the collected data to CSV file (already sorted by distance_1)"""
        if not data_list:
            print("No data to save.")
            return

        # Define CSV headers based on the expected API response structure
        headers = [
            'registration_number', 'name', 'school_name', 'option_type',
            'first_option_name', 'second_option_name', 'third_option_name',
            'distance_1', 'distance_2', 'distance_3',
            'score', 'score_a1', 'score_a2', 'score_a3',
            'score_kejuaraan', 'score_ujikom', 'created_at',
            'address_city', 'address_district', 'address_subdistrict'
        ]

        # Save all data to main file
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for i, data in enumerate(data_list, 1):
                # Ensure all fields are present, use empty string for missing fields
                row = {header: data.get(header, '') for header in headers}
                writer.writerow(row)

        print(f"✓ Saved {len(data_list)} records to {self.output_file}")

        # Filter and save only zonasi data
        zonasi_data = [record for record in data_list if record.get('option_type') == 'zonasi']

        if zonasi_data:
            with open(self.zonasi_only_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()

                for data in zonasi_data:
                    # Ensure all fields are present, use empty string for missing fields
                    row = {header: data.get(header, '') for header in headers}
                    writer.writerow(row)

            print(f"✓ Saved {len(zonasi_data)} ZONASI records to {self.zonasi_only_file}")
            print(f"✓ Data is already sorted by distance_1 (ascending)")

            # Show statistics
            ketm_data = [record for record in data_list if record.get('option_type') == 'ketm']
            print(f"\n📊 Data Summary:")
            print(f"   Total records: {len(data_list)}")
            print(f"   Zonasi (distance-based): {len(zonasi_data)}")
            print(f"   KETM (achievement-based): {len(ketm_data)}")

            # Show top 10 closest distances for zonasi only
            print(f"\n🏆 Top 10 closest distances (ZONASI only):")
            for i, record in enumerate(zonasi_data[:10], 1):
                name = record.get('name', 'Unknown')
                distance = record.get('distance_1', 'N/A')
                reg_number = record.get('registration_number', 'Unknown')
                print(f"{i:2d}. {name} ({reg_number}) - {distance}m")
        else:
            print("⚠️ No zonasi records found in the data.")
    
    def find_registration_position(self, registration_number: str, quota: int = 139) -> Optional[Dict]:
        """Find position of a registration number in the saved results (zonasi only)"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)

            # Filter only zonasi records for position calculation
            zonasi_data = [record for record in data if record.get('option_type') == 'zonasi']

            for i, record in enumerate(zonasi_data):
                if record['registration_number'] == registration_number:
                    position = i + 1

                    # Calculate acceptance probability based on zonasi position only
                    if position <= quota:
                        if position <= quota * 0.3:
                            probability = 95.0
                            status = "SANGAT TINGGI"
                        elif position <= quota * 0.6:
                            probability = 85.0
                            status = "TINGGI"
                        else:
                            probability = 75.0
                            status = "SEDANG-TINGGI"
                    elif position <= quota * 1.2:
                        probability = 40.0
                        status = "RENDAH"
                    else:
                        probability = 10.0
                        status = "SANGAT RENDAH"

                    return {
                        'position': position,
                        'total_zonasi': len(zonasi_data),
                        'total_all': len(data),
                        'quota': quota,
                        'probability': round(probability, 1),
                        'status': status,
                        'student_data': record
                    }

            return None

        except FileNotFoundError:
            print(f"Results file {self.output_file} not found.")
            return None

    def show_neighbors(self, target_registration: str, neighbors: int = 5):
        """Show students positioned around a target registration number"""
        try:
            # Read zonasi-only data
            with open(self.zonasi_only_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                zonasi_data = list(reader)

            # Find the target registration number
            target_position = None
            target_record = None

            for i, record in enumerate(zonasi_data):
                if record['registration_number'] == target_registration:
                    target_position = i
                    target_record = record
                    break

            if target_position is None:
                print(f"\n❌ Registration {target_registration} not found in zonasi data")
                return

            # Calculate range
            start_idx = max(0, target_position - neighbors)
            end_idx = min(len(zonasi_data), target_position + neighbors + 1)

            print(f"\n{'='*100}")
            print(f"🎯 STUDENTS AROUND REGISTRATION: {target_registration}")
            print(f"{'='*100}")
            print(f"📍 Target: #{target_position + 1} - {target_record.get('name', 'Unknown')} - {target_record.get('distance_1', 'N/A')}m")

            print(f"\n📊 NEIGHBORS (Showing {neighbors} above and {neighbors} below)")
            print(f"{'-'*100}")
            print(f"{'Pos':<4} {'Registration':<20} {'Name':<25} {'Distance':<10} {'School':<25}")
            print(f"{'-'*100}")

            # Show students in range
            for i in range(start_idx, end_idx):
                record = zonasi_data[i]
                position = i + 1
                reg_num = record.get('registration_number', '')
                name = record.get('name', '')[:24]  # Truncate long names
                distance = record.get('distance_1', '')
                school = record.get('school_name', '')[:24]  # Truncate long school names

                # Highlight the target registration
                if record['registration_number'] == target_registration:
                    print(f"🎯 {position:<3} {reg_num:<20} {name:<25} {distance:<10} {school:<25}")
                else:
                    # Show position relative to target
                    diff = position - (target_position + 1)
                    if diff < 0:
                        indicator = f"↑{abs(diff)}"
                    elif diff > 0:
                        indicator = f"↓{diff}"
                    else:
                        indicator = "🎯"

                    print(f"{indicator:<3} {position:<3} {reg_num:<20} {name:<25} {distance:<10} {school:<25}")

            print(f"{'-'*100}")

            # Quick analysis
            quota = 139
            if target_position + 1 <= quota:
                status = "✅ DALAM KUOTA"
                remaining = quota - (target_position + 1)
                print(f"Status: {status} ({remaining} slots remaining)")
            else:
                status = "⚠️ DI LUAR KUOTA"
                excess = (target_position + 1) - quota
                print(f"Status: {status} (+{excess} beyond quota)")

            print(f"{'='*100}")

        except FileNotFoundError:
            print(f"\n❌ Zonasi file {self.zonasi_only_file} not found.")
        except Exception as e:
            print(f"\n❌ Error showing neighbors: {e}")

def main():
    # API URL for paginated results
    api_url = "https://spmb.jabarprov.go.id/api/public/registration"
    
    # Initialize scraper
    scraper = PaginatedScraper(api_url)
    
    try:
        # Scrape all pages
        all_data = scraper.scrape_all_pages(limit_per_page=100, delay=1.0)
        
        if all_data:
            # Save to CSV
            scraper.save_to_csv(all_data)
            
            # Test lookup for the registration number from your selection
            test_registration = "20227910-16-1-00369"
            print(f"\n{'='*60}")
            print(f"Testing position lookup for: {test_registration}")
            print(f"{'='*60}")
            
            result = scraper.find_registration_position(test_registration)
            if result:
                student = result['student_data']
                print(f"Position (ZONASI only): #{result['position']} out of {result['total_zonasi']} zonasi students")
                print(f"Acceptance probability: {result['probability']}% ({result['status']})")
                print(f"Student: {student.get('name', 'Unknown')}")
                print(f"Distance: {student.get('distance_1', 'N/A')}m")

                # Show neighbors around the test registration
                scraper.show_neighbors(test_registration)
            else:
                print(f"Registration {test_registration} not found in results")
        
        else:
            print("No data was collected.")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
