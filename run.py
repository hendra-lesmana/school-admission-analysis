import requests
import csv
import time
import json
from typing import Dict, Optional, List

class RegistrationScraper:
    def __init__(self, base_url: str, output_file: str = "hasil_valid.csv"):
        self.base_url = base_url
        self.output_file = output_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def generate_registration_numbers(self, start: int = 0, end: int = 999) -> List[str]:
        """Generate registration numbers from start to end"""
        base_number = "20227910-16-1-"
        return [f"{base_number}{str(i).zfill(5)}" for i in range(start, end + 1)]

    def fetch_registration_data(self, registration_number: str) -> Optional[Dict]:
        """Fetch data for a single registration number"""
        url = f"{self.base_url}/{registration_number}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if the response indicates data was found
            if data.get('code') == 200 and data.get('status') == 'Data ditemukan':
                return data.get('result')
            else:
                print(f"No data found for {registration_number}: {data.get('message', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {registration_number}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON for {registration_number}: {e}")
            return None

    def save_to_csv(self, data_list: List[Dict]):
        """Save the collected data to CSV file, sorted by distance_1 ascending"""
        if not data_list:
            print("No valid data to save.")
            return

        # Sort data by distance_1 in ascending order
        # Handle cases where distance_1 might be None or empty
        def get_distance_1(item):
            distance = item.get('distance_1')
            if distance is None or distance == '':
                return float('inf')  # Put None/empty values at the end
            try:
                return float(distance)
            except (ValueError, TypeError):
                return float('inf')  # Put invalid values at the end

        sorted_data = sorted(data_list, key=get_distance_1)

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

            for data in sorted_data:
                # Ensure all fields are present, use None/empty string for missing fields
                row = {header: data.get(header, '') for header in headers}
                writer.writerow(row)

        print(f"Saved {len(sorted_data)} records to {self.output_file} (sorted by distance_1 ascending)")

    def scrape_all_registrations(self, start: int = 0, end: int = 999, delay: float = 0):
        """Scrape all registration numbers from start to end"""
        registration_numbers = self.generate_registration_numbers(start, end)
        valid_data = []

        print(f"Starting to scrape {len(registration_numbers)} registration numbers...")
        print(f"Range: {registration_numbers[0]} to {registration_numbers[-1]}")

        for i, reg_number in enumerate(registration_numbers):
            print(f"Progress: {i+1}/{len(registration_numbers)} - Checking {reg_number}")

            data = self.fetch_registration_data(reg_number)
            if data:
                valid_data.append(data)
                print(f"✓ Found valid data for {reg_number} - {data.get('name', 'Unknown')}")

            # Rate limiting to be respectful to the server
            time.sleep(delay)

            # Save progress every 100 requests
            if (i + 1) % 100 == 0:
                print(f"Checkpoint: Saving {len(valid_data)} valid records so far...")
                self.save_to_csv(valid_data)

        # Final save
        self.save_to_csv(valid_data)
        print(f"Scraping completed! Found {len(valid_data)} valid registrations out of {len(registration_numbers)} checked.")

        return valid_data

    def find_registration_position(self, registration_number: str, quota: int = 139) -> Optional[Dict]:
        """Find the position of a specific registration number in the sorted results"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)

            # Find the registration number
            for i, record in enumerate(data):
                if record['registration_number'] == registration_number:
                    position = i + 1  # 1-based position

                    # Calculate acceptance probability
                    acceptance_probability = self.calculate_acceptance_probability(position, len(data), quota)

                    result = {
                        'position': position,
                        'total_records': len(data),
                        'percentile': round((position / len(data)) * 100, 1),
                        'quota': quota,
                        'acceptance_probability': acceptance_probability,
                        'student_data': record
                    }
                    return result

            return None  # Registration number not found

        except FileNotFoundError:
            print(f"Results file {self.output_file} not found. Please run the scraper first.")
            return None
        except Exception as e:
            print(f"Error reading results file: {e}")
            return None

    def calculate_acceptance_probability(self, position: int, total_records: int, quota: int) -> Dict:
        """Calculate acceptance probability based on position, total records, and quota"""

        # Basic probability if only considering current scraped data
        if position <= quota:
            basic_probability = 100.0  # Very high chance if within quota of scraped data
        else:
            basic_probability = 0.0  # Low chance if beyond quota

        # More realistic probability considering that there might be more registrations
        # that weren't found in our 00000-00999 range

        # Estimate total possible registrations (this is a rough estimate)
        # Based on the pattern, there might be more registrations outside our range
        estimated_total_registrations = total_records * 2  # Conservative estimate

        # Calculate realistic probability
        if position <= quota:
            # If within quota of found registrations, very high probability
            realistic_probability = min(95.0, 100.0 - (position / quota) * 20)
        elif position <= quota * 1.5:
            # If close to quota, moderate probability
            realistic_probability = max(10.0, 80.0 - ((position - quota) / quota) * 60)
        else:
            # If far from quota, low probability
            realistic_probability = max(1.0, 20.0 - ((position - quota) / quota) * 15)

        # Calculate position relative to quota
        quota_ratio = (position / quota) * 100

        return {
            'basic_probability': round(basic_probability, 1),
            'realistic_probability': round(realistic_probability, 1),
            'quota_ratio': round(quota_ratio, 1),
            'status': self.get_acceptance_status(position, quota),
            'explanation': self.get_probability_explanation(position, quota, total_records)
        }

    def get_acceptance_status(self, position: int, quota: int) -> str:
        """Get acceptance status based on position and quota"""
        if position <= quota * 0.5:
            return "SANGAT TINGGI"  # Very High
        elif position <= quota * 0.8:
            return "TINGGI"  # High
        elif position <= quota:
            return "SEDANG-TINGGI"  # Medium-High
        elif position <= quota * 1.2:
            return "SEDANG"  # Medium
        elif position <= quota * 1.5:
            return "RENDAH"  # Low
        else:
            return "SANGAT RENDAH"  # Very Low

    def get_probability_explanation(self, position: int, quota: int, total_found: int) -> str:
        """Get explanation for the probability calculation"""
        if position <= quota:
            return f"Posisi dalam kuota ({position}/{quota}). Kemungkinan diterima sangat tinggi."
        else:
            excess = position - quota
            return f"Posisi di luar kuota sebanyak {excess} siswa. Kemungkinan diterima tergantung pada siswa lain yang tidak terdaftar dalam data ini."

    def display_registration_position(self, registration_number: str, quota: int = 139):
        """Display the position and details of a specific registration number"""
        result = self.find_registration_position(registration_number, quota)

        if result is None:
            print(f"Registration number {registration_number} not found in the results.")
            return

        student = result['student_data']
        acceptance = result['acceptance_probability']

        print(f"\n{'='*70}")
        print(f"LAPORAN POSISI DAN KEMUNGKINAN DITERIMA")
        print(f"{'='*70}")
        print(f"Nomor Registrasi: {registration_number}")
        print(f"Posisi dalam urutan: #{result['position']} dari {result['total_records']} siswa")
        print(f"Persentil: {result['percentile']}% (top {result['percentile']}%)")

        print(f"\n{'='*70}")
        print(f"ANALISIS KEMUNGKINAN DITERIMA")
        print(f"{'='*70}")
        print(f"Kuota penerimaan: {quota} siswa")
        print(f"Rasio posisi terhadap kuota: {acceptance['quota_ratio']}%")
        print(f"Status kemungkinan: {acceptance['status']}")
        print(f"Kemungkinan diterima: {acceptance['realistic_probability']}%")
        print(f"Penjelasan: {acceptance['explanation']}")

        print(f"\n{'='*70}")
        print(f"DETAIL SISWA")
        print(f"{'='*70}")
        print(f"  Nama: {student.get('name', 'Unknown')}")
        print(f"  Sekolah asal: {student.get('school_name', 'Unknown')}")
        print(f"  Jarak ke pilihan 1: {student.get('distance_1', 'N/A')}m")
        print(f"  Jarak ke pilihan 2: {student.get('distance_2', 'N/A')}m")
        print(f"  Pilihan 1: {student.get('first_option_name', 'Unknown')}")
        print(f"  Pilihan 2: {student.get('second_option_name', 'Unknown')}")
        print(f"  Skor: {student.get('score', 'N/A')}")
        print(f"  Alamat: {student.get('address_subdistrict', '')}, {student.get('address_district', '')}, {student.get('address_city', '')}")

        # Add color-coded status indicator
        if acceptance['status'] in ['SANGAT TINGGI', 'TINGGI']:
            status_indicator = "🟢 KEMUNGKINAN BESAR DITERIMA"
        elif acceptance['status'] in ['SEDANG-TINGGI', 'SEDANG']:
            status_indicator = "🟡 KEMUNGKINAN SEDANG"
        else:
            status_indicator = "🔴 KEMUNGKINAN RENDAH"

        print(f"\n{'='*70}")
        print(f"KESIMPULAN: {status_indicator}")
        print(f"{'='*70}\n")

def main():
    # API base URL
    base_url = "https://spmb.jabarprov.go.id/api/public/registration"

    # Initialize scraper
    scraper = RegistrationScraper(base_url)

    # Ask user for confirmation before starting full scrape
    print("This script will scrape 1000 registration numbers (00000 to 00999).")
    print("This may take approximately 8-10 minutes with 0.5 second delays between requests.")

    # Test with a known working registration number first
    print("\nTesting with known registration number: 20227910-16-1-00369")
    test_data = scraper.fetch_registration_data("20227910-16-1-00369")
    if test_data:
        print(f"✓ Test successful! Found: {test_data.get('name', 'Unknown')}")
        print("API is working correctly.\n")
    else:
        print("✗ Test failed. Please check the API endpoint.")
        return

    # Start scraping from 00000 to 00999
    try:
        valid_data = scraper.scrape_all_registrations(start=0, end=999, delay=0.5)
        print(f"\nScraping Summary:")
        print(f"Total valid registrations found: {len(valid_data)}")
        print(f"Data saved to: {scraper.output_file}")

        # Demonstrate position lookup functionality
        print(f"\n" + "="*60)
        print("POSITION LOOKUP FUNCTIONALITY")
        print("="*60)

        # Example: Show position of the test registration number
        test_registration = "20227910-16-1-00369"
        print(f"Looking up position for test registration: {test_registration}")
        scraper.display_registration_position(test_registration)

        # Interactive lookup option
        while True:
            user_input = input("Enter a registration number to check its position (or 'quit' to exit): ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input:
                scraper.display_registration_position(user_input)
            else:
                print("Please enter a valid registration number or 'quit' to exit.")

    except KeyboardInterrupt:
        print("\nScraping interrupted by user. Partial data may have been saved.")
    except Exception as e:
        print(f"An error occurred: {e}")

def lookup_only():
    """Function to only lookup positions without running the scraper"""
    scraper = RegistrationScraper("https://spmb.jabarprov.go.id/api/public/registration")

    print("="*70)
    print("PENCARIAN POSISI DAN KEMUNGKINAN DITERIMA")
    print("="*70)
    print("Tool ini akan menampilkan posisi dan kemungkinan diterima untuk nomor registrasi.")
    print("Pastikan Anda sudah menjalankan scraper terlebih dahulu.\n")

    # Ask for quota (default 139)
    quota_input = input("Masukkan kuota penerimaan (default: 139): ").strip()
    try:
        quota = int(quota_input) if quota_input else 139
    except ValueError:
        quota = 139
        print("Input tidak valid, menggunakan kuota default: 139")

    print(f"Menggunakan kuota penerimaan: {quota} siswa\n")

    while True:
        user_input = input("Masukkan nomor registrasi (atau 'quit' untuk keluar): ").strip()
        if user_input.lower() in ['quit', 'exit', 'q', 'keluar']:
            break
        elif user_input:
            scraper.display_registration_position(user_input, quota)
        else:
            print("Silakan masukkan nomor registrasi yang valid atau 'quit' untuk keluar.")

if __name__ == "__main__":
    import sys

    # Check if user wants to run lookup only
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['lookup', 'position', 'find']:
        lookup_only()
    else:
        main()