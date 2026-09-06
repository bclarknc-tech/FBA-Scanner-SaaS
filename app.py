from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_products():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            return jsonify({'success': False, 'error': 'Please upload a valid CSV or Excel file'}), 400
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read()))
        else:
            df = pd.read_excel(io.BytesIO(file.read()))
            
        # Normalize columns
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        prod_col = next((c for c in df.columns if 'product' in c or 'title' in c or 'name' in c or 'asin' in c), df.columns[0])
        price_col = next((c for c in df.columns if 'price' in c or 'cost' in c), None)
        sales_col = next((c for c in df.columns if 'sales' in c or 'volume' in c or 'demand' in c), None)
        review_col = next((c for c in df.columns if 'review' in c or 'ratings count' in c), None)
        
        results = []
        for _, row in df.iterrows():
            try:
                name = str(row[prod_col])
                price = float(row[price_col]) if price_col and pd.notna(row[price_col]) else 19.99
                sales = float(row[sales_col]) if sales_col and pd.notna(row[sales_col]) else 350.0
                reviews = int(row[review_col]) if review_col and pd.notna(row[review_col]) else 100
                
                # Rule of Threes check
                is_qualified = (15.0 <= price <= 30.0) and (sales >= 300.0) and (reviews < 200)
                
                est_revenue = round(price * sales, 2)
                
                results.append({
                    'product': name,
                    'price': price,
                    'est_sales': sales,
                    'reviews': reviews,
                    'est_revenue': est_revenue,
                    'qualified': is_qualified,
                    'score': '🔥 High Potential' if is_qualified else 'Standard'
                })
            except:
                continue
                
        qualified_count = sum(1 for r in results if r['qualified'])
        
        return jsonify({
            'success': True,
            'total_scanned': len(results),
            'qualified_count': qualified_count,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
