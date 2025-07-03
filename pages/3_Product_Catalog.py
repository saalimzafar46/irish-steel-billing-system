import streamlit as st
from models.product import Product, ProductManager
from utils.validators import Validators
from utils.formatters import Formatters
import pandas as pd

st.set_page_config(page_title="Product Catalog", page_icon="📦", layout="wide")

st.title("📦 Steel Product Catalog")
st.markdown("Manage your steel product inventory and pricing.")

# Initialize product manager
product_manager = ProductManager()

# Sidebar for actions
with st.sidebar:
    st.subheader("Actions")
    action = st.radio("Choose Action:", ["View Products", "Add New Product", "Edit Product"])

if action == "View Products":
    st.subheader("Product Catalog")
    
    products = product_manager.get_all_products()
    
    if not products:
        st.info("No products found. Add your first product using the sidebar.")
    else:
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search products...", placeholder="Search by name, grade, or category")
        with col2:
            category_filter = st.selectbox("Filter by Category", 
                                         ["All"] + list(set(p.category for p in products)))
        with col3:
            show_inactive = st.checkbox("Show inactive products")
        
        # Filter products
        filtered_products = products
        
        if search_term:
            filtered_products = [
                product for product in filtered_products
                if (search_term.lower() in product.name.lower() or
                    search_term.lower() in product.grade.lower() or
                    search_term.lower() in product.category.lower() or
                    search_term.lower() in product.description.lower())
            ]
        
        if category_filter != "All":
            filtered_products = [p for p in filtered_products if p.category == category_filter]
        
        if not show_inactive:
            filtered_products = [p for p in filtered_products if p.is_active]
        
        if not filtered_products:
            st.warning("No products match your search criteria.")
        else:
            # Display products in a table format
            product_data = []
            for product in filtered_products:
                product_data.append({
                    "Name": product.name,
                    "Category": product.category,
                    "Grade": product.grade,
                    "Dimensions": Formatters.format_dimensions(product.dimensions),
                    "Price": Formatters.format_currency(product.base_price),
                    "Stock": product.stock_quantity,
                    "Active": "✅" if product.is_active else "❌",
                    "Actions": product.id
                })
            
            df = pd.DataFrame(product_data)
            
            # Display interactive table
            for i, product in enumerate(filtered_products):
                with st.expander(f"**{product.name}** - {product.category} ({product.grade})", expanded=False):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {product.description}")
                        st.write(f"**Category:** {product.category}")
                        st.write(f"**Grade:** {product.grade}")
                        st.write(f"**Dimensions:** {Formatters.format_dimensions(product.dimensions)}")
                        st.write(f"**Finish:** {product.finish}")
                    
                    with col2:
                        st.write(f"**Base Price:** {Formatters.format_currency(product.base_price)}")
                        if product.cutting_charge > 0:
                            st.write(f"**Cutting Charge:** {Formatters.format_currency(product.cutting_charge)} per cut")
                        st.write(f"**Weight:** {product.weight_per_unit} kg per {product.unit_of_measure}")
                        st.write(f"**Stock:** {product.stock_quantity}")
                        st.write(f"**Min Order:** {product.min_order_quantity}")
                        st.write(f"**Status:** {'Active' if product.is_active else 'Inactive'}")
                    
                    with col3:
                        if st.button(f"Edit", key=f"edit_{product.id}"):
                            st.session_state.edit_product_id = product.id
                            st.rerun()
                        
                        if st.button(f"{'Deactivate' if product.is_active else 'Activate'}", 
                                   key=f"toggle_{product.id}"):
                            product.is_active = not product.is_active
                            product_manager.update_product(product.id, product)
                            st.rerun()
                        
                        if st.button(f"Delete", key=f"delete_{product.id}", type="secondary"):
                            st.session_state.delete_product_id = product.id
                            st.rerun()

