# Irish Steel Billing System

A comprehensive web-based billing application designed specifically for Irish steel suppliers. Built with Streamlit and featuring professional PDF invoice generation.

## Features

- **Company Setup**: Configure your business information with Irish-specific validation
- **Client Management**: Full CRUD operations for customer database
- **Product Catalog**: Manage steel products with specifications, grades, and cutting charges
- **Invoice Creation**: Professional invoice generation with automatic calculations
- **PDF Generation**: High-quality PDF invoices with company branding
- **Invoice History**: Track and manage all billing history with filtering and search
- **Irish Compliance**: VAT handling, phone/address validation, and Eircode support

## Installation Options

### Option 1: Download Pre-built EXE (Recommended)
1. Go to the [Releases](https://github.com/yourusername/irish-steel-billing/releases) page
2. Download the latest `IrishSteelBilling.exe` file
3. Run the EXE file - it will automatically:
   - Start the application server
   - Open your browser to the application
   - No installation required!

### Option 2: Run from Source
1. Clone or download this repository
2. Install Python 3.11 or higher
3. Install required dependencies:

```bash
pip install -r requirements_standalone.txt
```

4. Start the application:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Automatic EXE Building

This repository is configured with GitHub Actions to automatically build Windows executables. Every time you push code to the main branch:

1. GitHub Actions installs all dependencies
2. Builds a standalone EXE file using PyInstaller
3. Creates a new release with the downloadable EXE
4. No local setup required!

## Configuration

For production deployment, you may want to modify the `.streamlit/config.toml` file:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
```

## Project Structure

```
├── app.py                    # Main application entry point
├── models/                   # Data models
│   ├── company.py           # Company information model
│   ├── client.py            # Client management model
│   ├── product.py           # Product catalog model
│   └── invoice.py           # Invoice and invoice items model
├── pages/                    # Streamlit pages
│   ├── 1_Company_Setup.py   # Company configuration
│   ├── 2_Client_Management.py # Client CRUD operations
│   ├── 3_Product_Catalog.py # Product management
│   ├── 4_Create_Invoice.py  # Invoice creation
│   └── 5_Invoice_History.py # Invoice tracking
├── services/                 # Business logic services
│   ├── data_manager.py      # Data backup and export
│   └── pdf_generator.py     # PDF invoice generation
├── utils/                    # Utility functions
│   ├── formatters.py        # Data formatting utilities
│   └── validators.py        # Irish-specific validation
├── data/                     # JSON data storage
└── .streamlit/              # Streamlit configuration
```

## Data Storage

The application uses JSON files for data persistence:
- `data/company.json` - Company information
- `data/clients.json` - Client database
- `data/products.json` - Product catalog
- `data/invoices.json` - Invoice history

## Irish Business Features

- **VAT Number Validation**: Irish VAT format (IE1234567T)
- **Phone Number Formatting**: Irish landline and mobile formats
- **Address Validation**: Eircode postal code support
- **Currency**: Euro (EUR) formatting
- **Tax Compliance**: 23% VAT rate (configurable)

## Getting Started

1. **Company Setup**: Configure your business details
2. **Add Clients**: Build your customer database
3. **Add Products**: Set up your steel product catalog
4. **Create Invoices**: Generate professional invoices
5. **Export PDFs**: Download invoices for sending to clients

## Dependencies

- **Streamlit**: Web application framework
- **ReportLab**: PDF generation
- **Pandas**: Data manipulation

## License

This project is open source and available under the MIT License.

## Support

For support or questions about this application, please refer to the documentation or create an issue in the repository.