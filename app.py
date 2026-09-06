from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import io
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auto-scan', methods=['POST'])
def auto_scan():
    # Automated market discovery dataset representing trending niches across Amazon & wholesale directories
    trending_pool = [
        {"product": "Silicone Travel Bottle Set", "price": 19.99, "est_sales": 450, "reviews": 120},
        {"product": "Bamboo Drawer Dividers", "price": 27.99, "est_sales": 620, "reviews": 95},
        {"product": "Stainless Steel Measuring Spoons", "price": 14.50, "est_sales": 280, "reviews": 450},
        {"product": "Acrylic Desktop Organizer", "price": 24.99, "est_sales": 340, "reviews": 180},
        {"product": "Insulated Coffee Tumbler 20oz", "price": 22.50, "est_sales": 890, "reviews": 1450},
        {"product": "Magnetic Cable Clips (Pack of 6)", "price": 16.99, "est_sales": 720, "reviews": 110},
        {"product": "Ergonomic Foot Rest for Under Desk", "price": 29.99, "est_sales": 410, "reviews": 165},
        {"product": "Silicone Baking Mats (Set of 2)", "price": 18.99, "est_sales": 530, "reviews": 88},
        {"product": "Reusable Produce Bags (Pack of 9)", "price": 15.99, "est_sales": 390, "reviews": 135},
        {"product": "Minimalist Leather Passport Holder", "price": 17.50, "est_sales": 310, "reviews": 74},
        {"product": "Heavy Duty Resistance Bands Set", "price": 21.99, "est_sales": 940, "reviews": 2100},
        {"product": "LED Under Cabinet Lighting Bar", "price": 25.00, "est_sales": 480, "reviews": 190}
    ]
    
    results = []
    for item in trending_pool:
        price = item['price']
        sales = item['est_sales']
        reviews = item['reviews']
        
        # Rule of Threes check
        is_qualified = (15.0 <= price <= 30.0) and (sales >= 300.0) and (reviews < 200)
        est_revenue = round(price * sales, 2)
        
        results.append({
            'product': item['product'],
            'price': price,
            'est_sales': sales,
            'reviews': reviews,
            'est_revenue': est_revenue,
            'qualified': is_qualified,
            'score': '🔥 High Potential' if is_qualified else 'Standard'
        })
        
    qualified_count = sum(1 for r in results if r['qualified'])
    
    return jsonify({
        'success': True,
        'total_scanned': len(results),
        'qualified_count': qualified_count,
        'results': results
    })

@app.route('/api/scan', methods=['POST'])
def scan_products():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            return jsonify({'success': False, 'error': 'Please upload a valid CSV or Excel file'}), 400
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read()))
        else:
            df = pd.read_excel(io.BytesIO(file.read()))
            
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
