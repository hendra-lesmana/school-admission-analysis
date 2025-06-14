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
    
    def scrape_all_pages(self, progress_bar, status_text, limit_per_page: int = 100) -> List[Dict]:
        """Scrape all pages of data with progress tracking"""
        all_data = []
        page = 1
        
        while True:
            status_text.text(f"Fetching page {page}...")
            page_data = self.fetch_page(page, limit_per_page)
            
            if page_data is None:
                break
            
            result = page_data.get('result', {})
            data_items = result.get('itemsList', [])
            
            if data_items:
                all_data.extend(data_items)
                progress_bar.progress(min(len(all_data) / 200, 1.0))  # Estimate progress
                status_text.text(f"Page {page}: Found {len(data_items)} records (Total: {len(all_data)})")
                
                if len(data_items) < limit_per_page:
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

def main():
    st.title("🎓 School Admission Analysis System")
    st.markdown("**Analisis Penerimaan Siswa SMA Negeri Jawa Barat**")
    
    # Sidebar
    st.sidebar.title("📋 Menu")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Data Scraping", "🔍 Position Lookup", "📊 Data Analysis", "👥 Neighbor View"])
    
    with tab1:
        st.header("🔄 Data Scraping")
        st.markdown("Scrape latest data from the official API")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Start Scraping", type="primary"):
                scraper = StreamlitScraper("https://spmb.jabarprov.go.id/api/public/registration")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("Scraping data..."):
                    all_data = scraper.scrape_all_pages(progress_bar, status_text)
                
                if all_data:
                    # Convert to DataFrame
                    df = pd.DataFrame(all_data)
                    
                    # Filter zonasi data
                    zonasi_df = df[df['option_type'] == 'zonasi'].copy()
                    
                    # Save to CSV
                    df.to_csv('hasil_paginated_sorted.csv', index=False)
                    zonasi_df.to_csv('hasil_zonasi_only.csv', index=False)
                    
                    st.success(f"✅ Scraping completed!")
                    st.info(f"📊 Total records: {len(df)} | Zonasi: {len(zonasi_df)} | KETM: {len(df) - len(zonasi_df)}")
                    
                    # Show top 10
                    st.subheader("🏆 Top 10 Closest Distances (Zonasi)")
                    top_10 = zonasi_df.head(10)[['registration_number', 'name', 'distance_1', 'school_name']]
                    st.dataframe(top_10, use_container_width=True)
                else:
                    st.error("❌ No data was collected")
        
        with col2:
            st.info("**Data Source:**\nSPMB Jabar Official API\n\n**Parameters:**\n- NPSN: 20227910\n- Sorted by: distance_1\n- Order: ascending")
    
    with tab2:
        st.header("🔍 Position Lookup")
        st.markdown("Find position and acceptance probability for any registration number")
        
        # Load data
        zonasi_df = load_data_from_csv('hasil_zonasi_only.csv')
        
        if zonasi_df is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                reg_number = st.text_input("📝 Registration Number:", value="20227910-16-1-00369", placeholder="20227910-16-1-00369")
                quota = st.number_input("🎯 Quota:", min_value=1, max_value=500, value=139)
            
            with col2:
                st.info(f"**Available Data:**\n{len(zonasi_df)} zonasi students")
            
            if reg_number and st.button("🔍 Search Position"):
                # Find student
                student_row = zonasi_df[zonasi_df['registration_number'] == reg_number]
                
                if not student_row.empty:
                    position = student_row.index[0] + 1
                    student = student_row.iloc[0]
                    
                    # Calculate probability
                    prob_data = calculate_acceptance_probability(position, len(zonasi_df), quota)
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Position", f"#{position}", f"out of {len(zonasi_df)}")
                    
                    with col2:
                        st.metric("Acceptance Probability", f"{prob_data['probability']}%", prob_data['status'])
                    
                    with col3:
                        quota_status = "✅ In Quota" if prob_data['in_quota'] else "⚠️ Beyond Quota"
                        remaining = quota - position if prob_data['in_quota'] else position - quota
                        st.metric("Quota Status", quota_status, f"{remaining} slots")
                    
                    # Student details
                    st.subheader("👤 Student Details")
                    details_col1, details_col2 = st.columns(2)
                    
                    with details_col1:
                        st.write(f"**Name:** {student.get('name', 'Unknown')}")
                        st.write(f"**School:** {student.get('school_name', 'Unknown')}")
                        st.write(f"**Distance 1:** {student.get('distance_1', 'N/A')}m")
                        st.write(f"**Distance 2:** {student.get('distance_2', 'N/A')}m")
                    
                    with details_col2:
                        st.write(f"**First Choice:** {student.get('first_option_name', 'Unknown')}")
                        st.write(f"**Second Choice:** {student.get('second_option_name', 'Unknown')}")
                        st.write(f"**Score:** {student.get('score', 'N/A')}")
                        st.write(f"**Address:** {student.get('address_subdistrict', '')}, {student.get('address_district', '')}")
                else:
                    st.error(f"❌ Registration number {reg_number} not found in zonasi data")
        else:
            st.warning("⚠️ No data available. Please run the scraper first.")
    
    with tab3:
        st.header("📊 Data Analysis")
        
        zonasi_df = load_data_from_csv('hasil_zonasi_only.csv')
        
        if zonasi_df is not None:
            # Convert distance to numeric
            zonasi_df['distance_1_num'] = pd.to_numeric(zonasi_df['distance_1'], errors='coerce')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Distance distribution
                fig_hist = px.histogram(
                    zonasi_df, 
                    x='distance_1_num', 
                    nbins=30,
                    title="Distance Distribution (Zonasi Students)",
                    labels={'distance_1_num': 'Distance (meters)', 'count': 'Number of Students'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # School distribution
                school_counts = zonasi_df['school_name'].value_counts().head(10)
                fig_bar = px.bar(
                    x=school_counts.values,
                    y=school_counts.index,
                    orientation='h',
                    title="Top 10 Schools by Student Count",
                    labels={'x': 'Number of Students', 'y': 'School Name'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Quota analysis
            st.subheader("🎯 Quota Analysis")
            quota = 139
            in_quota = len(zonasi_df[zonasi_df.index < quota])
            beyond_quota = len(zonasi_df) - in_quota
            
            quota_col1, quota_col2, quota_col3 = st.columns(3)
            
            with quota_col1:
                st.metric("Students in Quota", in_quota, f"out of {quota}")
            
            with quota_col2:
                st.metric("Students beyond Quota", beyond_quota)
            
            with quota_col3:
                acceptance_rate = (in_quota / len(zonasi_df)) * 100
                st.metric("Acceptance Rate", f"{acceptance_rate:.1f}%")
        else:
            st.warning("⚠️ No data available. Please run the scraper first.")
    
    with tab4:
        st.header("👥 Neighbor View")
        st.markdown("View students positioned around any registration number")
        
        zonasi_df = load_data_from_csv('hasil_zonasi_only.csv')
        
        if zonasi_df is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                reg_number = st.text_input("📝 Registration Number:", value="20227910-16-1-00369", placeholder="20227910-16-1-00369", key="neighbor_reg")
                neighbors = st.slider("👥 Number of neighbors to show:", min_value=3, max_value=15, value=5)
            
            if reg_number and st.button("👥 Show Neighbors"):
                student_row = zonasi_df[zonasi_df['registration_number'] == reg_number]
                
                if not student_row.empty:
                    target_position = student_row.index[0]
                    
                    # Calculate range
                    start_idx = max(0, target_position - neighbors)
                    end_idx = min(len(zonasi_df), target_position + neighbors + 1)
                    
                    # Get neighbors
                    neighbors_df = zonasi_df.iloc[start_idx:end_idx].copy()
                    neighbors_df['position'] = neighbors_df.index + 1
                    neighbors_df['is_target'] = neighbors_df['registration_number'] == reg_number
                    
                    # Display table
                    st.subheader(f"👥 Students around position #{target_position + 1}")
                    
                    # Format the display
                    display_df = neighbors_df[['position', 'registration_number', 'name', 'distance_1', 'school_name']].copy()
                    
                    # Style the target row
                    def highlight_target(row):
                        if neighbors_df.loc[row.name, 'is_target']:
                            return ['background-color: yellow'] * len(row)
                        return [''] * len(row)
                    
                    styled_df = display_df.style.apply(highlight_target, axis=1)
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Analysis
                    target_student = student_row.iloc[0]
                    quota = 139
                    position = target_position + 1
                    
                    if position <= quota:
                        status = f"✅ In Quota ({quota - position} slots remaining)"
                    else:
                        status = f"⚠️ Beyond Quota (+{position - quota} positions)"
                    
                    st.info(f"**Position Analysis:** {status}")
                else:
                    st.error(f"❌ Registration number {reg_number} not found")
        else:
            st.warning("⚠️ No data available. Please run the scraper first.")

if __name__ == "__main__":
    main()
