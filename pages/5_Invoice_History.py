import streamlit as st
from models.invoice import InvoiceManager
from models.client import ClientManager
from models.company import Company
from services.pdf_generator import PDFGenerator
from utils.formatters import Formatters
import pandas as pd
from datetime import datetime, timedelta
import base64

st.set_page_config(page_title="Invoice History", page_icon="📋", layout="wide")

st.title("📋 Invoice History")
st.markdown("View and manage all your invoices.")

# Initialize managers
invoice_manager = InvoiceManager()
client_manager = ClientManager()
company = Company.load()

# Get all invoices
invoices = invoice_manager.get_all_invoices()

if not invoices:
    st.info("No invoices found. Create your first invoice!")
    if st.button("➕ Create Invoice"):
        st.switch_page("pages/4_Create_Invoice.py")
else:
    # Filters and search
    st.subheader("Filter & Search")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Invoice number, client...")
    
    with col2:
        status_filter = st.selectbox("Status", 
                                   ["All", "Draft", "Sent", "Paid", "Overdue", "Cancelled"])
    
    with col3:
        # Date range filter
        date_filter = st.selectbox("Date Range", 
                                 ["All Time", "Last 30 Days", "Last 90 Days", "This Year", "Custom"])
    
    with col4:
        if date_filter == "Custom":
            date_from = st.date_input("From Date")
            date_to = st.date_input("To Date")
    
    # Apply filters
    filtered_invoices = invoices
    
    # Search filter
    if search_term:
        filtered_invoices = [
            inv for inv in filtered_invoices
            if (search_term.lower() in inv.invoice_number.lower() or
                search_term.lower() in inv.client_name.lower())
        ]
    
    # Status filter
    if status_filter != "All":
        filtered_invoices = [inv for inv in filtered_invoices if inv.status == status_filter]
    
    # Date filter
    if date_filter != "All Time":
        today = datetime.now().date()
        
        if date_filter == "Last 30 Days":
            cutoff_date = today - timedelta(days=30)
        elif date_filter == "Last 90 Days":
            cutoff_date = today - timedelta(days=90)
        elif date_filter == "This Year":
            cutoff_date = datetime(today.year, 1, 1).date()
        elif date_filter == "Custom":
            cutoff_date = date_from
        
        filtered_invoices = [
            inv for inv in filtered_invoices
            if datetime.strptime(inv.issue_date, "%Y-%m-%d").date() >= cutoff_date
        ]
        
        if date_filter == "Custom":
            filtered_invoices = [
                inv for inv in filtered_invoices
                if datetime.strptime(inv.issue_date, "%Y-%m-%d").date() <= date_to
            ]
    
    # Summary statistics
    st.markdown("---")
    st.subheader("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_amount = sum(inv.total_amount for inv in filtered_invoices)
    paid_amount = sum(inv.total_amount for inv in filtered_invoices if inv.status == "Paid")
    outstanding_amount = sum(inv.total_amount for inv in filtered_invoices if inv.status in ["Sent", "Overdue"])
    
    with col1:
        st.metric("Total Invoices", len(filtered_invoices))
    
    with col2:
        st.metric("Total Value", Formatters.format_currency(total_amount))
    
    with col3:
        st.metric("Paid", Formatters.format_currency(paid_amount))
    
    with col4:
        st.metric("Outstanding", Formatters.format_currency(outstanding_amount))
    
    # Invoice list
    st.markdown("---")
    st.subheader(f"Invoices ({len(filtered_invoices)})")
    
    if not filtered_invoices:
        st.warning("No invoices match your filter criteria.")
    else:
        # Sort options
        col1, col2 = st.columns([1, 1])
        with col1:
            sort_by = st.selectbox("Sort by", ["Date (Newest First)", "Date (Oldest First)", 
                                              "Amount (High to Low)", "Amount (Low to High)",
                                              "Status", "Client Name"])
        
        # Apply sorting
        if sort_by == "Date (Newest First)":
            filtered_invoices.sort(key=lambda x: x.issue_date, reverse=True)
        elif sort_by == "Date (Oldest First)":
            filtered_invoices.sort(key=lambda x: x.issue_date)
        elif sort_by == "Amount (High to Low)":
            filtered_invoices.sort(key=lambda x: x.total_amount, reverse=True)
        elif sort_by == "Amount (Low to High)":
            filtered_invoices.sort(key=lambda x: x.total_amount)
        elif sort_by == "Status":
            filtered_invoices.sort(key=lambda x: x.status)
        elif sort_by == "Client Name":
            filtered_invoices.sort(key=lambda x: x.client_name)
        
        # Display invoices
        for invoice in filtered_invoices:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
                
                with col1:
                    st.write(f"**{invoice.invoice_number}**")
                    st.caption(f"Created: {Formatters.format_date(invoice.created_date)}")
                
                with col2:
                    st.write(f"**{invoice.client_name}**")
                    st.caption(f"Due: {invoice.due_date}")
                
                with col3:
                    # Status badge
                    status_colors = {
                        "Draft": "🔘",
                        "Sent": "📤",
                        "Paid": "✅",
                        "Overdue": "🔴",
                        "Cancelled": "❌"
                    }
                    st.write(f"{status_colors.get(invoice.status, '❓')} {invoice.status}")
                
                with col4:
                    st.write(f"**{Formatters.format_currency(invoice.total_amount)}**")
                    st.caption(f"{len(invoice.items)} items")
                
                with col5:
                    # Action buttons
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("📄", key=f"pdf_{invoice.id}", help="Generate PDF"):
                            # Generate PDF
                            try:
                                pdf_generator = PDFGenerator()
                                client = client_manager.get_client(invoice.client_id)
                                if client:
                                    pdf_buffer = pdf_generator.generate_invoice_pdf(invoice, company, client)
                                    pdf_data = pdf_buffer.getvalue()
                                    b64_pdf = base64.b64encode(pdf_data).decode()
                                    
                                    filename = f"Invoice_{invoice.invoice_number}_{invoice.client_name.replace(' ', '_')}.pdf"
                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">Download PDF</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                                else:
                                    st.error("Client not found")
                            except Exception as e:
                                st.error(f"Error generating PDF: {str(e)}")
                    
                    with col_b:
                        if st.button("📝", key=f"edit_{invoice.id}", help="Edit Invoice"):
                            st.session_state.current_invoice = invoice
                            st.switch_page("pages/4_Create_Invoice.py")
                    
                    with col_c:
                        if st.button("🗑️", key=f"delete_{invoice.id}", help="Delete Invoice"):
                            st.session_state.delete_invoice_id = invoice.id
                            st.rerun()
                
                # Invoice details expander
                with st.expander(f"View Details - {invoice.invoice_number}"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Invoice Information:**")
                        st.write(f"Number: {invoice.invoice_number}")
                        st.write(f"Issue Date: {invoice.issue_date}")
                        st.write(f"Due Date: {invoice.due_date}")
                        st.write(f"Status: {invoice.status}")
                        st.write(f"Payment Terms: {invoice.payment_terms}")
                        
                        if invoice.notes:
                            st.write(f"Notes: {invoice.notes}")
                    
                    with detail_col2:
                        st.markdown("**Financial Summary:**")
                        st.write(f"Subtotal: {Formatters.format_currency(invoice.subtotal)}")
                        if invoice.additional_charges_total > 0:
                            st.write(f"Additional Charges: {Formatters.format_currency(invoice.additional_charges_total)}")
                        if invoice.global_discount_total > 0:
                            st.write(f"Discounts: -{Formatters.format_currency(invoice.global_discount_total)}")
                        st.write(f"VAT ({invoice.vat_rate}%): {Formatters.format_currency(invoice.vat_amount)}")
                        st.write(f"**Total: {Formatters.format_currency(invoice.total_amount)}**")
                    
                    # Items table
                    if invoice.items:
                        st.markdown("**Items:**")
                        items_data = []
                        for item in invoice.items:
                            items_data.append({
                                "Product": item.product_name,
                                "Quantity": item.quantity,
                                "Unit Price": Formatters.format_currency(item.unit_price),
                                "Total": Formatters.format_currency(item.line_total)
                            })
                        
                        items_df = pd.DataFrame(items_data)
                        st.dataframe(items_df, use_container_width=True)
                
                st.markdown("---")

# Handle delete confirmation
if 'delete_invoice_id' in st.session_state:
    invoice_id = st.session_state.delete_invoice_id
    invoice = invoice_manager.get_invoice(invoice_id)
    
    if invoice:
        st.error(f"Are you sure you want to delete invoice '{invoice.invoice_number}'?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Delete", type="primary"):
                invoice_manager.delete_invoice(invoice_id)
                st.success(f"Invoice '{invoice.invoice_number}' deleted successfully!")
                del st.session_state.delete_invoice_id
                st.rerun()
        
        with col2:
            if st.button("Cancel"):
                del st.session_state.delete_invoice_id
                st.rerun()

# Bulk actions
if filtered_invoices:
    st.markdown("---")
    st.subheader("Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to CSV"):
            # Create CSV data
            csv_data = []
            for invoice in filtered_invoices:
                csv_data.append({
                    "Invoice Number": invoice.invoice_number,
                    "Client": invoice.client_name,
                    "Issue Date": invoice.issue_date,
                    "Due Date": invoice.due_date,
                    "Status": invoice.status,
                    "Subtotal": invoice.subtotal,
                    "VAT": invoice.vat_amount,
                    "Total": invoice.total_amount,
                    "Items Count": len(invoice.items)
                })
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False)
            
            # Create download link
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="invoices_export.csv">📊 Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with col2:
        st.info("More bulk actions coming soon...")
    
    with col3:
        st.info("Batch PDF generation coming soon...")
