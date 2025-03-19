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
