import streamlit as st
from models.invoice import Invoice, InvoiceItem, InvoiceManager
from models.client import ClientManager
from models.product import ProductManager
from models.company import Company
from services.pdf_generator import PDFGenerator
from utils.formatters import Formatters
from datetime import datetime, timedelta
import base64

st.set_page_config(page_title="Create Invoice", page_icon="📄", layout="wide")

st.title("📄 Create Invoice")
st.markdown("Generate professional invoices for your steel products.")

# Initialize managers
invoice_manager = InvoiceManager()
client_manager = ClientManager()
product_manager = ProductManager()
company = Company.load()

# Check if company is configured
if not company.name:
    st.error("Please configure your company information first.")
    if st.button("Go to Company Setup"):
        st.switch_page("pages/1_Company_Setup.py")
    st.stop()

# Get clients and products
clients = client_manager.get_all_clients()
products = product_manager.get_active_products()

if not clients:
    st.error("No clients found. Please add clients first.")
    if st.button("Go to Client Management"):
        st.switch_page("pages/2_Client_Management.py")
    st.stop()

if not products:
    st.error("No active products found. Please add products first.")
    if st.button("Go to Product Catalog"):
        st.switch_page("pages/3_Product_Catalog.py")
    st.stop()

# Initialize invoice in session state
if 'current_invoice' not in st.session_state:
    st.session_state.current_invoice = Invoice()

invoice = st.session_state.current_invoice

# Ensure invoice is not None
if invoice is None:
    st.session_state.current_invoice = Invoice()
    invoice = st.session_state.current_invoice



# Invoice Header Section
st.subheader("Invoice Details")

col1, col2, col3 = st.columns(3)

with col1:
    # Client selection
    client_options = {
        f"{client.name} - {client.city}": client
        for client in clients
    }
    selected_client_key = st.selectbox("Select Client *",
                                       options=list(client_options.keys()))

# Initialize selected_client variable outside the column context
selected_client = None
if selected_client_key:
    selected_client = client_options[selected_client_key]
    invoice.client_id = selected_client.id
    invoice.client_name = selected_client.name
    invoice.payment_terms = selected_client.payment_terms

with col2:
    # Invoice dates
    issue_date = st.date_input("Issue Date",
                               value=datetime.strptime(invoice.issue_date,
                                                       "%Y-%m-%d"))
    invoice.issue_date = issue_date.strftime("%Y-%m-%d")

    # Calculate due date based on payment terms
    if invoice.payment_terms:
        try:
            days = int(invoice.payment_terms.split()[0])
            due_date_default = issue_date + timedelta(days=days)
        except:
            due_date_default = issue_date + timedelta(days=30)
    else:
        due_date_default = issue_date + timedelta(days=30)

    due_date = st.date_input("Due Date", value=due_date_default)
    invoice.due_date = due_date.strftime("%Y-%m-%d")

with col3:
    # Invoice status and number
    invoice.status = st.selectbox(
        "Status", ["Draft", "Sent", "Paid", "Overdue", "Cancelled"],
        index=["Draft", "Sent", "Paid", "Overdue",
               "Cancelled"].index(invoice.status))

    # Auto-generate invoice number if empty
    if not invoice.invoice_number:
        invoice.invoice_number = invoice_manager.generate_invoice_number()

    invoice_number = st.text_input("Invoice Number",
                                   value=invoice.invoice_number)
    invoice.invoice_number = invoice_number

# Invoice Items Section
st.markdown("---")
st.subheader("Invoice Items")

