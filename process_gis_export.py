
import argparse
import pandas as pd
import numpy as np

def calculate_lead_score(row):
    score = 0
    
    beauty_keywords = [
        'парикмахер', 'барбершоп', 'маникюр', 'ногти', 'брови', 'ресницы', 
        'косметолог', 'массаж', 'spa', 'спа', 'эпиляция', 'депиляция'
    ]
    
    if any(keyword in str(row['name']).lower() for keyword in beauty_keywords) or \
       any(keyword in str(row['site']).lower() for keyword in beauty_keywords):
        score += 40
        
    if row['has_phone']:
        score += 10
        
    if row['rating'] >= 4.0:
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
    parser.add_argument('--input', required=True, help='Path to the input Excel file.')
    parser.add_argument('--city', default='', help='City name.')
    parser.add_argument('--output', required=True, help='Path to the output CSV file.')
    
    args = parser.parse_args()
    
    df = pd.read_excel(args.input)
    
    column_mapping = {
        'Название': 'name',
        'Адрес': 'address',
        'Телефон': 'phones',
        'Сайт': 'site',
        'Соцсети': 'socials',
        'Время работы': 'schedule',
        'Email': 'email',
        'Рейтинг': 'rating',
        'Количество отзывов': 'reviews_count'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    df['city'] = args.city
    df['source'] = 'gis_extension'
    
    df['has_phone'] = df['phones'].notna() & (df['phones'] != '')
    
    # Fill missing numeric/string columns that are used in calculations
    df['rating'] = pd.to_numeric(df.get('rating', 0), errors='coerce').fillna(0)
    df['name'] = df.get('name', '').fillna('')
    df['site'] = df.get('site', '').fillna('')
    df['socials'] = df.get('socials', '').fillna('')

    df['lead_score'] = df.apply(calculate_lead_score, axis=1)
    df['segment'] = df['lead_score'].apply(get_segment)
    
    output_columns = [
        'name', 'city', 'address', 'phones', 'site', 'socials', 'schedule', 
        'email', 'rating', 'reviews_count', 'segment', 'lead_score', 
        'has_phone', 'source'
    ]
    
    # Ensure all required columns exist, fill with defaults if not
    for col in output_columns:
        if col not in df.columns:
            df[col] = ''
            
    df = df[output_columns]
    
    df.to_csv(args.output, index=False, encoding='utf-8')
    print(f"Processed file saved to {args.output}")

if __name__ == '__main__':
    main()
