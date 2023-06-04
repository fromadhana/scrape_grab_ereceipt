Certainly! Here's an updated version of the README file with the added disclaimer:

# Grab E-Receipt Dashboard

This repository contains a Python script that retrieves and analyzes Grab Bike and Grab Food e-receipts from a Gmail account. It provides a Streamlit dashboard for visualizing transaction data and generating insights.

**Disclaimer: This project is for educational purposes only. The script and dashboard are intended to showcase data retrieval, processing, and visualization techniques. The subject and content of the e-receipts used in this project might differ from actual Grab e-receipts.**

## Features

- Fetches Grab Bike and Grab Food e-receipts from a Gmail account using IMAP protocol.
- Extracts relevant information from the HTML email bodies, such as transaction amounts.
- Converts the transaction dates to the UTC+7 timezone.
- Performs data processing and aggregation to calculate total amounts and averages.
- Generates a dynamic Streamlit dashboard to display a transactions table and line chart.
- Allows filtering of transactions based on a date range.
- Presents key metrics, including total amounts and averages for Grab Bike, Grab Food, and the combined total.
- Utilizes Plotly Express library for interactive data visualization.

## Requirements

- Python 3.x
- Required libraries: `re`, `pytz`, `numpy`, `pandas`, `streamlit`, `plotly`, `beautifulsoup4`
- Gmail account with IMAP access enabled

## Usage

1. Install the required libraries: `pip install -r requirements.txt`.
2. Set up your Gmail account credentials by creating a `secrets.toml` file and providing your email and password in the following format:

```
[gmail_account]
gmail = "your_email@gmail.com"
pass = "your_password"
```

3. Run the script: `streamlit run grab_ereceipt.py`.
4. Access the Streamlit dashboard in your web browser.
5. Enter the desired start and end dates for filtering the transactions.
6. Explore the transactions table, key metrics, and line chart.


## Acknowledgements

- The script utilizes the [IMAPClient](https://imapclient.readthedocs.io/) library for accessing the Gmail account.
- Parsing of HTML email bodies is performed using the [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library.
- Data visualization is powered by the [Plotly Express](https://plotly.com/python/plotly-express/) library.
- Streamlit is used to create the interactive dashboard.

## Contributing

Contributions to the project are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

Please ensure that your contributions align with the project's coding style and conventions.

## Contact

For any inquiries or questions, please contact [f.romadhana@gmail.com](mailto:f.romadhana@gmail.com).

Enjoy analyzing your Grab Bike and Grab Food transactions with the Grab E-Receipt Dashboard!