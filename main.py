import streamlit as st
import pandas as pd
import re
import dns.resolver

# --- 1. VALIDATION FUNCTIONS (Unchanged) ---

def is_valid_syntax(email):
    """Checks if the email looks like a real email address using Regex."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(regex, str(email)):
        return True
    return False

def has_mx_record(domain):
    """Checks if the domain actually has a mail server set up."""
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return True if records else False
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.name.EmptyLabel):
        return False

def validate_email(email):
    """Combines the checks and returns a status."""
    email = str(email).strip() # Clean up accidental spaces
    
    if not email:
        return "Empty"
        
    if not is_valid_syntax(email):
        return "Invalid Syntax"
        
    domain = email.split('@')[1]
    
    if not has_mx_record(domain):
        return "Invalid Domain/No Inbox"
        
    return "Valid (Passed Syntax & MX)"

# --- 2. STREAMLIT USER INTERFACE ---

st.title("Internal Email Validator ✉️")
st.write("Check email formatting and domain validity instantly. No data is stored.")

# Create two tabs for the user to choose from
tab1, tab2 = st.tabs(["📝 Type or Paste Emails", "📁 Upload CSV"])

# --- TAB 1: MANUAL ENTRY ---
with tab1:
    st.write("### Manual Entry")
    # A larger text box for pasting multiple emails
    pasted_emails = st.text_area("Type or paste emails here (one per line, or separated by commas):", height=150)
    
    if st.button("Validate Typed Emails"):
        if not pasted_emails.strip():
            st.warning("Please enter at least one email.")
        else:
            # Replace commas with newlines, then split the text into a list of emails
            clean_text = pasted_emails.replace(',', '\n')
            email_list = [e.strip() for e in clean_text.split('\n') if e.strip()]
            
            if email_list:
                progress_bar = st.progress(0)
                results_data = []
                
                for index, email in enumerate(email_list):
                    status = validate_email(email)
                    results_data.append({"Email": email, "Validation_Status": status})
                    progress_bar.progress((index + 1) / len(email_list))
                
                # Convert results to a DataFrame for clean display
                results_df = pd.DataFrame(results_data)
                
                st.write("### Validation Complete!")
                st.dataframe(results_df)

# --- TAB 2: CSV UPLOAD ---
with tab2:
    st.write("### Bulk Upload")
    uploaded_file = st.file_uploader("Upload CSV (Must have a column named 'email')", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Make the column check case-insensitive (e.g., 'Email' or 'email')
        df.columns = [col.lower() for col in df.columns]
        
        if 'email' not in df.columns:
            st.error("Error: We couldn't find an 'email' column in your CSV.")
        else:
            st.success(f"Successfully loaded {len(df)} rows. Ready to process!")
            
            if st.button("Validate CSV Emails"):
                progress_bar = st.progress(0)
                status_list = []
                
                for index, row in df.iterrows():
                    current_email = row['email']
                    result = validate_email(current_email)
                    status_list.append(result)
                    progress_bar.progress((index + 1) / len(df))
                    
                df['Validation_Status'] = status_list
                
                st.write("### Validation Complete!")
                st.dataframe(df.head(10)) 
                
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Validated List",
                    data=csv_data,
                    file_name='validated_results.csv',
                    mime='text/csv'
                )