# Add item form
with st.expander("➕ Add Item", expanded=len(invoice.items) == 0):
    with st.form("add_item_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Product selection
            product_options = {
                f"{product.name} - {product.category}": product
                for product in products
            }
            selected_product_key = st.selectbox("Select Product",
                                                options=list(
                                                    product_options.keys()))

        # Initialize selected_product outside the column context
        selected_product = None
        if selected_product_key:
            selected_product = product_options[selected_product_key]

            # Show product details
            st.info(
                f"**Price:** {Formatters.format_currency(selected_product.base_price)} | "
                f"**Stock:** {selected_product.stock_quantity} | "
                f"**Grade:** {selected_product.grade}")

        with col1:
            quantity = st.number_input("Quantity",
                                       min_value=0.1,
                                       step=0.1,
                                       value=1.0)
            unit_price = st.number_input("Unit Price (EUR)",
                                         min_value=0.0,
                                         step=0.01,
                                         value=selected_product.base_price
                                         if selected_product else 0.0)

        with col2:
            # Cutting and discounts
            cuts_required = 0
            cutting_charge_per_cut = 0.0

            if selected_product and selected_product.is_cuttable:
                cuts_required = st.number_input("Cuts Required",
                                                min_value=0,
                                                step=1,
                                                value=0)
                cutting_charge_per_cut = st.number_input(
                    "Cutting Charge per Cut (EUR)",
                    min_value=0.0,
                    step=0.01,
                    value=selected_product.cutting_charge)

            # Discounts
            discount_percentage = st.number_input("Discount (%)",
                                                  min_value=0.0,
                                                  max_value=100.0,
                                                  step=0.1,
                                                  value=0.0)
            discount_amount = st.number_input("Fixed Discount (EUR)",
                                              min_value=0.0,
                                              step=0.01,
                                              value=0.0)

        # Item description
        item_description = st.text_area(
            "Item Description (optional)",
            value=selected_product.description if selected_product is not None else "")

        add_item = st.form_submit_button("Add Item", use_container_width=True)

        if add_item and selected_product:
            new_item = InvoiceItem(
                product_id=selected_product.id,
                product_name=selected_product.name,
                description=item_description,
                quantity=quantity,
                unit_price=unit_price,
                cuts_required=cuts_required,
                cutting_charge_per_cut=cutting_charge_per_cut,
                discount_percentage=discount_percentage,
                discount_amount=discount_amount)

            invoice.add_item(new_item)
            st.rerun()

# Display current items
if invoice.items:
    st.markdown("### Current Items")

    for i, item in enumerate(invoice.items):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

            with col1:
                st.write(f"**{item.product_name}**")
                if item.description:
                    st.caption(item.description)

            with col2:
                st.write(f"Qty: {item.quantity}")
                if item.cuts_required > 0:
                    st.caption(f"Cuts: {item.cuts_required}")

            with col3:
                st.write(f"{Formatters.format_currency(item.unit_price)}")
                if item.cutting_charge_per_cut > 0:
                    st.caption(
                        f"Cut: {Formatters.format_currency(item.cutting_charge_per_cut)}"
                    )

            with col4:
                if item.discount_percentage > 0 or item.discount_amount > 0:
                    st.write(
                        f"-{Formatters.format_currency(item.total_discount)}")
                else:
                    st.write("-")

            with col5:
                st.write(f"**{Formatters.format_currency(item.line_total)}**")
                if st.button("🗑️", key=f"remove_{i}", help="Remove item"):
                    invoice.remove_item(i)
                    st.rerun()

            st.markdown("---")

# Additional Charges and Discounts
st.subheader("Additional Charges & Discounts")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Additional Charges**")
    invoice.shipping_cost = st.number_input("Shipping Cost (EUR)",
                                            min_value=0.0,
                                            step=0.01,
                                            value=invoice.shipping_cost)
    invoice.handling_cost = st.number_input("Handling Cost (EUR)",
                                            min_value=0.0,
                                            step=0.01,
                                            value=invoice.handling_cost)
    invoice.other_charges = st.number_input("Other Charges (EUR)",
                                            min_value=0.0,
                                            step=0.01,
                                            value=invoice.other_charges)
    if invoice.other_charges > 0:
        invoice.other_charges_description = st.text_input(
            "Other Charges Description",
            value=invoice.other_charges_description,
            placeholder="e.g., Special handling fee")

with col2:
    st.markdown("**Global Discounts**")
    invoice.global_discount_percentage = st.number_input(
        "Global Discount (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        value=invoice.global_discount_percentage)
    invoice.global_discount_amount = st.number_input(
        "Fixed Global Discount (EUR)",
        min_value=0.0,
        step=0.01,
        value=invoice.global_discount_amount)

    st.markdown("**Tax Settings**")
    invoice.vat_rate = st.number_input("VAT Rate (%)",
                                       min_value=0.0,
                                       max_value=50.0,
                                       step=0.1,
                                       value=invoice.vat_rate)

# Notes and Terms
invoice.notes = st.text_area(
    "Invoice Notes",
    value=invoice.notes,
    placeholder="Additional notes or payment instructions...")

# Invoice Summary
st.markdown("---")
st.subheader("Invoice Summary")

col1, col2 = st.columns([1, 1])

with col2:
    # Calculate and display totals
    summary_data = [
        ("Subtotal:", Formatters.format_currency(invoice.subtotal)),
    ]

    if invoice.additional_charges_total > 0:
        if invoice.shipping_cost > 0:
            summary_data.append(
                ("Shipping:",
                 Formatters.format_currency(invoice.shipping_cost)))
        if invoice.handling_cost > 0:
            summary_data.append(
                ("Handling:",
                 Formatters.format_currency(invoice.handling_cost)))
        if invoice.other_charges > 0:
            desc = invoice.other_charges_description or "Other Charges"
            summary_data.append(
                (f"{desc}:",
                 Formatters.format_currency(invoice.other_charges)))

    if invoice.global_discount_total > 0:
        summary_data.append(
            ("Global Discount:",
             f"-{Formatters.format_currency(invoice.global_discount_total)}"))

    summary_data.extend([
        ("Total Before VAT:",
         Formatters.format_currency(invoice.total_before_vat)),
        (f"VAT ({invoice.vat_rate}%):",
         Formatters.format_currency(invoice.vat_amount)),
        ("**TOTAL AMOUNT:**",
         f"**{Formatters.format_currency(invoice.total_amount)}**")
    ])

    for label, value in summary_data:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.write(label)
        with col_b:
            st.write(value)

# Action buttons
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💾 Save Invoice", use_container_width=True):
        if not invoice.items:
            st.error("Cannot save invoice without items.")
        else:
            invoice_id = invoice_manager.add_invoice(invoice)
            st.success(
                f"✅ Invoice {invoice.invoice_number} saved successfully!")
            # Reset current invoice
            st.session_state.current_invoice = Invoice()
            st.rerun()

with col2:
    if st.button("📄 Generate PDF", use_container_width=True):
        if not invoice.items:
            st.error("Cannot generate PDF without items.")
        elif not selected_client_key:
            st.error("Please select a client.")
        else:
            try:
                pdf_generator = PDFGenerator()
                selected_client = client_options[selected_client_key]
                pdf_buffer = pdf_generator.generate_invoice_pdf(
                    invoice, company, selected_client)

                # Encode PDF for download
                pdf_data = pdf_buffer.getvalue()
                b64_pdf = base64.b64encode(pdf_data).decode()

                # Create download link
                filename = f"Invoice_{invoice.invoice_number}_{selected_client.name.replace(' ', '_')}.pdf"
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">📄 Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

                st.success(
                    "✅ PDF generated successfully! Click the link above to download."
                )

            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

with col3:
    if st.button("🔄 Clear Invoice", use_container_width=True):
        st.session_state.current_invoice = Invoice()
        st.rerun()

with col4:
    if st.button("📋 View All Invoices", use_container_width=True):
        st.switch_page("pages/5_Invoice_History.py")

# Display current invoice preview
if invoice.items:
    with st.expander("📋 Invoice Preview"):
        st.markdown(f"**Invoice:** {invoice.invoice_number}")
        st.markdown(f"**Client:** {invoice.client_name}")
        st.markdown(
            f"**Date:** {invoice.issue_date} | **Due:** {invoice.due_date}")
        st.markdown(
            f"**Items:** {len(invoice.items)} | **Total:** {Formatters.format_currency(invoice.total_amount)}"
        )
