"""
Report Generator
Creates detailed analysis reports from transaction data.
"""
import os
from typing import Dict, Any
from datetime import datetime
import json


class ReportGenerator:
    """Generates detailed financial analysis reports."""
    
    def generate_report(self, results: Dict[str, Any], filename: str) -> str:
        """
        Generate a detailed text report from analysis results.
        
        Args:
            results: Analysis results dictionary
            filename: Original filename
            
        Returns:
            Path to generated report file
        """
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("FINANCIAL STATEMENT ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Source File: {filename}")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Monthly Highlights
        report_lines.append("MONTHLY HIGHLIGHTS")
        report_lines.append("-" * 80)
        highlights = results.get('highlights', [])
        if highlights:
            for i, highlight in enumerate(highlights, 1):
                report_lines.append(f"{i}. {highlight}")
        else:
            report_lines.append("No highlights available")
        report_lines.append("")
        
        # Monthly Analysis
        report_lines.append("DETAILED MONTHLY ANALYSIS")
        report_lines.append("-" * 80)
        
        monthly_analysis = results.get('monthly_analysis', {})
        for month, data in sorted(monthly_analysis.items()):
            report_lines.append(f"\n📅 {month}")
            report_lines.append("-" * 40)
            
            # Summary
            report_lines.append(f"  Total Income:      ${data['total_income']:,.2f}")
            report_lines.append(f"  Total Expenses:    ${data['total_expenses']:,.2f}")
            report_lines.append(f"  Net Savings:       ${data['net_savings']:,.2f}")
            report_lines.append(f"  Transactions:      {data['transaction_count']}")
            report_lines.append("")
            
            # Category Breakdown
            report_lines.append("  Category Breakdown:")
            category_breakdown = data.get('category_breakdown', {})
            
            if category_breakdown:
                # Sort by total amount
                sorted_categories = sorted(
                    category_breakdown.items(),
                    key=lambda x: x[1]['total'],
                    reverse=True
                )
                
                for category, cat_data in sorted_categories:
                    report_lines.append(
                        f"    • {category.title():20s} "
                        f"${cat_data['total']:>10,.2f}  "
                        f"({cat_data['percentage']:>5.1f}%)  "
                        f"{cat_data['count']:>3d} transactions"
                    )
            else:
                report_lines.append("    No categorized transactions")
            
            report_lines.append("")
        
        # Transaction Details
        report_lines.append("\nTRANSACTION DETAILS")
        report_lines.append("-" * 80)
        
        transactions = results.get('transactions', [])
        if transactions:
            report_lines.append(f"Total Transactions: {len(transactions)}")
            report_lines.append("")
            
            # Group by category for detailed view
            from collections import defaultdict
            by_category = defaultdict(list)
            
            for txn in transactions:
                category = txn.get('category', 'misc')
                by_category[category].append(txn)
            
            for category in sorted(by_category.keys()):
                report_lines.append(f"\n{category.upper()}")
                report_lines.append("-" * 40)
                
                for txn in by_category[category]:
                    date = txn.get('date', 'N/A')
                    desc = txn.get('description', 'N/A')
                    amount = txn.get('amount', 0)
                    txn_type = txn.get('type', 'unknown')
                    
                    # Format amount with sign
                    amount_str = f"${abs(float(amount)):,.2f}"
                    if txn_type == 'credit':
                        amount_str = f"+{amount_str}"
                    else:
                        amount_str = f"-{amount_str}"
                    
                    report_lines.append(f"  {date[:10] if isinstance(date, str) else str(date)[:10]:12s} {desc[:40]:40s} {amount_str:>15s}")
        else:
            report_lines.append("No transactions available")
        
        # Footer
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        # Write report to file
        report_filename = f"{filename}_analysis_report.txt"
        report_path = os.path.join('uploads', report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return report_path
