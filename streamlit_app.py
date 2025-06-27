import streamlit as st
import pandas as pd
import requests
import csv
import json
import time
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="School Admission Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
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
            response = self.session.get(school_url, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 200:
                return data
            else:
                st.error(f"School API returned error code: {data.get('code')} - {data.get('message', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching school options: {e}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"Error parsing school options JSON: {e}")
            return None
    
    def fetch_page(self, page: int = 1, limit: int = 100, npsn: str = '20227910',
                   option_type: str = 'zonasi', orderby: str = 'distance_1',
                   order: str = 'asc', major_id: str = None) -> Optional[Dict]:
        """Fetch a single page of data from the API with flexible parameters"""
        params = {
            'page': page,
            'limit': limit,
            'orderby': orderby,
            'order': order,
            'pagination': 'true',
            'columns[0][key]': 'name',
            'columns[0][searchable]': 'false',
            'columns[1][key]': 'registration_number',
            'columns[1][searchable]': 'true',
            'npsn': npsn,
            'filters[1][key]': 'option_type',
            'filters[1][value]': option_type
        }

        # Add major_id if provided (for prestasi-rapor)
        if major_id and option_type == 'prestasi-rapor':
            params['major_id'] = major_id

        try:
            response = self.session.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 200:
                return data
            else:
                st.error(f"API returned error code: {data.get('code')} - {data.get('message', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching page {page}: {e}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON for page {page}: {e}")
            return None
    
    def scrape_all_pages(self, progress_bar, status_text, limit_per_page: int = 100,
                        npsn: str = '20227910', option_type: str = 'zonasi',
                        orderby: str = 'distance_1', order: str = 'asc',
                        major_id: str = None) -> List[Dict]:
        """Scrape all pages of data with progress tracking and flexible parameters"""
        all_data = []
        page = 1

        while True:
            status_text.text(f"Fetching page {page}...")
            page_data = self.fetch_page(page, limit_per_page, npsn, option_type, orderby, order, major_id)

            if page_data is None:
                break

            result = page_data.get('result', {})
            data_items = result.get('itemsList', [])

            if data_items:
                all_data.extend(data_items)

                # Get pagination info for better progress tracking
                pagination = result.get('pagination', {})
                total_records = pagination.get('total_records', len(all_data))

                if total_records > 0:
                    progress_bar.progress(min(len(all_data) / total_records, 1.0))
                else:
                    progress_bar.progress(min(len(all_data) / 200, 1.0))  # Fallback estimate

                status_text.text(f"Page {page}: Found {len(data_items)} records (Total: {len(all_data)})")

                # Check if we've reached the last page using pagination info
                current_page = pagination.get('current_page', page)
                total_pages = pagination.get('total_pages', 0)

                if current_page >= total_pages and total_pages > 0:
                    break
                elif len(data_items) < limit_per_page:
                    break
            else:
                break

            page += 1
            time.sleep(0.5)  # Rate limiting

        return all_data

def load_data_from_csv(file_path: str) -> Optional[pd.DataFrame]:
    """Load data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def calculate_acceptance_probability(position: int, total_zonasi: int, quota: int = 139) -> Dict:
    """Calculate acceptance probability"""
    if position <= quota:
        if position <= quota * 0.3:
            probability = 95.0
            status = "SANGAT TINGGI"
            color = "green"
        elif position <= quota * 0.6:
            probability = 85.0
            status = "TINGGI"
            color = "green"
        else:
            probability = 75.0
            status = "SEDANG-TINGGI"
            color = "orange"
    elif position <= quota * 1.2:
        probability = 40.0
        status = "RENDAH"
        color = "red"
    else:
        probability = 10.0
        status = "SANGAT RENDAH"
        color = "red"
    
    return {
        'probability': probability,
        'status': status,
        'color': color,
        'in_quota': position <= quota
    }

def analyze_prestasi_by_jurusan(df: pd.DataFrame) -> Dict:
    """Analyze prestasi-rapor data and create top 50 per jurusan"""
    if df is None or len(df) == 0:
        return {}

    # Clean data
    df_clean = df.dropna(subset=['first_option_name', 'score']).copy()
    df_clean['score'] = pd.to_numeric(df_clean['score'], errors='coerce')
    df_clean = df_clean.dropna(subset=['score'])

    # Get unique jurusan
    jurusan_list = df_clean['first_option_name'].unique()

    results = {}

    for jurusan in jurusan_list:
        # Filter data untuk jurusan ini
        jurusan_df = df_clean[df_clean['first_option_name'] == jurusan].copy()

        # Sort berdasarkan score (descending)
        jurusan_df = jurusan_df.sort_values('score', ascending=False)

        # Ambil top 50 (atau semua jika kurang dari 50)
        top_50 = jurusan_df.head(50).copy()

        # Tambahkan ranking
        top_50['Ranking'] = range(1, len(top_50) + 1)

        # Clean jurusan name
        clean_name = jurusan.replace('SMKN 4 PADALARANG - ', '').replace('SMAN 2 PADALARANG - ', '')
        clean_name = clean_name.replace(' - PRESTASI NILAI RAPOR', '')

        results[clean_name] = {
            'data': top_50,
            'total_siswa': len(jurusan_df),
            'score_tertinggi': jurusan_df['score'].max(),
            'score_terendah': jurusan_df['score'].min(),
            'rata_rata_score': jurusan_df['score'].mean(),
            'median_score': jurusan_df['score'].median()
        }

    return results

def main():
    st.title("🎓 School Admission Analysis System")
    st.markdown("**Analisis Penerimaan Siswa SMA Negeri Jawa Barat**")

    # Sidebar
    st.sidebar.title("📋 Menu")

    # Sidebar configuration
    st.sidebar.subheader("🏫 School Configuration")
    npsn = st.sidebar.text_input("NPSN:", value="20206224", help="School NPSN code")

    # Main tabs
    tab1, tab2 = st.tabs(["🎯 Prestasi Scraping", "🏆 Top 50 per Jurusan"])
    
    with tab1:
        st.header("🎯 Prestasi-Rapor Data Scraping")
        st.markdown("Scrape prestasi-rapor data with major selection")

        # First, get school options
        scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")

        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("🔍 Load School Options", key="load_options"):
                with st.spinner("Loading school options..."):
                    school_data = scraper.fetch_school_options(npsn)

                    if school_data and school_data.get('result'):
                        school_info = school_data['result']
                        st.session_state['school_data'] = school_info

                        st.success(f"✅ Loaded options for: {school_info.get('name', 'Unknown School')}")

                        # Display school statistics
                        stats = school_info.get('statistics', [])
                        if stats and isinstance(stats, list):
                            st.subheader("📊 School Statistics")

                            # Calculate totals from all options
                            total_registrations = sum(stat.get('total_registration', 0) for stat in stats)
                            total_verified = sum(stat.get('total_verified', 0) for stat in stats)
                            total_not_verified = sum(stat.get('total_not_verified', 0) for stat in stats)
                            total_canceled = sum(stat.get('total_canceled', 0) for stat in stats)

                            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)

                            with col_stats1:
                                st.metric("Total Registrations", total_registrations)
                            with col_stats2:
                                st.metric("Verified", total_verified)
                            with col_stats3:
                                st.metric("Not Verified", total_not_verified)
                            with col_stats4:
                                st.metric("Canceled", total_canceled)
                    else:
                        st.error("❌ Failed to load school options")

            # Show school information if loaded
            if 'school_data' in st.session_state:
                school_info = st.session_state['school_data']

                # Show available prestasi options for information
                stats = school_info.get('statistics', [])
                prestasi_options = []
                if isinstance(stats, list):
                    prestasi_options = [stat for stat in stats if 'PRESTASI NILAI RAPOR' in stat.get('option', '')]

                if prestasi_options:
                    st.subheader("🎓 Available Prestasi-Rapor Programs")
                    st.info(f"This school offers {len(prestasi_options)} prestasi-rapor programs. The scraper below will collect data from ALL programs.")

                    # Show available prestasi options
                    for i, option in enumerate(prestasi_options, 1):
                        option_name = option.get('option', 'Unknown')
                        registrations = option.get('total_registration', 0)
                        st.write(f"{i}. {option_name} ({registrations} registrations)")
                else:
                    st.warning("⚠️ No prestasi-rapor programs found for this school")

                # Add scraping option
                st.subheader("🎯 Scraping")

                if st.button("🚀 Scrape ALL Prestasi-Rapor Data", type="primary", key="scrape_all_prestasi"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    st.info(f"🔍 Scraping ALL prestasi-rapor data (no major filter)")
                    st.write(f"- NPSN: {npsn}")
                    st.write(f"- Option Type: prestasi-rapor")
                    st.write(f"- Order By: score (descending)")
                    st.write(f"- Major ID: None (all majors)")

                    try:
                        with st.spinner("Scraping ALL prestasi-rapor data..."):
                            all_prestasi_data = scraper.scrape_all_pages(
                                progress_bar, status_text,
                                npsn=npsn, option_type='prestasi-rapor',
                                orderby='score', order='desc'
                                # No major_id parameter = get all majors
                            )

                        st.write(f"🔍 Raw data result: {type(all_prestasi_data)} with {len(all_prestasi_data) if all_prestasi_data else 0} items")

                        if all_prestasi_data:
                            # Convert to DataFrame
                            df_all_prestasi = pd.DataFrame(all_prestasi_data)

                            # Save to CSV
                            df_all_prestasi.to_csv('hasil_all_prestasi_rapor.csv', index=False)

                            st.success(f"✅ ALL Prestasi-rapor scraping completed!")
                            st.info(f"📊 Total prestasi-rapor records: {len(df_all_prestasi)}")

                            # Show statistics by major/option
                            if 'first_option_name' in df_all_prestasi.columns:
                                st.subheader("📊 Records by Major")
                                major_counts = df_all_prestasi['first_option_name'].value_counts()
                                st.bar_chart(major_counts)
                                st.write("**Major Distribution:**")
                                for major, count in major_counts.head(10).items():
                                    st.write(f"- {major}: {count} students")

                            # Show all records in a table
                            st.subheader(f"📋 All {len(df_all_prestasi)} Prestasi-Rapor Records")
                            if len(df_all_prestasi) > 0:
                                # Add ranking column
                                df_display = df_all_prestasi.copy()
                                df_display.insert(0, 'Rank', range(1, len(df_display) + 1))

                                display_cols = ['Rank', 'registration_number', 'name', 'score', 'first_option_name', 'school_name', 'created_at']
                                available_cols = [col for col in display_cols if col in df_display.columns]

                                # Show all records with pagination-like display
                                st.dataframe(
                                    df_display[available_cols],
                                    use_container_width=True,
                                    height=600  # Set height to show more records
                                )

                                # Add download button for CSV
                                csv_data = df_all_prestasi.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download All Records as CSV",
                                    data=csv_data,
                                    file_name=f"all_prestasi_rapor_{npsn}.csv",
                                    mime="text/csv"
                                )
                        else:
                            st.error("❌ No prestasi-rapor data was collected")
                            st.write("🔍 This might indicate no prestasi-rapor registrations exist for this school")

                    except Exception as e:
                        st.error(f"❌ Error during ALL prestasi-rapor scraping: {e}")
                        st.exception(e)



        with col2:
            st.info(f"**Data Source:**\nSPMB Jabar Official API\n\n**Parameters:**\n- NPSN: {npsn}\n- Type: Prestasi-Rapor (ALL majors)\n- Sorted by: score\n- Order: descending\n- Major Filter: None (scrapes all)")

            if 'school_data' in st.session_state:
                school_info = st.session_state['school_data']
                st.info(f"**School:** {school_info.get('name', 'Unknown')}\n**Address:** {school_info.get('address', 'N/A')}")

    with tab2:
        st.header("🏆 Top 50 per Jurusan")
        st.markdown("Analisis ranking top 50 siswa untuk setiap jurusan")

        # Load prestasi-rapor data
        prestasi_df = load_data_from_csv('hasil_all_prestasi_rapor.csv')

        if prestasi_df is not None:
            # Analyze data by jurusan
            jurusan_analysis = analyze_prestasi_by_jurusan(prestasi_df)

            if jurusan_analysis:
                st.success(f"✅ Data berhasil dianalisis untuk {len(jurusan_analysis)} jurusan")

                # Summary statistics
                st.subheader("📊 Ringkasan Semua Jurusan")

                col_summary1, col_summary2, col_summary3 = st.columns(3)

                total_siswa = sum([data['total_siswa'] for data in jurusan_analysis.values()])
                highest_score = max([data['score_tertinggi'] for data in jurusan_analysis.values()])
                lowest_score = min([data['score_terendah'] for data in jurusan_analysis.values()])

                with col_summary1:
                    st.metric("Total Jurusan", len(jurusan_analysis))

                with col_summary2:
                    st.metric("Total Siswa", total_siswa)

                with col_summary3:
                    st.metric("Score Range", f"{lowest_score:.1f} - {highest_score:.1f}")

                # Jurusan selection
                st.subheader("🎓 Pilih Jurusan untuk Melihat Top 50")

                jurusan_names = list(jurusan_analysis.keys())
                selected_jurusan = st.selectbox(
                    "Pilih Jurusan:",
                    options=jurusan_names,
                    key="jurusan_select"
                )

                if selected_jurusan:
                    jurusan_data = jurusan_analysis[selected_jurusan]

                    # Display jurusan statistics
                    st.subheader(f"📈 Statistik Jurusan: {selected_jurusan}")

                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

                    with col_stat1:
                        st.metric("Total Siswa", jurusan_data['total_siswa'])

                    with col_stat2:
                        st.metric("Score Tertinggi", f"{jurusan_data['score_tertinggi']:.1f}")

                    with col_stat3:
                        st.metric("Score Terendah", f"{jurusan_data['score_terendah']:.1f}")

                    with col_stat4:
                        st.metric("Rata-rata", f"{jurusan_data['rata_rata_score']:.1f}")

                    # Display top 50 table
                    top_50_data = jurusan_data['data']

                    st.subheader(f"🏆 Top {len(top_50_data)} Siswa - {selected_jurusan}")

                    # Prepare display columns
                    display_cols = ['Ranking', 'registration_number', 'name', 'score']
                    if 'school_name' in top_50_data.columns:
                        display_cols.append('school_name')
                    if 'created_at' in top_50_data.columns:
                        display_cols.append('created_at')

                    # Filter available columns
                    available_cols = [col for col in display_cols if col in top_50_data.columns]

                    # Display table
                    st.dataframe(
                        top_50_data[available_cols],
                        use_container_width=True,
                        height=600
                    )

                    # Download button
                    csv_data = top_50_data.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download Top {len(top_50_data)} {selected_jurusan} as CSV",
                        data=csv_data,
                        file_name=f"top50_{selected_jurusan.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )

                # Show all jurusan comparison
                st.subheader("📊 Perbandingan Semua Jurusan")

                # Create comparison dataframe
                comparison_data = []
                for jurusan, data in jurusan_analysis.items():
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

                st.dataframe(comparison_df, use_container_width=True)

                # Download all comparison
                csv_comparison = comparison_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Perbandingan Jurusan as CSV",
                    data=csv_comparison,
                    file_name="perbandingan_jurusan.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Tidak ada data jurusan yang ditemukan")
        else:
            st.warning("⚠️ File hasil_all_prestasi_rapor.csv tidak ditemukan. Silakan lakukan scraping prestasi-rapor terlebih dahulu.")





if __name__ == "__main__":
    main()
