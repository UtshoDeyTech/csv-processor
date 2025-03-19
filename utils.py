import polars as pl
import os

def load_csv(file_name):
    if not os.path.exists(file_name):
        print("File not found!")
        return None
    return pl.read_csv(file_name)

def word_match(file_name, selected_column_names, search_values, include=True, case_insensitive=True):
    df = load_csv(file_name)
    if df is None:
        return None, 0, None

    if case_insensitive:
        masks = [pl.any_horizontal([pl.col(col).cast(str).str.to_lowercase().str.contains(val.lower()) for val in search_values]) for col in selected_column_names]
        mask = pl.any_horizontal(masks)
    else:
        search_pattern = "|".join(search_values)
        masks = [pl.col(col).cast(str).str.contains(search_pattern) for col in selected_column_names]
        mask = pl.any_horizontal(masks)
    
    filtered_df = df.filter(mask if include else ~mask)
    row_count = filtered_df.shape[0]
    print(f"Filtered rows count: {row_count}")
    return "filtered_output.csv", row_count, filtered_df

def remove_duplicates(file_name, selected_column_names):
    df = load_csv(file_name)
    if df is None:
        return None, 0, None

    cleaned_df = df.unique(subset=selected_column_names)
    row_count = cleaned_df.shape[0]
    print(f"Cleaned rows count: {row_count}")
    return "cleaned_output.csv", row_count, cleaned_df

def find_and_replace(df, column_name, old_value, new_value):
    if not old_value:  # If no old value is provided, replace null values
        df = df.with_columns(
            pl.col(column_name).fill_null(new_value)
        )
    else:
        df = df.with_columns(
            pl.when(pl.col(column_name).cast(str) == old_value)
            .then(new_value)
            .otherwise(pl.col(column_name))
            .alias(column_name)
        )
    
    return df

def main():
    file_name = input("Enter the CSV file name (must be in the current folder): ")
    if not os.path.exists(file_name):
        print("File not found!")
        return
    
    df = load_csv(file_name)
    if df is None:
        return
    
    current_df = df.clone()
    
    while True:
        print("\nSelect an option:")
        print("1. Word Match")
        print("2. Duplicate Remover")
        print("3. Find and Replace")
        print("4. Download CSV")
        print("5. Reset to Original")
        print("6. Exit")
        
        choice = input("Enter your choice: ")
        if choice == '1':
            print("1. Include")
            print("2. Exclude")
            include = input("Enter your choice: ") == '1'
            
            print("Case sensitivity:")
            print("1. Case sensitive")
            print("2. Case insensitive")
            case_insensitive = input("Enter your choice: ") == '2'
            
            print("Select columns by number:")
            for idx, col in enumerate(current_df.columns, start=1):
                print(f"{col} --- {idx}")
            selected_columns = input("Enter column numbers (comma-separated): ")
            selected_column_names = [current_df.columns[int(i)-1] for i in selected_columns.split(',')]
            
            search_values = input("Enter Search values (comma-separated): ").split(',')
            search_values = [value.strip() for value in search_values]
            
            current_df = word_match(file_name, selected_column_names, search_values, include, case_insensitive)[2]
            
        elif choice == '2':
            print("Select columns by number to check duplicates:")
            for idx, col in enumerate(current_df.columns, start=1):
                print(f"{col} --- {idx}")
            selected_columns = input("Enter column numbers (comma-separated): ")
            selected_column_names = [current_df.columns[int(i)-1] for i in selected_columns.split(',')]
            
            before_count = current_df.shape[0]
            current_df = current_df.unique(subset=selected_column_names)
            after_count = current_df.shape[0]
            
            print(f"Removed {before_count - after_count} duplicate rows")
            
        elif choice == '3':
            print("Select column for Find and Replace:")
            for idx, col in enumerate(current_df.columns, start=1):
                print(f"{col} --- {idx}")
            selected_column = input("Enter column number: ")
            column_name = current_df.columns[int(selected_column)-1]
            
            old_value = input("Enter value to find: ")
            new_value = input("Enter replacement value: ")
            
            current_df = find_and_replace(current_df, column_name, old_value, new_value)
            print(f"Replaced '{old_value}' with '{new_value}' in column '{column_name}'.")
            
        elif choice == '4':  # Always download as CSV
            print("Downloading CSV...")

            print("Select columns to include (default: all columns)")
            for idx, col in enumerate(current_df.columns, start=1):
                print(f"{col} --- {idx}")
            selected_columns = input("Enter column numbers (comma-separated) or press Enter for all: ")

            if selected_columns:
                selected_column_names = [current_df.columns[int(i)-1] for i in selected_columns.split(',')]
                download_df = current_df.select(selected_column_names)
            else:
                download_df = current_df

            output_file = input("Enter output file name (default: output): ") or "output"
            
            download_df.write_csv(f"{output_file}.csv")
            print(f"✅ Downloaded {output_file}.csv ({download_df.shape[0]} rows)")
            
        elif choice == '5':
            current_df = df.clone()
            print("Data reset to original.")
            
        elif choice == '6':
            print("Exiting program.")
            break
        
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