elif action == "Add New Product":
    st.subheader("Add New Product")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            name = st.text_input("Product Name *", help="e.g., Steel Bar 20mm x 20mm")
            description = st.text_area("Description", help="Detailed product description")
            category = st.selectbox("Category", 
                                   ["Steel Bar", "Steel Plate", "Steel Beam", "Angle Iron", "Channel Steel", "Tube", "Other"])
            grade = st.text_input("Steel Grade", help="e.g., S355, S275, A36")
            finish = st.selectbox("Finish", 
                                ["Hot Rolled", "Cold Rolled", "Galvanized", "Painted", "Stainless", "Other"])
            
        with col2:
            st.markdown("**Specifications**")
            dimensions = st.text_input("Dimensions", help="e.g., 20mm x 20mm x 6000mm")
            weight_per_unit = st.number_input("Weight per Unit (kg)", min_value=0.0, step=0.1)
            unit_of_measure = st.selectbox("Unit of Measure", 
                                         ["length", "weight", "piece", "square meter", "cubic meter"])
            is_cuttable = st.checkbox("Can be cut to size", value=True)
            cutting_charge = st.number_input("Cutting Charge per Cut (EUR)", min_value=0.0, step=0.50,
                                           help="Cost for each cut if cuttable")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Pricing & Inventory**")
            base_price = st.number_input("Base Price (EUR)", min_value=0.0, step=0.01)
            stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1)
            
        with col2:
            st.markdown("**Order Settings**")
            min_order_quantity = st.number_input("Minimum Order Quantity", min_value=1, step=1, value=1)
            is_active = st.checkbox("Active Product", value=True, help="Inactive products won't appear in invoices")
        
        submitted = st.form_submit_button("Add Product", use_container_width=True)
        
        if submitted:
            errors = []
            
            # Validate required fields
            if not name.strip():
                errors.append("Product name is required")
            
            if base_price <= 0:
                errors.append("Base price must be greater than 0")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create new product
                new_product = Product(
                    id="",  # Will be generated
                    name=name.strip(),
                    description=description.strip(),
                    category=category,
                    grade=grade.strip(),
                    dimensions=dimensions.strip(),
                    weight_per_unit=weight_per_unit,
                    base_price=base_price,
                    cutting_charge=cutting_charge if is_cuttable else 0.0,
                    unit_of_measure=unit_of_measure,
                    finish=finish,
                    stock_quantity=stock_quantity,
                    min_order_quantity=min_order_quantity,
                    is_cuttable=is_cuttable,
                    is_active=is_active
                )
                
                product_id = product_manager.add_product(new_product)
                st.success(f"✅ Product '{name}' added successfully!")
                st.rerun()

