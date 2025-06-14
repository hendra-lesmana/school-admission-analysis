import requests
import csv
import json
import time
from typing import Dict, List, Optional

class PaginatedScraper:
    def __init__(self, base_url: str, output_file: str = "hasil_paginated_sorted.csv"):
        self.base_url = base_url
        self.output_file = output_file
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
            'pagination': 'true',
            'columns[0][key]': 'name',
            'columns[0][searchable]': 'false',
            'columns[1][key]': 'registration_number',
            'columns[1][searchable]': 'true',
            'npsn': '20227910',
            'filters[1][key]': 'option_type',
            'filters[1][value]': 'zonasi'
        }
        
        try:
            print(f"Fetching page {page}...")
            response = self.session.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == 200:
                return data
            else:
                print(f"API returned error code: {data.get('code')} - {data.get('message')}")
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
        
        print("Starting paginated scraping...")
        print(f"API URL: {self.base_url}")
        print(f"Parameters: orderby=distance_1, order=asc, npsn=20227910, option_type=zonasi")
        print("-" * 60)
        
        while True:
            # Fetch current page
            page_data = self.fetch_page(page, limit_per_page)
            
            if page_data is None:
                print(f"Failed to fetch page {page}. Stopping.")
                break
            
            # Extract records from the response
            records = page_data.get('result', {}).get('data', [])
            
            if not records:
                print(f"No more data found on page {page}. Scraping complete.")
                break
            
            # Add records to our collection
            all_data.extend(records)
            
            # Get pagination info
            pagination = page_data.get('result', {}).get('pagination', {})
            total_pages = pagination.get('total_pages', 0)
            total_records = pagination.get('total_records', 0)
            current_page = pagination.get('current_page', page)
            
            print(f"✓ Page {current_page}/{total_pages} - Found {len(records)} records")
            print(f"  Total records so far: {len(all_data)}/{total_records}")
            
            # Check if we've reached the last page
            if current_page >= total_pages:
                print(f"Reached last page ({total_pages}). Scraping complete.")
                break
            
            # Move to next page
            page += 1
            
            # Rate limiting
            time.sleep(delay)
        
        print(f"\nScraping Summary:")
        print(f"Total records collected: {len(all_data)}")
        
        return all_data
    
    def save_to_csv(self, data_list: List[Dict]):
        """Save the collected data to CSV file (already sorted by distance_1)"""
        if not data_list:
            print("No data to save.")
            return
        
        # Define CSV headers based on the API response structure
        headers = [
            'registration_number', 'name', 'school_name', 'option_type',
            'first_option_name', 'second_option_name', 'third_option_name',
            'distance_1', 'distance_2', 'distance_3',
            'score', 'score_a1', 'score_a2', 'score_a3',
            'score_kejuaraan', 'score_ujikom', 'created_at',
            'address_city', 'address_district', 'address_subdistrict'
        ]
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for data in data_list:
                # Ensure all fields are present, use empty string for missing fields
                row = {header: data.get(header, '') for header in headers}
                writer.writerow(row)
        
        print(f"✓ Saved {len(data_list)} records to {self.output_file}")
        print(f"✓ Data is already sorted by distance_1 (ascending)")
    
    def display_summary(self, data_list: List[Dict]):
        """Display summary statistics of the scraped data"""
        if not data_list:
            return
        
        print(f"\n{'='*60}")
        print(f"DATA SUMMARY")
        print(f"{'='*60}")
        print(f"Total students found: {len(data_list)}")
        
        # Show top 10 closest distances
        print(f"\nTop 10 closest distances:")
        for i, record in enumerate(data_list[:10]):
            name = record.get('name', 'Unknown')
            distance = record.get('distance_1', 'N/A')
            reg_num = record.get('registration_number', 'Unknown')
            print(f"{i+1:2d}. {name} - {distance}m (Reg: {reg_num})")
        
        # Show distance statistics
        distances = []
        for record in data_list:
            try:
                dist = float(record.get('distance_1', 0))
                distances.append(dist)
            except (ValueError, TypeError):
                continue
        
        if distances:
            print(f"\nDistance Statistics:")
            print(f"  Closest: {min(distances):.1f}m")
            print(f"  Furthest: {max(distances):.1f}m")
            print(f"  Average: {sum(distances)/len(distances):.1f}m")
        
        print(f"{'='*60}")

def main():
    # API URL for paginated results
    api_url = "https://spmb.jabarprov.go.id/api/public/registration"
    
    # Initialize scraper
    scraper = PaginatedScraper(api_url)
    
    print("="*60)
    print("PAGINATED API SCRAPER")
    print("="*60)
    print("This script will scrape all registration data using the paginated API.")
    print("Data will be automatically sorted by distance_1 (ascending).")
    print("="*60)
    
    try:
        # Scrape all pages
        all_data = scraper.scrape_all_pages(limit_per_page=100, delay=1.0)
        
        if all_data:
            # Save to CSV
            scraper.save_to_csv(all_data)
            
            # Display summary
            scraper.display_summary(all_data)
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"📁 Results saved to: {scraper.output_file}")
        else:
            print("❌ No data was collected.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
