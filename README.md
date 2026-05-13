# EDA Agent 📊

An AI-powered Exploratory Data Analysis application built with Streamlit and Groq API.

## Features

- 📂 **Upload** any CSV file
- 📊 **Auto-generated** visualizations (histograms, bar charts, correlation heatmaps)
- 🤖 **AI Agent** powered by Groq LLM for intelligent data analysis
- 🔍 **Outlier detection** using IQR and Z-score methods
- 📄 **PDF report** generation with complete analysis

## Installation

### Local Development

1. Clone the repository
```bash
git clone <your-repo-url>
cd EDA_Agent
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up API key
Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

5. Run the app
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. **Push to GitHub**
   - Ensure `.env` is in `.gitignore` ✓ (already configured)
   - Ensure `requirements.txt` is committed ✓

2. **Deploy on Streamlit Cloud**
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - Select the app.py file
   - In **Advanced settings**, add secret:
     - Key: `GROQ_API_KEY`
     - Value: Your Groq API key

3. **Verify deployment**
   - Test file upload functionality
   - Test AI agent analysis
   - Test PDF report generation

## Tech Stack

- **Streamlit** - Web UI framework
- **Pandas** - Data processing
- **Matplotlib** - Data visualization
- **Groq API** - LLM for agentic AI
- **fpdf2** - PDF generation

## Project Structure

```
├── app.py              # Main Streamlit application
├── report.py           # PDF report generation
├── tools.py            # Data analysis utilities
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Streamlit configuration
├── .env                # Local environment variables (not committed)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Security Notes

- ✅ `.env` file is in `.gitignore` - API key won't be committed
- ✅ Streamlit Cloud secrets are stored securely in the dashboard
- Never commit sensitive data like API keys

## Troubleshooting

### API Key Error
If you see "Invalid API key" error:
1. Verify your Groq API key is correct
2. Check `.env` file (local) or Streamlit secrets (cloud)

### No Charts Generated
Make sure your CSV has at least one numeric column for analysis.

### PDF Generation Fails
Ensure matplotlib backend is properly configured (uses "Agg" in report.py).

## License

MIT License - Feel free to use for your projects!

---

Built with ❤️ using Streamlit
