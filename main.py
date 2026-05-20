import streamlit as st
import pandas as pd
import re
import dns.resolver

# --- 1. VALIDATION FUNCTIONS ---

def is_valid_syntax(email):
    """Checks if the email looks like a real email address using Regex."""
    # This regex looks for letters/numbers, an @ symbol, and a valid domain ending (.com, .org)
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(regex, str(email)):
        return True
    return False

def has_mx_record(domain):
    """Checks if the domain actually has a mail server set up."""
    try:
        # Queries the DNS records for 'MX' (Mail Exchange)
        records = dns.resolver.resolve(domain, 'MX')
        return True if records else False
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        # If the domain doesn't exist or has no mail server, it fails
        return False

def validate_email(email):
    """Combines the checks and returns a status."""
    email = str(email).strip() # Clean up accidental spaces
    
    if not is_valid_syntax(email):
        return "Invalid Syntax"
        
    # Split the email at the '@' to isolate the domain
    domain = email.split('@')[1]
    
    if not has_mx_record(domain):
        return "Invalid Domain/No Inbox"
        
    return "Valid (Passed Syntax & MX)"

# --- 2. STREAMLIT USER INTERFACE ---

st.title("Internal Email Validator ✉️")
st.write("Upload your CSV. We will check the formatting and domain validity.")

# Create the file upload box
uploaded_file = st.file_uploader("Upload CSV (Must have a column named 'email')", type=['csv'])

if uploaded_file is not None:
    # Read the CSV into Pandas
    df = pd.read_csv(uploaded_file)
    
    if 'email' not in df.columns:
        st.error("Error: We couldn't find an 'email' column in your CSV.")
    else:
        st.success(f"Successfully loaded {len(df)} rows. Ready to process!")
        
        if st.button("Start Validation"):
            progress_bar = st.progress(0)
            status_list = []
            
            # Loop through the emails
            for index, row in df.iterrows():
                current_email = row['email']
                
                # Run our validation function
                result = validate_email(current_email)
                status_list.append(result)
                
                # Update the visual progress bar
                progress_bar.progress((index + 1) / len(df))
                
            # Add the new column to the dataframe
            df['Validation_Status'] = status_list
            
            st.write("### Validation Complete!")
            st.dataframe(df.head(10)) # Show the first 10 rows as a preview
            
            # Convert back to CSV for downloading
            csv_data = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download Validated List",
                data=csv_data,
                file_name='validated_results.csv',
                mime='text/csv'
            )
