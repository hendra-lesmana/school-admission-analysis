# 🎓 School Admission Analysis System

A comprehensive web scraping and analysis system for school admission data from SPMB Jawa Barat (West Java School Admission System).

## 📋 Features

- **🔄 Data Scraping**: Automated scraping from official SPMB Jabar API
- **📊 Position Analysis**: Calculate admission probability based on distance ranking
- **👥 Neighbor Comparison**: View students positioned around any registration
- **🌐 Web Dashboard**: Interactive Streamlit application
- **📈 Data Visualization**: Charts and graphs for admission analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/school-admission-analysis.git
   cd school-admission-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the scraper**
   ```bash
   python scrape_paginated.py
   ```

4. **Launch web dashboard**
   ```bash
   streamlit run streamlit_app.py
   ```

## 📁 Project Structure

```
school-admission-analysis/
├── scrape_paginated.py      # Main scraping script with pagination
├── run.py                   # Original scraping script
├── lookup_position.py       # Position lookup and probability calculator
├── show_neighbors.py        # Neighbor analysis tool
├── streamlit_app.py         # Web dashboard application
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Usage

### Command Line Tools

**1. Scrape Latest Data**
```bash
python scrape_paginated.py
```

**2. Lookup Student Position**
```bash
python lookup_position.py 20227910-16-1-00369
```

**3. View Neighbors**
```bash
python show_neighbors.py 20227910-16-1-00369 5
```

### Web Dashboard

Launch the Streamlit application for an interactive experience:
```bash
streamlit run streamlit_app.py
```

Features include:
- 🔄 **Data Scraping Tab**: Scrape latest admission data
- 🔍 **Position Lookup Tab**: Find student position and acceptance probability
- 📊 **Data Analysis Tab**: Visualize distance distributions and school statistics
- 👥 **Neighbor View Tab**: Compare students around any position

## 📊 Data Analysis

The system analyzes:
- **Distance-based ranking** (Zonasi) for fair comparison
- **Acceptance probability** based on 139 student quota
- **Position relative to quota** with remaining slots
- **Competitive landscape** around any student position

### Sample Results
- **Position**: #46 out of 112 zonasi students
- **Acceptance Probability**: 85.0% (TINGGI)
- **Status**: ✅ DALAM KUOTA (93 slots remaining)

## 🎯 Key Features

### Intelligent Scraping
- Paginated API requests with rate limiting
- Automatic zonasi/KETM filtering
- Progress tracking and error handling
- Data sorted by distance (closest first)

### Position Analysis
- Accurate probability calculation
- Quota-based status determination
- Color-coded risk assessment
- Detailed student information

### Neighbor Comparison
- View students 5 positions above/below
- Distance gap analysis
- Competitive landscape visualization
- Position relative to quota

## 📈 Data Sources

- **API**: SPMB Jawa Barat Official Registration API
- **School**: SMP/SMA Negeri Padalarang (NPSN: 20227910)
- **Type**: Zonasi (distance-based) admissions
- **Sorting**: By distance_1 (ascending)

## 🛠️ Technical Details

### Dependencies
- `streamlit` - Web dashboard framework
- `pandas` - Data manipulation and analysis
- `requests` - HTTP requests for API scraping
- `plotly` - Interactive data visualization

### API Endpoint
```
https://spmb.jabarprov.go.id/api/public/registration
```

### Data Fields
- Registration number, student name, school
- Distance to 1st, 2nd, 3rd choice schools
- Scores and address information
- Option type (zonasi/KETM)

## 📝 License

This project is for educational and analysis purposes. Please respect the terms of service of the data source.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For questions or issues, please open an issue on GitHub.

---

**Note**: This tool is designed for analysis purposes. Always verify results with official sources for important decisions.
