
import argparse
import pandas as pd
import numpy as np

def calculate_lead_score(row):
    score = 0
    
    beauty_keywords = [
        'парикмахер', 'барбершоп', 'маникюр', 'ногти', 'брови', 'ресницы', 
        'косметолог', 'массаж', 'spa', 'спа', 'эпиляция', 'депиляция'
    ]
    
    auto_keywords = ['автосервис', 'шиномонтаж', 'автомойка']

    if any(keyword in str(row['name']).lower() for keyword in auto_keywords):
        score -= 20
    
    if any(keyword in str(row['name']).lower() for keyword in beauty_keywords) or \
       any(keyword in str(row['site']).lower() for keyword in beauty_keywords):
        score += 40
        
    if row['has_phone']:
        score += 10
        
    if row['rating'] >= 4.0:
        score += 10

    if row['reviews_count'] >= 20 and row['rating'] >= 4.3:
        score += 10
        
    booking_sites = ['yclients', 'dikidi', 'dikidi.net']
    if any(booking in str(row['site']).lower() for booking in booking_sites) or \
       any(booking in str(row['socials']).lower() for booking in booking_sites):
        score -= 30
        
    return score

def get_segment(score):
    if score >= 80:
        return 'beauty_micro'
    elif 50 <= score <= 79:
        return 'beauty_mid'
    else:
        return 'other'

def main():
    parser = argparse.ArgumentParser(description='Process GIS export.')
    parser.add_argument('--input', required=True, help='Path to the input Excel or CSV file.')
    parser.add_argument('--city', default='', help='City name.')
    parser.add_argument('--output', required=True, help='Path to the output CSV file.')
    
    args = parser.parse_args()
    
    if args.input.endswith('.xlsx'):
        df = pd.read_excel(args.input, engine='openpyxl')
    elif args.input.endswith('.csv'):
        df = pd.read_csv(args.input)
    else:
        print("Unsupported file type. Please use .xlsx or .csv.")
        return

    column_mapping = {
        'title': 'name',
        'address': 'address',
        'contacts': 'phones',
        'urls': 'site',
        'socialLinks': 'socials',
        'workingTimeText': 'schedule',
        'emails': 'email',
        'rating': 'rating',
        'reviewCount': 'reviews_count',
    }
    df.rename(columns=column_mapping, inplace=True)

    required_cols = {
        'phones': '', 'site': '', 'socials': '', 'schedule': '', 'email': '',
        'rating': 0.0, 'reviews_count': 0, 'name': ''
    }
    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default

    for col in ['name', 'address', 'phones', 'site', 'socials', 'schedule', 'email']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df['phones'] = df['phones'].str.replace(r'\n|;', ', ', regex=True)

    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce').fillna(0).astype(int)

    df['city'] = args.city
    df['source'] = 'gis_extension'
    df['has_phone'] = df['phones'].notna() & (df['phones'] != '')
    
    df['lead_score'] = df.apply(calculate_lead_score, axis=1)
    df['segment'] = df['lead_score'].apply(get_segment)
    
    output_columns = [
        'name', 'city', 'address', 'phones', 'site', 'socials', 'schedule', 
        'email', 'rating', 'reviews_count', 'segment', 'lead_score', 
        'has_phone', 'source'
    ]
    
    for col in output_columns:
        if col not in df.columns:
            df[col] = ''
            
    df = df[output_columns]
    
    df.to_csv(args.output, index=False, encoding='utf-8')
    print(f"Processed file saved to {args.output}")

    print("\n--- Statistics ---")
    print(f"Total rows: {len(df)}")
    print(f"Segments:\n{df['segment'].value_counts().to_string()}")
    print(f"With phone: {df['has_phone'].sum()}")

if __name__ == '__main__':
    main()