elif action == "Edit Product":
    if 'edit_product_id' not in st.session_state:
        st.info("Select a product to edit from the 'View Products' section.")
    else:
        product_id = st.session_state.edit_product_id
        product = product_manager.get_product(product_id)
        
        if not product:
            st.error("Product not found.")
            if st.button("Back to Product List"):
                del st.session_state.edit_product_id
                st.rerun()
        else:
            st.subheader(f"Edit Product: {product.name}")
            
            with st.form("edit_product_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Basic Information**")
                    name = st.text_input("Product Name *", value=product.name)
                    description = st.text_area("Description", value=product.description)
                    category = st.selectbox("Category", 
                                           ["Steel Bar", "Steel Plate", "Steel Beam", "Angle Iron", "Channel Steel", "Tube", "Other"],
                                           index=["Steel Bar", "Steel Plate", "Steel Beam", "Angle Iron", "Channel Steel", "Tube", "Other"].index(product.category) if product.category in ["Steel Bar", "Steel Plate", "Steel Beam", "Angle Iron", "Channel Steel", "Tube", "Other"] else 0)
                    grade = st.text_input("Steel Grade", value=product.grade)
                    finish = st.selectbox("Finish", 
                                        ["Hot Rolled", "Cold Rolled", "Galvanized", "Painted", "Stainless", "Other"],
                                        index=["Hot Rolled", "Cold Rolled", "Galvanized", "Painted", "Stainless", "Other"].index(product.finish) if product.finish in ["Hot Rolled", "Cold Rolled", "Galvanized", "Painted", "Stainless", "Other"] else 0)
                    
                with col2:
                    st.markdown("**Specifications**")
                    dimensions = st.text_input("Dimensions", value=product.dimensions)
                    weight_per_unit = st.number_input("Weight per Unit (kg)", min_value=0.0, step=0.1, value=product.weight_per_unit)
                    unit_of_measure = st.selectbox("Unit of Measure", 
                                                 ["length", "weight", "piece", "square meter", "cubic meter"],
                                                 index=["length", "weight", "piece", "square meter", "cubic meter"].index(product.unit_of_measure) if product.unit_of_measure in ["length", "weight", "piece", "square meter", "cubic meter"] else 0)
                    is_cuttable = st.checkbox("Can be cut to size", value=product.is_cuttable)
                    cutting_charge = st.number_input("Cutting Charge per Cut (EUR)", min_value=0.0, step=0.50, value=product.cutting_charge)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Pricing & Inventory**")
                    base_price = st.number_input("Base Price (EUR)", min_value=0.0, step=0.01, value=product.base_price)
                    stock_quantity = st.number_input("Stock Quantity", min_value=0, step=1, value=product.stock_quantity)
                    
                with col2:
                    st.markdown("**Order Settings**")
                    min_order_quantity = st.number_input("Minimum Order Quantity", min_value=1, step=1, value=product.min_order_quantity)
                    is_active = st.checkbox("Active Product", value=product.is_active)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    submitted = st.form_submit_button("Update Product", use_container_width=True)
                
                with col2:
                    cancelled = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancelled:
                    del st.session_state.edit_product_id
                    st.rerun()
                
                if submitted:
                    errors = []
                    
                    # Validate required fields
                    if not name.strip():
                        errors.append("Product name is required")
                    
                    if base_price <= 0:
                        errors.append("Base price must be greater than 0")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Update product
                        updated_product = Product(
                            id=product_id,
                            name=name.strip(),
                            description=description.strip(),
                            category=category,
                            grade=grade.strip(),
                            dimensions=dimensions.strip(),
                            weight_per_unit=weight_per_unit,
                            base_price=base_price,
                            cutting_charge=cutting_charge if is_cuttable else 0.0,
                            unit_of_measure=unit_of_measure,
                            finish=finish,
                            stock_quantity=stock_quantity,
                            min_order_quantity=min_order_quantity,
                            is_cuttable=is_cuttable,
                            is_active=is_active
                        )
                        
                        success = product_manager.update_product(product_id, updated_product)
                        if success:
                            st.success(f"✅ Product '{name}' updated successfully!")
                            del st.session_state.edit_product_id
                            st.rerun()
                        else:
                            st.error("Failed to update product.")

# Handle delete confirmation
if 'delete_product_id' in st.session_state:
    product_id = st.session_state.delete_product_id
    product = product_manager.get_product(product_id)
    
    if product:
        st.error(f"Are you sure you want to delete product '{product.name}'?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Delete", type="primary"):
                product_manager.delete_product(product_id)
                st.success(f"Product '{product.name}' deleted successfully!")
                del st.session_state.delete_product_id
                st.rerun()
        
        with col2:
            if st.button("Cancel"):
                del st.session_state.delete_product_id
                st.rerun()

# Statistics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

products = product_manager.get_all_products()
active_products = [p for p in products if p.is_active]

with col1:
    st.metric("Total Products", len(products))

with col2:
    st.metric("Active Products", len(active_products))

with col3:
    total_stock_value = sum(p.base_price * p.stock_quantity for p in active_products)
    st.metric("Stock Value", Formatters.format_currency(total_stock_value))

with col4:
    categories = len(set(p.category for p in products))
    st.metric("Categories", categories)

# Quick add frequently used products
with st.expander("💡 Quick Add Common Steel Products"):
    st.markdown("""
    Common steel products you might want to add:
    
    **Steel Bars:**
    - Round bars: 10mm, 12mm, 16mm, 20mm, 25mm diameter
    - Square bars: 20x20mm, 25x25mm, 30x30mm
    - Flat bars: 20x3mm, 25x5mm, 40x5mm
    
    **Angle Iron:**
    - Equal angles: 25x25x3mm, 40x40x4mm, 50x50x5mm
    - Unequal angles: 40x25x4mm, 50x30x5mm
    
    **Standard Grades:**
    - S275 (equivalent to old Fe430)
    - S355 (equivalent to old Fe510)
    - S235 (mild steel)
    """)
