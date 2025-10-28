"""
CheckWealth - Financial Statement Analyzer
A web-based application for analyzing bank statements with LLM-powered categorization.
"""
import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import json

from analyzer import TransactionAnalyzer
from report_generator import ReportGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize analyzer and report generator
analyzer = TransactionAnalyzer()
report_generator = ReportGenerator()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/demo')
def demo():
    """Render demo results page."""
    return render_template('demo_results.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process bank statement."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload CSV or Excel file.'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        transactions = analyzer.process_statement(filepath)
        
        # Generate analysis
        monthly_analysis = analyzer.get_monthly_analysis(transactions)
        highlights = analyzer.get_monthly_highlights(transactions)
        
        # Convert transactions to JSON-serializable format
        transactions_copy = transactions.copy()
        if 'date' in transactions_copy.columns:
            transactions_copy['date'] = transactions_copy['date'].astype(str)
        if 'month' in transactions_copy.columns:
            transactions_copy = transactions_copy.drop(columns=['month'])
        
        # Store results in session or database (simplified version uses temp file)
        results = {
            'transactions': transactions_copy.to_dict('records'),
            'monthly_analysis': monthly_analysis,
            'highlights': highlights,
            'filename': filename
        }
        
        # Save results to temp file for report generation
        results_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, default=str)
        
        return jsonify(results)
    
    except Exception as e:
        # Log the full error server-side but don't expose details to user
        app.logger.error(f'Error processing file: {str(e)}', exc_info=True)
        return jsonify({'error': 'Error processing file. Please check the file format and try again.'}), 500


@app.route('/download-report/<filename>')
def download_report(filename):
    """Generate and download detailed analysis report."""
    try:
        # Sanitize filename to prevent path traversal attacks
        filename = secure_filename(filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        results_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}_results.json")
        
        # Verify the file path is within the upload folder (prevent path traversal)
        if not os.path.abspath(results_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            return jsonify({'error': 'Invalid file path'}), 400
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'Results file not found'}), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        # Generate report
        report_path = report_generator.generate_report(results, filename)
        
        # Verify report path is within upload folder
        if not os.path.abspath(report_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            return jsonify({'error': 'Invalid report path'}), 400
        
        return send_file(report_path, as_attachment=True)
    
    except Exception as e:
        # Log the full error server-side but don't expose details to user
        app.logger.error(f'Error generating report: {str(e)}', exc_info=True)
        return jsonify({'error': 'Error generating report. Please try again.'}), 500


if __name__ == '__main__':
    # Only enable debug mode in development, not in production
    import os
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
