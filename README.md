# CheckWealth 💰

An AI-powered web-based financial statement analyzer that converts raw bank statements (CSV/Excel) into actionable insights with automatic transaction categorization using Large Language Models (LLM).

## Features

✨ **Smart Transaction Analysis**
- Upload bank statements in CSV or Excel format (XLSX, XLS)
- Automatic detection of credit/debit transactions
- AI-powered transaction categorization using OpenAI GPT

📊 **Comprehensive Categories**
- Eatouts
- Grocery
- Transportation
- Drinks/Coffee
- Entertainment
- Healthcare
- Shopping
- Education
- Telecom
- Donations
- Miscellaneous
- Custom category suggestions via LLM

📈 **Monthly Analysis**
- Total income and expenses tracking
- Net savings calculation
- Transaction count and breakdown
- Category-wise spending analysis with percentages

🎯 **Monthly Highlights**
- Highest spending category
- Largest single transaction
- Average daily spending
- Savings rate percentage

📄 **Detailed Reports**
- Downloadable text-based analysis reports
- Complete transaction history by category
- Month-by-month breakdown

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for LLM-based categorization)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/poojanagvekar/checkwealth.git
   cd checkwealth
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OpenAI API Key**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```
   
   Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Uploading Bank Statements

1. Click the upload area or drag-and-drop your CSV/Excel file
2. Supported formats: `.csv`, `.xlsx`, `.xls`
3. Maximum file size: 16MB

### Expected File Format

Your bank statement should contain at least these columns (column names are flexible):
- **Date**: Transaction date (various formats supported)
- **Description**: Transaction description/narration
- **Amount**: Transaction amount (or separate Debit/Credit columns)

The application supports multiple bank statement formats with automatic column detection:

**Format 1 - Simple format:**
```csv
Date,Description,Amount,Type
2024-01-05,SALARY CREDIT,5000.00,credit
2024-01-06,STARBUCKS,-5.50,debit
```

**Format 2 - With sub-descriptions:**
```csv
Filter,Date,Description,Sub-description,Status,Type of Transaction,Amount
July 2025,2025-07-31,mcdonald's,North York On (Apple Pay),posted,Debit,16.02
```

**Format 3 - With transaction types:**
```csv
First Bank Card,Transaction Type,Date Posted,Transaction Amount,Description
5510290061711841,CREDIT,20250801,719.58,[DN] B/M PAY-PAIE PAY/PAY
5510290061711841,DEBIT,20250730,125.43,WALMART GROCERY STORE
```

**Supported Date Formats:**
- `YYYY-MM-DD` (2025-07-31)
- `YYYYMMDD` (20250801)
- `MM/DD/YYYY` (07/31/2025)
- `DD/MM/YYYY` (31/07/2025)
- And other common formats

Sample statement files are included:
- `sample_statement.csv` - Basic format
- `sample_statement_format1.csv` - Format with sub-descriptions
- `sample_statement_format2.csv` - Format with explicit transaction types

### How It Works

1. **Upload**: Upload your bank statement file through the web interface
2. **Processing**: The system:
   - Parses the file and standardizes column names
   - Identifies credit/debit transactions
   - Uses OpenAI GPT to categorize each transaction
   - Falls back to rule-based categorization if LLM is unavailable
3. **Analysis**: Generates:
   - Monthly highlights with key insights
   - Financial overview (income, expenses, savings)
   - Category breakdown with percentages
4. **Report**: Download a detailed text report with complete analysis

### Transaction Categorization

The app uses OpenAI's GPT-3.5-turbo model to intelligently categorize transactions. The LLM:
- Analyzes transaction descriptions
- Maps them to predefined categories
- Suggests new categories when appropriate
- Provides accurate categorization based on context

If the OpenAI API is unavailable, the system falls back to rule-based categorization using keyword matching.

## Project Structure

```
checkwealth/
├── app.py                  # Flask web application
├── analyzer.py            # Transaction analysis and LLM integration
├── report_generator.py    # Report generation logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── sample_statement.csv  # Sample bank statement for testing
├── templates/
│   └── index.html        # Web interface
└── uploads/              # Uploaded files and generated reports
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for LLM-based categorization

### Application Settings

Edit `app.py` to customize:
- `UPLOAD_FOLDER`: Directory for uploaded files (default: 'uploads')
- `MAX_CONTENT_LENGTH`: Maximum upload file size (default: 16MB)
- `ALLOWED_EXTENSIONS`: Allowed file extensions

## Troubleshooting

### Common Issues

1. **"No module named 'openai'"**
   - Run: `pip install -r requirements.txt`

2. **"API key not found"**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - The app will fall back to rule-based categorization

3. **"Error processing file"**
   - Check that your file has the required columns (Date, Description, Amount)
   - Ensure the file format is CSV or Excel

4. **Categories showing as "misc"**
   - LLM categorization requires a valid OpenAI API key
   - Rule-based fallback may categorize unknown transactions as "misc"

## Dependencies

- **Flask**: Web framework
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file support
- **openai**: OpenAI API integration
- **python-dotenv**: Environment variable management
- **werkzeug**: File upload utilities

## Security Notes

- Never commit your `.env` file with actual API keys
- The `.env` file is gitignored by default
- Uploaded files are stored locally in the `uploads/` directory (also gitignored)
- All file paths are sanitized to prevent path traversal attacks
- Debug mode is disabled by default (set `FLASK_ENV=development` to enable)
- Error details are logged server-side only, not exposed to users
- Consider implementing user authentication for production use
- Use HTTPS in production
- Consider implementing rate limiting for API endpoints

## Future Enhancements

- [ ] Multi-currency support
- [ ] Budget setting and tracking
- [ ] Trend analysis across multiple months
- [ ] PDF report generation
- [ ] Data visualization with charts
- [ ] User accounts and data persistence
- [ ] Mobile app
- [ ] Multiple bank account support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ by CheckWealth Team
