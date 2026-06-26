import argparse

def main():
    parser = argparse.ArgumentParser(description="Data Processing Tool")
    
    parser.add_argument('--input', type=str, required=True, help='Input file path')
    parser.add_argument('--output', type=str, required=True, help='Output file path')
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'parquet'], default='csv', help='Output format')
    parser.add_argument('--rows', type=int, default=1000, help='Number of rows to process')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Format: {args.format}")
    print(f"Rows: {args.rows}")
    
    if args.verbose:
        print("Verbose mode enabled")
    
    process_data(args.input, args.output, args.format, args.rows)

def process_data(input_file, output_file, file_format, num_rows):
    import pandas as pd
    import json
    
    print(f"Processing {num_rows} rows from {input_file}")
    
    # Read CSV file
    df = pd.read_csv(input_file, nrows=num_rows)
    
    # Save in specified format
    if file_format == 'csv':
        df.to_csv(output_file, index=False)
    elif file_format == 'json':
        df.to_json(output_file, orient='records', indent=2)
    elif file_format == 'parquet':
        df.to_parquet(output_file, index=False)
    
    print(f"Saving as {file_format} to {output_file}")
    print(f"✓ File created successfully at {output_file}")

if __name__ == "__main__":
    main()