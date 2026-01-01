
import pandas as pd
from processing_logic import process_raw_file

def main():
    # This script is now a wrapper around the shared logic
    # You can adapt it to your specific needs, for example, by adding
    # command-line arguments to specify input/output files.
    input_file = "unique_items_2gis-1.xlsx"
    output_file = "processed_2gis_export.csv"
    city = "Екатеринбург"  # Example city

    processed_df = process_raw_file(input_file, city)
    
    # You can add further processing specific to this script here
    
    processed_df.to_csv(output_file, index=False)
    print(f"Processed file saved to {output_file}")

if __name__ == "__main__":
    main()
