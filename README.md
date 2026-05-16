# EDA Agent 📊

An AI-powered **Exploratory Data Analysis (EDA) platform** that automatically analyzes CSV files and generates professional reports with statistics, visualizations, and AI-generated insights.

## What is EDA Agent?

EDA Agent is a web-based application that simplifies data analysis. Simply upload a CSV file, and the AI agent will:
- ✅ Analyze dataset structure and quality
- ✅ Calculate statistical measures (mean, median, std, min, max)
- ✅ Detect outliers using the IQR method
- ✅ Generate distribution charts
- ✅ Create correlation matrices
- ✅ Provide AI-powered insights and recommendations
- ✅ Export professional PDF reports

## How It Works

### 1. **Upload CSV File**
Navigate to the web interface and upload your CSV file. The AI agent will process it automatically.

![Upload Interface](screenshots/img1.png)

### 2. **Automatic Analysis**
The system runs comprehensive analysis:
- **Dataset Overview** - Rows, columns, data types, null values
- **Basic Statistics** - Mean, median, standard deviation, min/max for numeric columns
- **Outlier Detection** - Identifies anomalies using statistical methods
- **Visualizations** - Generates distribution plots and correlation matrices

![Dataset Overview](screenshots/img2.png)

### 3. **AI-Generated Summary**
Groq AI processes the analysis and provides professional insights with:
- Key findings from the data
- Statistical interpretations
- Actionable recommendations
- Data quality assessment

### 4. **Download Report**
Export a professional PDF report containing:
- Dataset overview table
- Statistical summary table
- Outlier detection results
- AI agent analysis and recommendations
- Visual charts

![Analysis Results](screenshots/img3.png)
![PDF Report Preview](screenshots/img4.png)

## Features

### 🎯 Core Capabilities
- **Automatic EDA** - One-click analysis without manual setup
- **AI Insights** - Groq LLM integration for intelligent analysis
- **Professional Reports** - PDF export with tables and charts
- **Web Interface** - Clean, intuitive dark-themed UI
- **Real-time Visualization** - Interactive charts and statistics

### 📊 Analysis Tools
- Dataset dimensionality assessment
- Data type detection
- Missing value analysis
- Statistical computations
- Outlier detection (IQR method)
- Distribution plotting
- Correlation analysis

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd EDA_Agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

5. **Run the application**
```bash
uvicorn main:app --reload
```

Access the application at `http://127.0.0.1:8000`

## Project Structure

```
EDA_Agent/
├── agent.py              # AI agent logic
├── main.py               # FastAPI application
├── tools.py              # Analysis tools
├── report.py             # PDF report generation
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (git ignored)
├── .gitignore            # Git ignore rules
├── static/
│   └── index.html        # Web UI
├── outputs/              # Generated reports and charts
├── uploads/              # Temporary file storage
└── screenshots/          # Documentation images
```

## Usage

### Web Interface

1. **Open the application** - Navigate to http://127.0.0.1:8000
2. **Upload CSV** - Click the upload area or drag-and-drop a CSV file
3. **Click "Analyze with AI Agent"** - Wait for analysis to complete
4. **View Results** - See structured analysis with tables and charts
5. **Download Report** - Click the "📥 Download PDF Report" button

### API Endpoint

**POST** `/analyze`

Request:
```bash
curl -X POST -F "file=@data.csv" http://127.0.0.1:8000/analyze
```

Response:
```json
{
  "summary": "AI-generated analysis...",
  "charts": ["/outputs/distributions.png", "/outputs/correlation_matrix.png"],
  "rows": 100,
  "columns": 5,
  "report_url": "/outputs/report.pdf",
  "overview": {...},
  "statistics": {...},
  "outliers": {...}
}
```

## Technologies Used

- **Backend**: FastAPI, Python
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **PDF Generation**: fpdf2
- **AI**: Groq API (Llama 3.3)
- **Frontend**: HTML, CSS, JavaScript
- **Server**: Uvicorn

## Data Limits

- **Sampling**: Datasets larger than 500 rows are sampled for agent analysis
- **Full Data**: PDF reports use complete dataset
- **File Format**: CSV only
- **Max File Size**: Limited by server configuration

## API Requirements

This application uses the **Groq API** for AI-powered insights:
- Get your API key at: https://console.groq.com
- Model used: llama-3.3-70b-versatile
- Requests are processed asynchronously

## Troubleshooting

### Issue: "Failed to call a function" error
- **Solution**: Ensure Groq API key is valid in `.env`

### Issue: Font errors in PDF generation
- **Solution**: The app uses built-in Helvetica font - no additional installation needed

### Issue: Charts not generating
- **Solution**: Ensure the `outputs/` directory exists and is writable

### Issue: Port 8000 already in use
- **Solution**: `uvicorn main:app --reload --port 8001`

## Configuration

### Modify Analysis Parameters

Edit `agent.py` to adjust:
- Maximum iterations for analysis
- Groq model selection
- Analysis tools subset

Edit `tools.py` to adjust:
- Statistical calculations
- Outlier detection sensitivity (IQR multiplier)
- Chart styling

## Performance

- **Upload Processing**: < 1 second
- **Analysis (500 rows)**: 10-30 seconds
- **PDF Generation**: 5-10 seconds
- **Total Time**: ~20-50 seconds

## Future Enhancements

- [ ] Support for Excel (.xlsx) files
- [ ] Interactive data exploration dashboard
- [ ] Custom analysis templates
- [ ] Data validation and cleaning suggestions
- [ ] Automated anomaly detection alerts
- [ ] Real-time collaboration features
- [ ] Advanced statistical tests

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review the code comments
3. Check API documentation at https://console.groq.com

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

**Made with ❤️ for data analysts and data scientists**
