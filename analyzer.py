"""
Transaction Analyzer
Handles parsing, categorization, and analysis of bank statements.
"""
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TransactionAnalyzer:
    """Analyzes bank transactions and categorizes them using LLM."""
    
    # Predefined categories
    CATEGORIES = [
        'eatouts',
        'grocery',
        'transportation',
        'drinks/coffee',
        'entertainment',
        'healthcare',
        'shopping',
        'education',
        'telecom',
        'donations',
        'misc'
    ]
    
    def __init__(self):
        """Initialize the analyzer with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key) if api_key else None
        
    def process_statement(self, filepath: str) -> pd.DataFrame:
        """
        Process a bank statement file and categorize transactions.
        
        Args:
            filepath: Path to the CSV or Excel file
            
        Returns:
            DataFrame with processed transactions
        """
        # Read file based on extension
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Normalize column names (handle different bank formats)
        df.columns = df.columns.str.lower().str.strip()
        
        # Detect and standardize columns
        df = self._standardize_columns(df)
        
        # Parse dates with multiple formats
        if 'date' in df.columns:
            df['date'] = self._parse_dates(df['date'])
        
        # Determine credit/debit
        df['type'] = df.apply(self._determine_transaction_type, axis=1)
        
        # Categorize transactions
        df['category'] = df.apply(self._categorize_transaction, axis=1)
        
        return df
    
    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        """
        Parse dates with multiple format support.
        """
        # Try multiple date formats
        date_formats = [
            '%Y-%m-%d',      # 2025-07-31
            '%Y%m%d',        # 20250801
            '%m/%d/%Y',      # 07/31/2025
            '%d/%m/%Y',      # 31/07/2025
            '%Y/%m/%d',      # 2025/07/31
            '%d-%m-%Y',      # 31-07-2025
            '%m-%d-%Y',      # 07-31-2025
        ]
        
        parsed_dates = pd.Series([pd.NaT] * len(date_series), index=date_series.index)
        
        for fmt in date_formats:
            # Try parsing with this format
            mask = parsed_dates.isna()
            if mask.any():
                try:
                    parsed_dates[mask] = pd.to_datetime(
                        date_series[mask], 
                        format=fmt, 
                        errors='coerce'
                    )
                except (ValueError, TypeError, AttributeError):
                    pass
        
        # If still NaT, try general parsing
        mask = parsed_dates.isna()
        if mask.any():
            parsed_dates[mask] = pd.to_datetime(date_series[mask], errors='coerce')
        
        return parsed_dates
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names from different bank formats.
        """
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Common column mappings
        column_mappings = {
            'transaction date': 'date',
            'trans date': 'date',
            'posting date': 'date',
            'date posted': 'date',
            'value date': 'date',
            'description': 'description',
            'narration': 'description',
            'particulars': 'description',
            'details': 'description',
            'transaction details': 'description',
            'sub-description': 'sub_description',
            'amount': 'amount',
            'transaction amount': 'amount',
            'withdrawal': 'debit',
            'deposit': 'credit',
            'debit': 'debit',
            'credit': 'credit',
            'type of transaction': 'transaction_type',
            'transaction type': 'transaction_type',
            'balance': 'balance',
            'closing balance': 'balance',
            'status': 'status',
            'filter': 'filter',
            'first bank card': 'card_number'
        }
        
        # Rename columns
        for old_name, new_name in column_mappings.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        # Combine description and sub-description if both exist
        if 'description' in df.columns and 'sub_description' in df.columns:
            # Vectorized operation instead of apply
            mask = df['sub_description'].notna()
            df.loc[mask, 'description'] = df.loc[mask, 'description'] + ' ' + df.loc[mask, 'sub_description']
        
        # Handle transaction_type column (some banks specify CREDIT/DEBIT explicitly)
        if 'transaction_type' in df.columns and 'amount' in df.columns:
            # Convert amount based on transaction type using vectorized operations
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            trans_type_upper = df['transaction_type'].str.upper()
            
            # Credit transactions should be positive, debit should be negative
            credit_mask = trans_type_upper == 'CREDIT'
            debit_mask = trans_type_upper == 'DEBIT'
            
            df.loc[credit_mask, 'amount'] = df.loc[credit_mask, 'amount'].abs()
            df.loc[debit_mask, 'amount'] = -df.loc[debit_mask, 'amount'].abs()
        
        # If amount column doesn't exist, try to create it from debit/credit
        if 'amount' not in df.columns:
            if 'debit' in df.columns and 'credit' in df.columns:
                # Vectorized operations for debit/credit conversion
                df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
                df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
                
                # Combine: debits are negative, credits are positive
                df['amount'] = df['credit'] - df['debit']
        
        # Ensure required columns exist
        required_columns = ['date', 'description', 'amount']
        for col in required_columns:
            if col not in df.columns:
                # Try to find similar column
                if col == 'date' and len(df.columns) > 0:
                    # Use first column as date if not found
                    df['date'] = df.iloc[:, 0]
                elif col == 'description' and len(df.columns) > 1:
                    # Use second column as description if not found
                    df['description'] = df.iloc[:, 1]
                elif col == 'amount' and len(df.columns) > 2:
                    # Use third column as amount if not found
                    df['amount'] = pd.to_numeric(df.iloc[:, 2], errors='coerce')
        
        # Clean up amount column - ensure it's numeric
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        return df
    
    def _determine_transaction_type(self, row: pd.Series) -> str:
        """
        Determine if transaction is credit or debit.
        """
        amount = row.get('amount', 0)
        
        try:
            amount = float(amount)
            return 'credit' if amount > 0 else 'debit'
        except (ValueError, TypeError):
            return 'unknown'
    
    def _categorize_transaction(self, row: pd.Series) -> str:
        """
        Categorize transaction using LLM.
        """
        description = str(row.get('description', ''))
        amount = row.get('amount', 0)
        
        # Use LLM for categorization if available
        if self.client:
            try:
                category = self._categorize_with_llm(description, amount)
                return category
            except Exception as e:
                print(f"LLM categorization failed: {e}")
                # Fallback to rule-based
                return self._categorize_with_rules(description)
        else:
            # Use rule-based categorization as fallback
            return self._categorize_with_rules(description)
    
    def _categorize_with_llm(self, description: str, amount: float) -> str:
        """
        Use OpenAI to categorize transaction.
        """
        prompt = f"""Categorize the following bank transaction into ONE of these categories:
{', '.join(self.CATEGORIES)}

Transaction: {description}
Amount: {amount}

If the transaction doesn't fit any category well, choose 'misc'.
If you think a new category would be better, suggest it but also provide the closest existing category.

Respond with ONLY the category name in lowercase, or in format "category_name (suggested: new_category)" if suggesting a new one."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial transaction categorization expert. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        category = response.choices[0].message.content.strip().lower()
        
        # Extract base category if suggestion format is used
        if '(' in category:
            category = category.split('(')[0].strip()
        
        # Validate category
        if category not in self.CATEGORIES:
            # Try to find closest match
            for cat in self.CATEGORIES:
                if cat in category:
                    return cat
            return 'misc'
        
        return category
    
    def _categorize_with_rules(self, description: str) -> str:
        """
        Fallback rule-based categorization.
        """
        description = description.lower()
        
        # Simple keyword-based rules
        rules = {
            'eatouts': ['restaurant', 'food', 'zomato', 'swiggy', 'uber eats', 'dominos', 'pizza', 'cafe', 'dine'],
            'grocery': ['supermarket', 'grocery', 'walmart', 'target', 'whole foods', 'trader', 'market'],
            'transportation': ['uber', 'lyft', 'taxi', 'fuel', 'gas', 'petrol', 'parking', 'metro', 'bus', 'train'],
            'drinks/coffee': ['starbucks', 'coffee', 'bar', 'pub', 'brewery', 'wine', 'liquor'],
            'entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'amazon prime', 'ticket', 'concert', 'game'],
            'healthcare': ['hospital', 'pharmacy', 'medical', 'doctor', 'clinic', 'health', 'medicine'],
            'shopping': ['amazon', 'ebay', 'shop', 'mall', 'store', 'retail'],
            'education': ['school', 'college', 'university', 'course', 'tuition', 'book'],
            'telecom': ['phone', 'mobile', 'internet', 'broadband', 'telecom', 'verizon', 'at&t'],
            'donations': ['donation', 'charity', 'ngo', 'foundation']
        }
        
        for category, keywords in rules.items():
            if any(keyword in description for keyword in keywords):
                return category
        
        return 'misc'
    
    def get_monthly_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate monthly analysis from transactions.
        """
        if df.empty:
            return {}
        
        # Ensure date column is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['month'] = df['date'].dt.to_period('M')
        else:
            return {}
        
        analysis = {}
        
        for month in df['month'].unique():
            if pd.isna(month):
                continue
                
            month_data = df[df['month'] == month]
            
            # Calculate totals
            total_credit = month_data[month_data['type'] == 'credit']['amount'].sum()
            total_debit = abs(month_data[month_data['type'] == 'debit']['amount'].sum())
            
            # Category breakdown
            category_breakdown = {}
            for category in self.CATEGORIES:
                cat_data = month_data[month_data['category'] == category]
                if not cat_data.empty:
                    cat_total = abs(cat_data['amount'].sum())
                    cat_count = len(cat_data)
                    category_breakdown[category] = {
                        'total': float(cat_total),
                        'count': int(cat_count),
                        'percentage': float(cat_total / total_debit * 100) if total_debit > 0 else 0
                    }
            
            # Convert Period to string for JSON serialization
            month_key = str(month)
            analysis[month_key] = {
                'total_income': float(total_credit),
                'total_expenses': float(total_debit),
                'net_savings': float(total_credit - total_debit),
                'transaction_count': int(len(month_data)),
                'category_breakdown': category_breakdown
            }
        
        return analysis
    
    def get_monthly_highlights(self, df: pd.DataFrame) -> List[str]:
        """
        Generate monthly highlights from transactions.
        """
        highlights = []
        
        if df.empty:
            return highlights
        
        # Top spending category
        if 'category' in df.columns and 'amount' in df.columns:
            expenses = df[df['type'] == 'debit'].copy()
            if not expenses.empty:
                expenses['abs_amount'] = expenses['amount'].abs()
                category_totals = expenses.groupby('category')['abs_amount'].sum().sort_values(ascending=False)
                
                if not category_totals.empty:
                    top_category = category_totals.index[0]
                    top_amount = category_totals.iloc[0]
                    highlights.append(f"Highest spending category: {top_category.title()} (${top_amount:.2f})")
        
        # Largest single transaction
        if 'amount' in df.columns:
            largest_expense = df[df['type'] == 'debit']['amount'].min()  # Most negative
            if pd.notna(largest_expense):
                largest_expense_row = df[df['amount'] == largest_expense].iloc[0]
                highlights.append(f"Largest single expense: ${abs(largest_expense):.2f} ({largest_expense_row.get('description', 'N/A')})")
        
        # Average daily spending
        if 'date' in df.columns and 'amount' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            expenses = df[df['type'] == 'debit'].copy()
            if not expenses.empty and 'date' in expenses.columns:
                date_range = (expenses['date'].max() - expenses['date'].min()).days
                if date_range > 0:
                    total_expenses = abs(expenses['amount'].sum())
                    avg_daily = total_expenses / date_range
                    highlights.append(f"Average daily spending: ${avg_daily:.2f}")
        
        # Savings rate
        total_income = df[df['type'] == 'credit']['amount'].sum()
        total_expenses = abs(df[df['type'] == 'debit']['amount'].sum())
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            highlights.append(f"Savings rate: {savings_rate:.1f}%")
        
        return highlights
