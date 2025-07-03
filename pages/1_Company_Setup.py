import streamlit as st
from models.company import Company
from utils.validators import Validators
from utils.formatters import Formatters

st.set_page_config(page_title="Company Setup", page_icon="🏢", layout="wide")

st.title("🏢 Company Setup")
st.markdown("Configure your company information for invoices and business documents.")

# Load existing company data
company = Company.load()

# Company Information Form
with st.form("company_form"):
    st.subheader("Basic Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Company Name *", value=company.name, help="Your business name as it appears on invoices")
        address = st.text_area("Address *", value=company.address, help="Street address")
        city = st.text_input("City *", value=company.city)
        county = st.text_input("County", value=company.county, help="e.g., Dublin, Cork")
        
    with col2:
        postal_code = st.text_input("Postal Code (Eircode)", value=company.postal_code, help="e.g., D02 XY45")
        country = st.text_input("Country", value=company.country)
        phone = st.text_input("Phone Number", value=company.phone, help="Irish format: +353 1 234 5678")
        email = st.text_input("Email Address", value=company.email)
    
    st.subheader("Registration & Tax Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vat_number = st.text_input("VAT Number", value=company.vat_number, help="Irish format: IE1234567T")
        company_registration = st.text_input("Company Registration Number", value=company.company_registration)
        website = st.text_input("Website", value=company.website, help="https://yourcompany.ie")
    
    with col2:
        st.write("")  # Spacing
    
    st.subheader("Banking Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bank_name = st.text_input("Bank Name", value=company.bank_name)
        bank_account = st.text_input("Account Number", value=company.bank_account)
        
    with col2:
        bank_sort_code = st.text_input("Sort Code", value=company.bank_sort_code, help="6 digits: 12-34-56")
        iban = st.text_input("IBAN", value=company.iban, help="Irish format: IE29 AIBK 9311 5212 3456 78")
    
    submitted = st.form_submit_button("Save Company Information", use_container_width=True)
    
    if submitted:
        errors = []
        
        # Validate required fields
        if not name.strip():
            errors.append("Company name is required")
        if not address.strip():
            errors.append("Address is required")
        if not city.strip():
            errors.append("City is required")
        
        # Validate optional fields
        if email:
            valid, error = Validators.validate_email(email)
            if not valid:
                errors.append(f"Email: {error}")
        
        if phone:
            valid, error = Validators.validate_phone(phone)
            if not valid:
                errors.append(f"Phone: {error}")
        
        if vat_number:
            valid, error = Validators.validate_vat_number(vat_number)
            if not valid:
                errors.append(f"VAT Number: {error}")
        
        if iban:
            valid, error = Validators.validate_iban(iban)
            if not valid:
                errors.append(f"IBAN: {error}")
        
        if postal_code:
            valid, error = Validators.validate_postal_code(postal_code)
            if not valid:
                errors.append(f"Postal Code: {error}")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Save company information
            updated_company = Company(
                name=name.strip(),
                address=address.strip(),
                city=city.strip(),
                county=county.strip(),
                postal_code=postal_code.strip(),
                country=country.strip(),
                phone=phone.strip(),
                email=email.strip(),
                website=website.strip(),
                vat_number=vat_number.strip(),
                company_registration=company_registration.strip(),
                bank_name=bank_name.strip(),
                bank_account=bank_account.strip(),
                bank_sort_code=bank_sort_code.strip(),
                iban=iban.strip()
            )
            
            updated_company.save()
            st.success("✅ Company information saved successfully!")
            st.rerun()

# Preview section
if company.name:
    st.markdown("---")
    st.subheader("Company Information Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Business Details:**")
        st.write(f"**{company.name}**")
        st.write(company.address)
        st.write(f"{company.city}, {company.county} {company.postal_code}")
        st.write(company.country)
        
        if company.phone:
            st.write(f"📞 {Formatters.format_phone(company.phone)}")
        if company.email:
            st.write(f"📧 {company.email}")
        if company.website:
            st.write(f"🌐 {company.website}")
    
    with col2:
        st.markdown("**Registration & Banking:**")
        if company.vat_number:
            st.write(f"VAT: {Formatters.format_vat_number(company.vat_number)}")
        if company.company_registration:
            st.write(f"Registration: {company.company_registration}")
        
        if company.bank_name or company.iban:
            st.write("**Banking Details:**")
            if company.bank_name:
                st.write(f"Bank: {company.bank_name}")
            if company.iban:
                st.write(f"IBAN: {Formatters.format_iban(company.iban)}")
            if company.bank_sort_code:
                st.write(f"Sort Code: {company.bank_sort_code}")

# Tips section
with st.expander("💡 Setup Tips"):
    st.markdown("""
    **Required Fields:**
    - Company Name, Address, and City are required for invoice generation
    
    **VAT Number:**
    - Irish VAT numbers follow the format: IE1234567T or IE1234567AB
    - Required if you're VAT registered and want to show VAT on invoices
    
    **Banking Information:**
    - IBAN is required for customers to make payments
    - Sort code format: 12-34-56 (6 digits with hyphens)
    
    **Phone Numbers:**
    - Irish landline: +353 1 234 5678 or 01 234 5678
    - Irish mobile: +353 87 123 4567 or 087 123 4567
    """)
