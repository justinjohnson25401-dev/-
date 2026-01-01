
import pandas as pd
import numpy as np

def calculate_lead_score(row):
    score = 0

    text_blob = " ".join([
        str(row.get('phones', '')),
        str(row.get('site', '')),
        str(row.get('socials', '')),
    ]).lower()

    if 't.me/' in text_blob or 'telegram.me/' in text_blob:
        score += 15
    if 'wa.me/' in text_blob or 'whatsapp' in text_blob:
        score += 10
    
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

def process_raw_file(input_path, city):
    if input_path.endswith('.xlsx'):
        df = pd.read_excel(input_path, engine='openpyxl')
    elif input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    else:
        raise ValueError("Unsupported file type. Please use .xlsx or .csv.")

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

    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
    else:
        df['rating'] = 0.0

    if 'reviews_count' in df.columns:
        df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce').fillna(0).astype(int)
    else:
        df['reviews_count'] = 0
    
    for col in ['name', 'address', 'phones', 'site', 'socials', 'schedule', 'email']:
        if col not in df.columns:
            df[col] = np.nan

    df['city'] = city
    df['has_phone'] = df['phones'].apply(lambda x: pd.notna(x) and x != '')
    df['source'] = '2gis'
    
    df['lead_score'] = df.apply(calculate_lead_score, axis=1)
    df['segment'] = df['lead_score'].apply(get_segment)
    
    return df
