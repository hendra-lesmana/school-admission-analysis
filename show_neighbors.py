import csv
import sys

def show_student_neighbors(target_registration: str, csv_file: str = "hasil_zonasi_only.csv", neighbors: int = 5):
    """Show students positioned around a target registration number"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
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
            print(f"❌ Registration {target_registration} not found in zonasi data")
            return
        
        # Calculate range
        start_idx = max(0, target_position - neighbors)
        end_idx = min(len(zonasi_data), target_position + neighbors + 1)
        
        print(f"\n{'='*130}")
        print(f"🎯 STUDENTS AROUND REGISTRATION: {target_registration}")
        print(f"{'='*130}")
        print(f"📍 Target Position: #{target_position + 1} out of {len(zonasi_data)} zonasi students")
        print(f"👤 Target Student: {target_record.get('name', 'Unknown')}")
        print(f"📏 Target Distance: {target_record.get('distance_1', 'N/A')}m")
        print(f"🏫 Target School: {target_record.get('school_name', 'Unknown')}")
        
        print(f"\n{'='*130}")
        print(f"📊 RANKING TABLE (Showing {neighbors} above and {neighbors} below)")
        print(f"{'='*130}")
        
        # Header
        print(f"{'Pos':<4} {'Registration':<20} {'Name':<25} {'Distance':<10} {'School':<30} {'First Choice':<25}")
        print(f"{'-'*130}")
        
        # Show students in range
        for i in range(start_idx, end_idx):
            record = zonasi_data[i]
            position = i + 1
            reg_num = record.get('registration_number', '')
            name = record.get('name', '')[:24]  # Truncate long names
            distance = record.get('distance_1', '')
            school = record.get('school_name', '')[:29]  # Truncate long school names
            first_choice = record.get('first_option_name', '')[:24]
            
            # Highlight the target registration
            if record['registration_number'] == target_registration:
                print(f"🎯 {position:<3} {reg_num:<20} {name:<25} {distance:<10} {school:<30} {first_choice:<25}")
            else:
                # Show position relative to target
                diff = position - (target_position + 1)
                if diff < 0:
                    indicator = f"↑{abs(diff)}"
                elif diff > 0:
                    indicator = f"↓{diff}"
                else:
                    indicator = "🎯"
                
                print(f"{indicator:<3} {position:<3} {reg_num:<20} {name:<25} {distance:<10} {school:<30} {first_choice:<25}")
        
        print(f"{'-'*130}")
        
        # Analysis
        print(f"\n📈 POSITION ANALYSIS:")
        quota = 139
        if target_position + 1 <= quota:
            status = "✅ DALAM KUOTA"
            remaining_slots = quota - (target_position + 1)
            print(f"   Status: {status}")
            print(f"   Margin: {remaining_slots} slots remaining before quota limit")
        else:
            status = "⚠️ DI LUAR KUOTA"
            excess = (target_position + 1) - quota
            print(f"   Status: {status}")
            print(f"   Gap: {excess} positions beyond quota limit")
        
        # Distance comparison
        if target_position > 0:
            prev_distance = float(zonasi_data[target_position - 1].get('distance_1', 0))
            curr_distance = float(target_record.get('distance_1', 0))
            distance_gap = curr_distance - prev_distance
            print(f"   Distance gap from student above: +{distance_gap:.3f}m")
        
        if target_position < len(zonasi_data) - 1:
            next_distance = float(zonasi_data[target_position + 1].get('distance_1', 0))
            curr_distance = float(target_record.get('distance_1', 0))
            distance_gap = next_distance - curr_distance
            print(f"   Distance gap to student below: +{distance_gap:.3f}m")
        
        print(f"\n{'='*130}")
        
    except FileNotFoundError:
        print(f"❌ File {csv_file} not found. Please run the scraper first.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("🔍 STUDENT NEIGHBOR VIEWER")
        print("Usage: python show_neighbors.py <registration_number> [neighbors_count]")
        print("Example: python show_neighbors.py 20227910-16-1-00369 5")
        print("\nOr run interactively:")
        
        while True:
            reg_num = input("\nEnter registration number (or 'quit' to exit): ").strip()
            if reg_num.lower() in ['quit', 'exit', 'q']:
                break
            
            neighbors_input = input("Number of neighbors to show (default 5): ").strip()
            try:
                neighbors = int(neighbors_input) if neighbors_input else 5
            except ValueError:
                neighbors = 5
            
            if reg_num:
                show_student_neighbors(reg_num, neighbors=neighbors)
    else:
        target_registration = sys.argv[1]
        neighbors = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        show_student_neighbors(target_registration, neighbors=neighbors)

if __name__ == "__main__":
    main()
