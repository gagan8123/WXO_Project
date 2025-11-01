

# Invoice Automation using IBM Watsonx Orchestrate and Odoo ERP

## Overview
This project demonstrates an intelligent automation solution that connects **IBM Watsonx Orchestrate** with **Odoo ERP** using a **Flask** backend.  
The main objective is to automate the process of **invoice extraction**, **validation with purchase orders**, and **invoice creation** in Odoo — reducing manual effort and improving operational accuracy.

The solution leverages **agentic AI** capabilities of IBM Watsonx Orchestrate to interact with the Flask application through defined APIs (specified in `tools.yaml`).  
This integration allows the Watsonx Orchestrate agent to autonomously process invoices, validate them with existing POs, and upload them directly into Odoo ERP.

---

## How It Works

1. **Flask Application (app.py):**  
   Hosts API endpoints that communicate between Watsonx Orchestrate and Odoo ERP.  
   The app is hosted using **Ngrok**, making it accessible securely from Watsonx Orchestrate.

2. **OdooFunctions.py:**  
   Handles all backend operations such as:
   - Fetching and validating purchase orders
   - Extracting and processing invoice data
   - Creating invoices in Odoo once validation succeeds

3. **tools.yaml:**  
   Defines the tools and endpoints used by **Watsonx Orchestrate** to interact with the Flask app.  
   It enables the orchestrate agent to know which functions to call and how to execute them in sequence.

---

## Workflow

1. The user interacts with **Watsonx Orchestrate** using a conversational command (e.g., “Validate and upload this invoice”).
2. Orchestrate calls the relevant API from the Flask application (hosted via Ngrok).
3. The Flask backend extracts invoice data and validates it against Odoo purchase orders using the logic in `OdooFunctions.py`.
4. If the validation passes, an invoice is automatically created in **Odoo ERP**.
5. The Orchestrate agent provides real-time feedback on success, errors, or mismatches to the user.

---

## Key Features

- **End-to-End Automation:** From invoice extraction to posting in Odoo.
- **Agentic AI Integration:** Uses IBM Watsonx Orchestrate’s intelligent agent to reason and decide workflow steps.
- **Modular Design:** Flask handles API logic, OdooFunctions manages ERP operations, and YAML provides integration mapping.
- **Scalable and Adaptable:** Can be extended to handle other ERP modules or document types.

---

## Prerequisites

- Python 3.9 or above  
- Flask  
- Ngrok (for exposing the Flask app)  
- Access to an Odoo ERP instance  
- IBM Watsonx Orchestrate account  

---

## Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/gagan8123/WXO_Project.git
   cd WXO_Project



Install dependencies: <br>
`pip install flask requests`


Start the Flask application:<br>
`python app.py`


Expose it with Ngrok:<br>
`ngrok http 5000`

Update the `tools.yaml` file with your Ngrok URL and connect it with Watsonx Orchestrate.



Example Use Case


- A finance team member uploads an invoice file in Watsonx Orchestrate.


- The Orchestrate agent triggers the Flask endpoint to extract and validate data.


- After successful validation with the purchase order, the invoice is automatically created in Odoo.


- The user receives a confirmation message from Orchestrate.



Future Enhancements


- Add multi-document batch processing

- Integrate approval workflows

- Enhance exception handling with LLM-based reasoning

- Implement audit logging and reporting dashboard



