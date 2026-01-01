
import pandas as pd
import numpy as np
import re

def extract_tg_link(text: str) -> str:
    # Ищем полную ссылку с протоколом
    match = re.search(r'https?://t\.me/[^\s,"]+', str(text))
    if match:
        return match.group(0)
    # Резервный вариант: короткая форма без протокола
    match2 = re.search(r'\bt\.me/[^\s,"]+', str(text))
    return match2.group(0) if match2 else ''

def calculate_lead_score(row):
    score = 0

    if row.get('has_telegram'):
        score += 20

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

    combined = (
        df.get('phones', pd.Series(dtype=str)).fillna('').astype(str) + ' ' +
        df.get('site', pd.Series(dtype=str)).fillna('').astype(str) + ' ' +
        df.get('socials', pd.Series(dtype=str)).fillna('').astype(str)
    )

    df['tg_link'] = combined.apply(extract_tg_link)
    df['has_telegram'] = df['tg_link'] != ''

    df['city'] = city
    df['has_phone'] = df['phones'].apply(lambda x: pd.notna(x) and x != '')
    df['source'] = '2gis'
    
    df['lead_score'] = df.apply(calculate_lead_score, axis=1)
    df['segment'] = df['lead_score'].apply(get_segment)
    
    return df
