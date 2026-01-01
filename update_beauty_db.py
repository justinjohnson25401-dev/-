
import argparse
import pandas as pd
from datetime import datetime
from processing_logic import process_raw_file

def main():
    parser = argparse.ArgumentParser(description='Update beauty database.')
    parser.add_argument('--input', required=True, help='Path to the new 2GIS export file (xlsx or csv)')
    parser.add_argument('--city', required=True, help='City (string)')
    parser.add_argument('--db', default='beauty_db.csv', help='Path to the unified database (default: beauty_db.csv)')
    parser.add_argument('--min_score', type=int, default=0, help='Minimum lead_score to write to the database (default: 0)')
    args = parser.parse_args()

    new_data_df = process_raw_file(args.input, args.city)
    
    new_data_df = new_data_df[new_data_df['has_phone'] == True]
    new_data_df = new_data_df[new_data_df['lead_score'] >= args.min_score]

    new_data_df['company_key'] = new_data_df.apply(lambda row: f"{row['city']}||{row['address']}||{row['name']}".lower().strip(), axis=1)
    
    try:
        db_df = pd.read_csv(args.db)
        initial_db_count = len(db_df)
    except FileNotFoundError:
        db_df = pd.DataFrame(columns=[
            'name', 'city', 'address', 'phones', 'site', 'socials', 'schedule', 
            'email', 'rating', 'reviews_count', 'segment', 'lead_score', 'has_phone', 
            'has_telegram', 'has_whatsapp', 'source', 'first_seen_at', 'company_key'
        ])
        initial_db_count = 0

    new_records = new_data_df[~new_data_df['company_key'].isin(db_df['company_key'])]
    
    if not new_records.empty:
        new_records['first_seen_at'] = datetime.utcnow().isoformat()
        
        final_df = pd.concat([db_df, new_records], ignore_index=True)
    else:
        final_df = db_df

    final_df = final_df[[
        'name', 'city', 'address', 'phones', 'site', 'socials', 'schedule', 
        'email', 'rating', 'reviews_count', 'segment', 'lead_score', 'has_phone',
        'has_telegram', 'has_whatsapp', 'source', 'first_seen_at', 'company_key'
    ]]

    final_df.to_csv(args.db, index=False)

    print(f"Initial records in db: {initial_db_count}")
    print(f"New companies added: {len(new_records)}")
    print(f"Total companies in db: {len(final_df)}")
    print("\nSegment distribution in the updated database:")
    print(final_df['segment'].value_counts())

if __name__ == "__main__":
    main()
