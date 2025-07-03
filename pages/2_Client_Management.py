import streamlit as st
from models.client import Client, ClientManager
from utils.validators import Validators
from utils.formatters import Formatters
import pandas as pd

st.set_page_config(page_title="Client Management", page_icon="👥", layout="wide")

st.title("👥 Client Management")
st.markdown("Manage your customer database and billing information.")

# Initialize client manager
client_manager = ClientManager()

# Sidebar for actions
with st.sidebar:
    st.subheader("Actions")
    action = st.radio("Choose Action:", ["View Clients", "Add New Client", "Edit Client"])

if action == "View Clients":
    st.subheader("Client Database")
    
    clients = client_manager.get_all_clients()
    
    if not clients:
        st.info("No clients found. Add your first client using the sidebar.")
    else:
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search clients...", placeholder="Search by name, email, or city")
        with col2:
            show_all = st.checkbox("Show all details", help="Show extended client information")
        
        # Filter clients based on search
        if search_term:
            filtered_clients = [
                client for client in clients
                if (search_term.lower() in client.name.lower() or
                    search_term.lower() in client.email.lower() or
                    search_term.lower() in client.city.lower() or
                    search_term.lower() in client.contact_person.lower())
            ]
        else:
            filtered_clients = clients
        
        if not filtered_clients:
            st.warning("No clients match your search criteria.")
        else:
            # Display clients
            for client in filtered_clients:
                with st.expander(f"**{client.name}** - {client.city}", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Contact:** {client.contact_person}")
                        st.write(f"**Email:** {client.email}")
                        st.write(f"**Phone:** {Formatters.format_phone(client.phone)}")
                        if client.vat_number:
                            st.write(f"**VAT:** {client.vat_number}")
                    
                    with col2:
                        st.write(f"**Address:** {client.address}")
                        st.write(f"**City:** {client.city}, {client.county}")
                        st.write(f"**Payment Terms:** {client.payment_terms}")
                        if client.credit_limit > 0:
                            st.write(f"**Credit Limit:** {Formatters.format_currency(client.credit_limit)}")
                    
                    with col3:
                        if st.button(f"Edit", key=f"edit_{client.id}"):
                            st.session_state.edit_client_id = client.id
                            st.rerun()
                        
                        if st.button(f"Delete", key=f"delete_{client.id}", type="secondary"):
                            st.session_state.delete_client_id = client.id
                            st.rerun()
                    
                    if show_all and client.notes:
                        st.write(f"**Notes:** {client.notes}")

elif action == "Add New Client":
    st.subheader("Add New Client")
    
    with st.form("add_client_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            name = st.text_input("Company Name *", help="Client's business name")
            contact_person = st.text_input("Contact Person", help="Primary contact at the company")
            email = st.text_input("Email Address", help="Primary email for invoices")
            phone = st.text_input("Phone Number", help="Irish format preferred")
            
        with col2:
            st.markdown("**Address Information**")
            address = st.text_area("Address", help="Street address")
            city = st.text_input("City")
            county = st.text_input("County")
            postal_code = st.text_input("Postal Code (Eircode)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Business Information**")
            vat_number = st.text_input("VAT Number", help="Client's VAT registration number")
            payment_terms = st.selectbox("Payment Terms", 
                                       ["30 days", "14 days", "7 days", "Due on receipt", "Net 30", "Net 60"])
            
        with col2:
            st.markdown("**Account Settings**")
            credit_limit = st.number_input("Credit Limit (EUR)", min_value=0.0, value=0.0, step=100.0)
            notes = st.text_area("Notes", help="Additional information about this client")
        
        submitted = st.form_submit_button("Add Client", use_container_width=True)
        
        if submitted:
            errors = []
            
            # Validate required fields
            if not name.strip():
                errors.append("Company name is required")
            
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
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create new client
                new_client = Client(
                    id="",  # Will be generated
                    name=name.strip(),
                    contact_person=contact_person.strip(),
                    email=email.strip(),
                    phone=phone.strip(),
                    address=address.strip(),
                    city=city.strip(),
                    county=county.strip(),
                    postal_code=postal_code.strip(),
                    vat_number=vat_number.strip(),
                    payment_terms=payment_terms,
                    credit_limit=credit_limit,
                    notes=notes.strip()
                )
                
                client_id = client_manager.add_client(new_client)
                st.success(f"✅ Client '{name}' added successfully!")
                st.rerun()

elif action == "Edit Client":
    if 'edit_client_id' not in st.session_state:
        st.info("Select a client to edit from the 'View Clients' section.")
    else:
        client_id = st.session_state.edit_client_id
        client = client_manager.get_client(client_id)
        
        if not client:
            st.error("Client not found.")
            if st.button("Back to Client List"):
                del st.session_state.edit_client_id
                st.rerun()
        else:
            st.subheader(f"Edit Client: {client.name}")
            
            with st.form("edit_client_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Basic Information**")
                    name = st.text_input("Company Name *", value=client.name)
                    contact_person = st.text_input("Contact Person", value=client.contact_person)
                    email = st.text_input("Email Address", value=client.email)
                    phone = st.text_input("Phone Number", value=client.phone)
                    
                with col2:
                    st.markdown("**Address Information**")
                    address = st.text_area("Address", value=client.address)
                    city = st.text_input("City", value=client.city)
                    county = st.text_input("County", value=client.county)
                    postal_code = st.text_input("Postal Code", value=client.postal_code)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Business Information**")
                    vat_number = st.text_input("VAT Number", value=client.vat_number)
                    payment_terms = st.selectbox("Payment Terms", 
                                               ["30 days", "14 days", "7 days", "Due on receipt", "Net 30", "Net 60"],
                                               index=["30 days", "14 days", "7 days", "Due on receipt", "Net 30", "Net 60"].index(client.payment_terms) if client.payment_terms in ["30 days", "14 days", "7 days", "Due on receipt", "Net 30", "Net 60"] else 0)
                    
                with col2:
                    st.markdown("**Account Settings**")
                    credit_limit = st.number_input("Credit Limit (EUR)", min_value=0.0, value=client.credit_limit, step=100.0)
                    notes = st.text_area("Notes", value=client.notes)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    submitted = st.form_submit_button("Update Client", use_container_width=True)
                
                with col2:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancelled:
                    del st.session_state.edit_client_id
                    st.rerun()
                
                if submitted:
                    errors = []
                    
                    # Validate required fields
                    if not name.strip():
                        errors.append("Company name is required")
                    
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
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Update client
                        updated_client = Client(
                            id=client_id,
                            name=name.strip(),
                            contact_person=contact_person.strip(),
                            email=email.strip(),
                            phone=phone.strip(),
                            address=address.strip(),
                            city=city.strip(),
                            county=county.strip(),
                            postal_code=postal_code.strip(),
                            vat_number=vat_number.strip(),
                            payment_terms=payment_terms,
                            credit_limit=credit_limit,
                            notes=notes.strip(),
                            created_date=client.created_date
                        )
                        
                        success = client_manager.update_client(client_id, updated_client)
                        if success:
                            st.success(f"✅ Client '{name}' updated successfully!")
                            del st.session_state.edit_client_id
                            st.rerun()
                        else:
                            st.error("Failed to update client.")

# Handle delete confirmation
if 'delete_client_id' in st.session_state:
    client_id = st.session_state.delete_client_id
    client = client_manager.get_client(client_id)
    
    if client:
        st.error(f"Are you sure you want to delete client '{client.name}'?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Delete", type="primary"):
                client_manager.delete_client(client_id)
                st.success(f"Client '{client.name}' deleted successfully!")
                del st.session_state.delete_client_id
                st.rerun()
        
        with col2:
            if st.button("Cancel"):
                del st.session_state.delete_client_id
                st.rerun()

# Statistics
st.markdown("---")
col1, col2, col3 = st.columns(3)

clients = client_manager.get_all_clients()

with col1:
    st.metric("Total Clients", len(clients))

with col2:
    vat_registered = len([c for c in clients if c.vat_number])
    st.metric("VAT Registered", vat_registered)

with col3:
    total_credit = sum(c.credit_limit for c in clients)
    st.metric("Total Credit Limits", Formatters.format_currency(total_credit))
