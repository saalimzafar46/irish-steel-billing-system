import streamlit as st
import os
from pathlib import Path

# Initialize session state
if 'current_invoice' not in st.session_state:
    st.session_state.current_invoice = None

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Initialize empty data files if they don't exist
for filename in ["company.json", "clients.json", "products.json", "invoices.json"]:
    filepath = data_dir / filename
    if not filepath.exists():
        if filename == "company.json":
            content = "{}"
        else:
            content = "[]"
        with open(filepath, 'w') as f:
            f.write(content)

st.set_page_config(
    page_title="Irish Steel Billing System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏗️ Irish Steel Billing System")
st.markdown("### Professional Billing Solution for Steel Suppliers")

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Clients", "0", help="Number of registered clients")

with col2:
    st.metric("Products in Catalog", "0", help="Steel products available")

with col3:
    st.metric("Invoices This Month", "0", help="Invoices created this month")

with col4:
    st.metric("Total Revenue (EUR)", "€0.00", help="Total revenue generated")

st.markdown("---")

# Quick actions
st.markdown("### Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏢 Setup Company Info", use_container_width=True):
        st.switch_page("pages/1_Company_Setup.py")

with col2:
    if st.button("👥 Manage Clients", use_container_width=True):
        st.switch_page("pages/2_Client_Management.py")

with col3:
    if st.button("📄 Create Invoice", use_container_width=True):
        st.switch_page("pages/4_Create_Invoice.py")

# Recent activity
st.markdown("### Recent Activity")
st.info("Welcome to the Irish Steel Billing System! Start by setting up your company information.")

# Instructions
with st.expander("Getting Started"):
    st.markdown("""
    1. **Company Setup**: Configure your company details, logo, and tax information
    2. **Client Management**: Add and manage your client database
    3. **Product Catalog**: Set up your steel product inventory with specifications
    4. **Create Invoices**: Generate professional invoices with automatic calculations
    5. **Invoice History**: Track and manage all your billing history
    
    Navigate using the sidebar to access different sections of the application.
    """)
