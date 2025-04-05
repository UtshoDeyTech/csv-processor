import polars as pl
import os
import re
from urllib.parse import urlparse
import difflib

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

def filter_valid_emails(df, column_name):
    # Regular expression for basic email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Filter rows with valid emails
    return df.filter(
        pl.col(column_name).cast(str).str.contains(email_regex)
    )
    
def extract_domain_from_email(email):
    """Extract domain from email address"""
    try:
        if not email or not isinstance(email, str):
            return None
        return email.split('@')[1].lower() if '@' in email else None
    except Exception:  # Fixed bare except
        return None

def extract_username_from_email(email):
    """Extract username part from email address"""
    try:
        if not email or not isinstance(email, str):
            return None
        return email.split('@')[0].lower() if '@' in email else None
    except Exception:  # Fixed bare except
        return None

def extract_domain_from_url(url):
    """Extract domain from URL"""
    try:
        if not url or not isinstance(url, str):
            return None
            
        # Handle URLs without scheme
        if not re.match(r'^https?://', url):
            url = 'http://' + url
        
        domain = urlparse(url).netloc
        # Remove www. if present
        return re.sub(r'^www\.', '', domain).lower()
    except Exception:  # Fixed bare except
        return None
        
def extract_base_domain(domain):
    """Extract base domain without TLD"""
    if not domain:
        return None
    
    # Remove TLD (e.g., .com, .org)
    base = domain.split('.')[0] if '.' in domain else domain
    return base.lower()

def calculate_domain_similarity(email, website_domain, check_username=True):
    if not email or not website_domain:
        return 0.0
        
    # Extract email parts
    email_domain = extract_domain_from_email(email)
    
    # Case 1: Direct domain match
    domain_similarity = 0.0
    if email_domain and website_domain:
        domain_similarity = difflib.SequenceMatcher(None, email_domain, website_domain).ratio()
    
    # If not checking username or already perfect match, return domain similarity
    if not check_username or domain_similarity == 1.0:
        return domain_similarity
        
    # Case 2: Website domain appears in email username
    username_contains_domain = 0.0
    email_username = extract_username_from_email(email)
    website_base = extract_base_domain(website_domain)
    
    if website_base and email_username:
        if website_base in email_username:
            # Calculate how much of the username is the domain
            username_contains_domain = len(website_base) / len(email_username)
    
    # Return the higher of the two similarity scores
    return max(domain_similarity, username_contains_domain)

def domain_similarity_filter(df, email_column, domain_column, threshold=0.75, check_username=True, progress_callback=None):
    # We'll use a list comprehension to create a boolean mask
    mask = []
    
    # Convert to Python list for easier processing
    emails = df[email_column].to_list()
    domains = df[domain_column].to_list()
    total_rows = len(emails)
    
    # Check each row
    for i in range(total_rows):
        email = emails[i]
        domain = domains[i]
        
        # Default to excluding rows with missing data
        if not isinstance(email, str) or not isinstance(domain, str):
            mask.append(False)
            continue
            
        # Extract domain from website
        website_domain = extract_domain_from_url(domain)
        
        # Calculate similarity
        similarity = calculate_domain_similarity(email, website_domain, check_username)
        
        # Add to mask
        mask.append(similarity >= threshold)
        
        # Update progress every 100 rows or at the end
        if progress_callback and (i % 100 == 0 or i == total_rows - 1):
            progress_percent = min(90, int((i + 1) / total_rows * 90))
            progress_callback(progress_percent, f"Processed {i+1} of {total_rows} rows")
    
    # Convert mask to Polars expression
    filter_mask = pl.Series(mask)
    
    # Apply filter and update progress
    if progress_callback:
        progress_callback(95, "Applying filter...")
    
    result = df.filter(filter_mask)
    
    if progress_callback:
        progress_callback(100, "Completed")
    
    return result