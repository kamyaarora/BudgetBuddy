import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import random
import json
import streamlit.components.v1 as components


# Configure the Streamlit page with updated theme
def configure_page():
    st.set_page_config(
        page_title="BudgetBuddy - Your Property Buying Companion",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    set_custom_theme()


# Initialize session state variables if they don't exist
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': '',
        'budget': 0,
        'location': '',
        'income': 0,
        'loans': 0,
        'credit_score': 0,
        'dti_ratio': 0,
        'savings': 0,
        'monthly_expenses': 0
    }
if 'roundup_savings' not in st.session_state:
    st.session_state.roundup_savings = {
        'down_payment': 0,
        'closing_costs': 0,
        'emergency_fund': 0,
        'furniture': 0
    }
if 'properties_viewed' not in st.session_state:
    st.session_state.properties_viewed = []
if 'loan_info' not in st.session_state:
    st.session_state.loan_info = {
        'principal': 0,
        'interest_rate': 0,
        'term_years': 30,
        'start_date': datetime.now().strftime("%Y-%m-%d")
    }
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------- House API Integration ----------------------------- #
def geocode_address(address):
    """Convert address to latitude and longitude using Nominatim (OpenStreetMap)"""
    # Using Nominatim API which is free but has usage limits
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "PropertySearchApp/1.0"  # Nominatim requires a User-Agent
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    else:
        return None, None

# Property search page
import requests  # Add this line at the top of your script
import streamlit as st


def real_property_search(latitude, longitude, radius):
    # Fix the URL to use the parameters
    url = 'https://realtor16.p.rapidapi.com/search/forsale/coordinates'

    # Query string parameters
    querystring = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        "limit": 15
    }

    # Headers
    headers = {
        "X-RapidAPI-Key": 'c35ab3d705mshd50999ccaf60a08p1c1670jsna35df12d574c',
        "X-RapidAPI-Host": "realtor16.p.rapidapi.com"
    }

    # Send GET request to API
    response = requests.get(url, headers=headers, params=querystring)

    # Check if response was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        st.error(response.text)
        return None

# Function to calculate mortgage payment
def calculate_mortgage_payment(principal, annual_interest_rate, term_years):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    num_payments = term_years * 12
    if monthly_interest_rate == 0:
        return principal / num_payments
    monthly_payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / (
            (1 + monthly_interest_rate) ** num_payments - 1)
    return monthly_payment


# Function to generate amortization schedule
def generate_amortization_schedule(principal, annual_interest_rate, term_years, start_date):
    monthly_payment = calculate_mortgage_payment(principal, annual_interest_rate, term_years)
    schedule = []

    remaining_balance = principal
    monthly_interest_rate = annual_interest_rate / 12 / 100

    payment_date = datetime.strptime(start_date, "%Y-%m-%d")

    for i in range(term_years * 12):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        schedule.append({
            "payment_number": i + 1,
            "date": payment_date.strftime("%Y-%m-%d"),
            "payment": monthly_payment,
            "principal": principal_payment,
            "interest": interest_payment,
            "remaining_balance": max(0, remaining_balance)
        })

        payment_date = payment_date + timedelta(days=30)

    return schedule


def get_chatbot_response(user_query):
    # In a real app, you might use OpenAI API or another NLP service
    # This is a simple rule-based response for demonstration

    query = user_query.lower()

    if "save" in query and "month" in query:
        income = st.session_state.user_data['income']
        budget = st.session_state.user_data['budget']
        recommended_savings = max(income * 0.2, budget * 0.05)
        return f"Based on your income of ${income:,.2f} and target budget of ${budget:,.2f}, I recommend saving about ${recommended_savings:,.2f} per month towards your home purchase."

    elif "down payment" in query:
        budget = st.session_state.user_data['budget']
        recommended_dp = budget * 0.2
        return f"For a home with your budget of ${budget:,.2f}, a standard 20% down payment would be ${recommended_dp:,.2f}. However, there are programs that allow for as little as 3-5% down."

    elif "dti" in query or "debt to income" in query:
        dti = st.session_state.user_data['dti_ratio']
        if dti > 43:
            return f"Your current DTI ratio is {dti}%, which is above the typical maximum of 43% for qualifying for a mortgage. You might want to reduce some debt before proceeding."
        else:
            return f"Your DTI ratio of {dti}% is within acceptable limits for most mortgage lenders. The standard maximum is 43%."

    elif "afford" in query:
        income = st.session_state.user_data['income']
        max_affordability = income * 4
        return f"With your annual income of ${income:,.2f}, a common rule of thumb suggests you could afford a home up to ${max_affordability:,.2f}, but this depends on your debt, credit score, and other factors."

    else:
        return "I'm your budget buddy! Feel free to ask me about budgeting for a home purchase, down payment requirements, mortgage calculations, or any other financial aspects of buying property."


# Function to set custom CSS for the entire app
def set_custom_theme():
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --mint-green: #D5F5E3;
        --mint-light: #A2E4B8;
        --mint-dark: #82E0AA;
        --lavender: #E8DAEF;
        --light-blue: #D4F1F9;
        --soft-yellow: #FCF3CF;
    }

    .stApp {
        background-color: var(--mint-green);
    }

    /* Card styling */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Headers */
    h1, h2, h3 {
        color: #2E7D32 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--mint-dark);
        color: white;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #66BB6A;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: var(--mint-light);
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: var(--mint-light);
    }
    
     /* Smooth scroll for chat container */
    .chat-container {
        scroll-behavior: smooth;
    }

    </style>
    """, unsafe_allow_html=True)

# Add JavaScript for scrolling
def auto_scroll_js():
    js = """
    <script>
        function scrollToBottom() {
            // Target the chat expander which contains the messages
            const chatExpanders = window.parent.document.querySelectorAll('.stExpander');
            if (chatExpanders.length > 0) {
                // Get the last expander (which should be the chat)
                const chatExpander = chatExpanders[chatExpanders.length - 1];
                if (chatExpander) {
                    // Find the content part of the expander
                    const expanderContent = chatExpander.querySelector('.stExpander-content');
                    if (expanderContent) {
                        // Scroll the content to the bottom
                        expanderContent.scrollTop = expanderContent.scrollHeight;
                    }

                    // Also attempt to scroll any chat messages container that might exist
                    const chatMessages = chatExpander.querySelectorAll('.stChatMessage');
                    const lastMessage = chatMessages[chatMessages.length - 1];
                    if (lastMessage) {
                        lastMessage.scrollIntoView({behavior: 'smooth'});
                    }
                }
            }

            // Fallback: also scroll the entire page
            window.parent.scrollTo(0, document.body.scrollHeight);
        }

        // Set a delay to ensure content is rendered before scrolling
        setTimeout(scrollToBottom, 200);
    </script>
    """
    return components.html(js, height=0)

# Home page with updated theme
def render_home():
    set_custom_theme()

    st.title("Welcome to BudgetBuddy")
    st.subheader("Your Complete Property Buying Companion")

    col1, col2 = st.columns([1, 1.25])

    with col1:
        st.markdown("""
        ### Start Your Property Buying Journey Today!

        BudgetBuddy helps you manage all financial aspects of buying property:

        1. **Assess your financial readiness** with our comprehensive quiz
        2. **Plan and save** for your down payment with our budgeting tools
        3. **Find the perfect property** within your budget
        4. **Track your mortgage payments** and build equity

        Get started by taking our financial profile quiz!
        """)

        if st.button("Begin Financial Quiz >>"):
            st.session_state.page = "Quiz"

    with col2:
        st.image("https://wallpaperaccess.com/full/3816377.png", caption="Plan your dream home purchase.", use_container_width=True)

        # Show quick stats with updated styling if user has entered data
        if st.session_state.user_data['budget'] > 0:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 15px; border-radius: 8px; border-left: 4px solid #82E0AA;">
            <h3 style="color: #2E7D32; margin-top: 0;">Your Progress</h3>
            </div>
            """, unsafe_allow_html=True)

            # Calculate a mock affordability score
            income = st.session_state.user_data['income']
            loans = st.session_state.user_data['loans']
            budget = st.session_state.user_data['budget']

            affordability_ratio = min(100, max(0, 100 * (income - loans * 0.1) / (budget)))

            st.progress(affordability_ratio / 100, text=f"Affordability: {affordability_ratio:.1f}%")

            savings_progress = sum(st.session_state.roundup_savings.values()) / (budget * 0.2) * 100
            savings_progress = min(100, max(0, savings_progress))

            st.progress(savings_progress / 100, text=f"Savings Goal: {savings_progress:.1f}%")

    # Close the container div
    st.markdown("</div>", unsafe_allow_html=True)

    # Add feature highlights with pastel colors
    st.markdown("<br>", unsafe_allow_html=True)

    # How it works section
    st.markdown("### How it Works:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background-color: #FCF3CF; padding: 15px; border-radius: 10px; height: 150px; text-align: center;">
            <h3 style="color: #2E7D32;">Financial Planning</h3>
            <p>Personalized budget planning based on your income and goals</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background-color: #E8DAEF; padding: 15px; border-radius: 10px; height: 150px; text-align: center;">
            <h3 style="color: #4A235A;">Property Search</h3>
            <p>Find homes that match your budget and preferences</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background-color: #D4F1F9; padding: 15px; border-radius: 10px; height: 150px; text-align: center;">
            <h3 style="color: #1A5276;">Loan Tracking</h3>
            <p>Visualize your mortgage payments and build equity</p>
        </div>
        """, unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.markdown("""
    <div style="text-align: center; padding-bottom: 10px;">
        <h1 style="color: #2E7D32;">BudgetBuddy 🏠</h1>
        <p style="color: #388E3C;">Your Property Buying Companion</p>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Home"):
        st.session_state.page = "Home"

    st.sidebar.markdown("---")

    if st.sidebar.button("1. Financial Profile Quiz"):
        st.session_state.page = "Quiz"

    if st.sidebar.button("2. Roundup Buddy"):
        st.session_state.page = "Budgeting"

    if st.sidebar.button("3. Property Search"):
        st.session_state.page = "Property Search"

    if st.sidebar.button("4. Loan Tracker"):
        st.session_state.page = "Loan Tracker"

    st.sidebar.markdown("---")

    if st.sidebar.button("Chat with BudgetBuddy"):
        st.session_state.show_chat = not st.session_state.get("show_chat", False)

    # Display user info if available
    if st.session_state.user_data['name']:
        st.sidebar.markdown(f"""
        <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px;">
            <h3 style="color: #2E7D32; margin-top: 0;">Welcome, {st.session_state.user_data['name']}!</h3>
            <p>Budget: ${st.session_state.user_data['budget']:,.2f}</p>
            <p>Location: {st.session_state.user_data['location']}</p>
        </div>
        """, unsafe_allow_html=True)


# ----------------------------------------- Quiz page ----------------------------------------- #
def render_quiz():
    st.title("🏡 Let's Find Your Perfect Home Match")

    with st.form("financial_quiz"):
        st.subheader("🎯 Section 1: Basic Info")

        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Min Price ($)",
                                        min_value=50000,
                                        value=int(st.session_state.user_data.get('min_price', 300000)),
                                        step=10000)
        with col2:
            max_price = st.number_input("Max Price ($)",
                                        min_value=50000,
                                        value=int(st.session_state.user_data.get('max_price', 500000)),
                                        step=10000)

        # Store the average as the budget
        st.session_state.user_data['budget'] = (min_price + max_price) / 2
        st.session_state.user_data['min_price'] = min_price
        st.session_state.user_data['max_price'] = max_price

        # Location input
        st.session_state.user_data['location'] = st.text_input("Where are you looking to buy? (City, State, or ZIP)",
                                                               value=st.session_state.user_data.get('location', ''))

        st.divider()
        st.subheader("💼 Section 2: Income")

        monthly_income = st.number_input("What is your total monthly income (before taxes)? ($)",
                                         min_value=0,
                                         value=int(st.session_state.user_data.get('monthly_income', 0)),
                                         step=100)

        # Convert monthly to annual for backend compatibility
        st.session_state.user_data['income'] = monthly_income * 12
        st.session_state.user_data['monthly_income'] = monthly_income

        has_cobuyer = st.radio("Do you have a co-buyer?", ["No", "Yes"],
                               index=0 if not st.session_state.user_data.get('has_cobuyer') else 1)

        st.session_state.user_data['has_cobuyer'] = (has_cobuyer == "Yes")

        if has_cobuyer == "Yes":
            cobuyer_income = st.number_input("Co-buyer monthly income ($)",
                                             min_value=0,
                                             value=int(st.session_state.user_data.get('cobuyer_income', 0)),
                                             step=100)
            st.session_state.user_data['cobuyer_income'] = cobuyer_income
            st.session_state.user_data['income'] += (cobuyer_income * 12)

        st.divider()
        st.subheader("💳 Section 3: Debt")

        monthly_debt = st.number_input("What are your total monthly debt payments? ($)",
                                       min_value=0,
                                       value=int(st.session_state.user_data.get('loans', 0)),
                                       step=50,
                                       help="Include credit cards, student loans, car loans, etc.")

        st.session_state.user_data['loans'] = monthly_debt

        has_outstanding_loans = st.radio("Do you currently have any outstanding loans?",
                                         ["No", "Yes"],
                                         index=0 if not st.session_state.user_data.get('has_outstanding_loans') else 1)

        st.session_state.user_data['has_outstanding_loans'] = (has_outstanding_loans == "Yes")

        if has_outstanding_loans == "Yes":
            col1, col2, col3 = st.columns(3)
            with col1:
                loan_type = st.selectbox("Type of loan",
                                         ["Mortgage", "Auto Loan", "Student Loan", "Personal Loan", "Other"],
                                         index=0)
            with col2:
                loan_balance = st.number_input("Balance ($)",
                                               min_value=0,
                                               value=int(st.session_state.user_data.get('loan_balance', 0)),
                                               step=1000)
            with col3:
                loan_payment = st.number_input("Monthly Payment ($)",
                                               min_value=0,
                                               value=int(st.session_state.user_data.get('loan_payment', 0)),
                                               step=50)

            st.session_state.user_data['loan_type'] = loan_type
            st.session_state.user_data['loan_balance'] = loan_balance
            st.session_state.user_data['loan_payment'] = loan_payment

        credit_score_options = ["Below 580 (Poor)", "580–669 (Fair)", "670–739 (Good)",
                                "740–799 (Very Good)", "800+ (Excellent)"]

        credit_score_selection = st.selectbox("What's your current credit score?",
                                              credit_score_options,
                                              index=2)  # Default to "Good"

        # Map the credit score range to a numeric value for calculations
        credit_score_mapping = {
            "Below 580 (Poor)": 550,
            "580–669 (Fair)": 625,
            "670–739 (Good)": 700,
            "740–799 (Very Good)": 770,
            "800+ (Excellent)": 810
        }

        st.session_state.user_data['credit_score'] = credit_score_mapping[credit_score_selection]
        st.session_state.user_data['credit_range'] = credit_score_selection

        st.divider()
        st.subheader("📊 Section 4: Financial Health")

        down_payment = st.number_input("How much do you have saved for a down payment? ($)",
                                       min_value=0,
                                       value=int(st.session_state.user_data.get('savings', 0)),
                                       step=1000)

        st.session_state.user_data['savings'] = down_payment

        include_closing_costs = st.radio("Do you want to include estimated closing costs in your budget?",
                                         ["Yes", "No", "Not sure"],
                                         index=0 if st.session_state.user_data.get('include_closing_costs', True) else
                                         (1 if st.session_state.user_data.get('include_closing_costs') is False else 2))

        st.session_state.user_data['include_closing_costs'] = (include_closing_costs == "Yes")

        know_dti = st.radio("Do you know your Debt-to-Income (DTI) ratio?",
                            ["Yes, I know it", "No, please calculate it for me"],
                            index=0 if st.session_state.user_data.get('knows_dti', False) else 1)

        st.session_state.user_data['knows_dti'] = (know_dti == "Yes, I know it")

        if know_dti == "Yes, I know it":
            dti_ratio = st.number_input("Enter your DTI ratio (%)",
                                        min_value=0.0,
                                        max_value=100.0,
                                        value=float(st.session_state.user_data.get('dti_ratio', 0.0)),
                                        step=0.1)
            st.session_state.user_data['dti_ratio'] = dti_ratio
        else:
            # Calculate DTI if user doesn't know it
            if monthly_income > 0:
                dti = (monthly_debt / monthly_income) * 100
                st.session_state.user_data['dti_ratio'] = round(dti, 2)
                st.metric("Your calculated DTI ratio", f"{st.session_state.user_data['dti_ratio']}%")

        st.divider()
        st.subheader("🏠 Section 5: Home Goals")

        timeline_options = ["Within 3 months", "3–6 months", "6–12 months", "Just browsing"]
        timeline = st.radio("When are you planning to buy?",
                            timeline_options,
                            index=timeline_options.index(st.session_state.user_data.get('timeline', "Just browsing"))
                            if st.session_state.user_data.get('timeline') in timeline_options else 3)

        st.session_state.user_data['timeline'] = timeline

        home_type_options = ["Single-family", "Condo/Townhome", "Multi-family", "Not sure"]
        home_type = st.selectbox("What type of home are you looking for?",
                                 home_type_options,
                                 index=home_type_options.index(st.session_state.user_data.get('home_type', "Not sure"))
                                 if st.session_state.user_data.get('home_type') in home_type_options else 3)

        st.session_state.user_data['home_type'] = home_type

        usage_options = ["Live in it", "Rent it", "Both"]
        usage = st.radio("Do you plan to live in the home or rent it out?",
                         usage_options,
                         index=usage_options.index(st.session_state.user_data.get('usage', "Live in it"))
                         if st.session_state.user_data.get('usage') in usage_options else 0)

        st.session_state.user_data['usage'] = usage

        # Name field at the end for optional identification
        st.session_state.user_data['name'] = st.text_input("Your Name (Optional)",
                                                           value=st.session_state.user_data.get('name', ''))

        # Calculate monthly expenses to maintain compatibility with original code
        # This is just a placeholder - in a real app you might calculate this differently
        st.session_state.user_data['monthly_expenses'] = monthly_debt

        submit = st.form_submit_button("Find My Perfect Home Match")

        if submit:
            with st.spinner("Bud is crunching the numbers..."):
                # Simulate a brief delay for effect
                import time
                time.sleep(1)

            st.success("Your financial profile has been updated successfully!")

            # Calculate affordability
            if st.session_state.user_data['income'] > 0:
                affordable_amount = st.session_state.user_data['income'] * 4
                if st.session_state.user_data['budget'] > affordable_amount * 1.2:
                    st.warning(
                        f"Your budget may be high relative to your income. A recommended budget based on your income would be around ${affordable_amount:,.2f}")

            st.session_state.page = "Budgeting"
# --------------------------------------------------------------------------------------------------- #
import requests
import streamlit as st


# Function to get customer details
def get_customer_data(customer_id, api_key):
    url = f"http://api.nessieisreal.com/customers/{customer_id}?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return customer data
    else:
        return None


# Function to get accounts for a customer
def get_accounts_for_customer(customer_id, api_key):
    url = f"http://api.nessieisreal.com/customers/{customer_id}/accounts?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return account data
    else:
        return None


# Function to get purchases for a checking account
def get_purchases_for_account(checking_account_id, api_key):
    url = f"http://api.nessieisreal.com/accounts/{checking_account_id}/purchases?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return purchase data
    else:
        return None


import time


def update_account_balance(account_id, new_balance, api_key):
    url = f"http://api.nessieisreal.com/accounts/{account_id}?key={api_key}"
    data = {"balance": new_balance}
    response = requests.put(url, json=data)
    st.write(f"Updating account {account_id} with new balance: {new_balance}")
    st.write(f"Response status code: {response.status_code}")
    st.write(f"Response text: {response.text}")
    if response.status_code == 200:
        return response.json()  # Return updated account data
    else:
        return None


import time  # For adding a small delay


# Function to create a deposit into savings account
def deposit_to_savings(account_id, amount, api_key):
    url = f"http://api.nessieisreal.com/accounts/{account_id}/deposits?key={api_key}"
    payload = {
        "medium": "balance",
        "transaction_date": "2025-04-06",  # You can adjust this to the current date if needed
        "amount": amount,
        "description": "Round-up transfer"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        return response.json()
    else:
        print("Deposit failed:", response.status_code, response.text)
        return None


def transfer_to_savings(savings_account_id, checking_account_id, customer_id, api_key):
    # Fetch purchases from the checking account
    purchases = get_purchases_for_account(checking_account_id, api_key)
    if purchases:
        total_transfer = 0
        for purchase in purchases:
            amount = purchase['amount']
            rounded_up = (int(amount) + 1) if amount != int(amount) else int(amount)
            transfer_amount = round(rounded_up - amount, 2)
            if transfer_amount > 0:
                total_transfer += transfer_amount

        total_transfer = round(total_transfer, 2)

        # Perform deposit via POST (this updates the balance)
        deposit_result = deposit_to_savings(savings_account_id, total_transfer, api_key)
        if deposit_result:
            # Wait for a brief moment to allow the API to reflect the updated balance
            time.sleep(2)  # Wait 2 seconds for the balance to update
            # Re-fetch the actual updated savings account balance
            accounts_data = get_accounts_for_customer(customer_id, api_key)
            if accounts_data:
                updated_savings = next((acct for acct in accounts_data if acct['_id'] == savings_account_id), None)
                if updated_savings:
                    return total_transfer, updated_savings['balance']
        return None
    return None


# Dummy authentication function using if/elif statements
def authenticate_user(username, password):
    if username == "emilyC" and password == "123":
        return "67f1e8999683f20dd5194b84"
    elif username == "avaW" and password == "abc":
        return "67f1e8d59683f20dd5194b85"
    elif username == "ethanM" and password == "456":
        return "67f1e8e19683f20dd5194b86"
    elif username == "sophiaJ" and password == "efg":
        return "67f1e8f19683f20dd5194b87"
    else:
        return None


# Function to display customer info and purchases
def display_customer_info(customer_id, api_key):
    customer_data = get_customer_data(customer_id, api_key)
    if customer_data:
        st.write(f"Customer Name: {customer_data['first_name']} {customer_data['last_name']}")
        st.write(f"Address: {customer_data['address']['street_number']} {customer_data['address']['street_name']}")
        st.write(
            f"City: {customer_data['address']['city']}, {customer_data['address']['state']} {customer_data['address']['zip']}")

        accounts_data = get_accounts_for_customer(customer_id, api_key)
        if accounts_data:
            checking_account_id = None
            savings_account_id = None
            for account in accounts_data:
                if account['type'] == 'Checking':
                    checking_account_id = account['_id']
                if account['type'] == 'Savings':
                    savings_account_id = account['_id']

            if checking_account_id:
                checking_account_data = get_purchases_for_account(checking_account_id, api_key)
                if checking_account_data:
                    st.write("Purchases:")
                    for purchase in checking_account_data:
                        st.write(f" - {purchase['description']}: ${purchase['amount']}")

            if checking_account_id and savings_account_id:
                if st.button("Transfer Leftover Cents to Savings"):
                    result = transfer_to_savings(savings_account_id, checking_account_id, customer_id, api_key)
                    if result is not None:
                        transfer_amount, updated_balance = result
                        st.success(f"Transferred ${transfer_amount:.2f} to your savings account!")
                        st.write(f"Your updated savings balance is now: ${updated_balance:.2f}")
                        st.write("Congratulations! You are one step closer to your financial goals.")
                    else:
                        st.error("Error in transferring funds.")
        else:
            st.error("No accounts found for this customer.")
    else:
        st.error("Customer data not found.")


# Render login and budgeting UI
def render_budgeting():
    st.title("RoundUp Buddy")
    st.subheader("Powered by CapitalOne")
    st.write("Please enter your CapitalOne username and password.")

    # Initialize session state variables if not present
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = None

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Login"):
        customer_id = authenticate_user(username, password)
        if customer_id:
            st.session_state.customer_id = customer_id  # Store in session state
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")

    # If a customer is logged in, display their info
    if st.session_state.customer_id:
        api_key = "0d0de272b4e17fab344119646ea1862b"
        display_customer_info(st.session_state.customer_id, api_key)


## -------- CODE STOPS EHEREHERE --------
##
####
####
import requests
import streamlit as st
# --------------------------------------------------------------------------------------------------- #


# ------------------------------------------ Property Search ---------------------------------------------------- #

def render_property_search():
    st.title("Property Search")

    # Location input
    location = st.text_input("Enter Location (e.g., 'Houston, TX' or '123 Main St, New York, NY')")

    # Search radius input
    radius = st.number_input("Search Radius (km)", min_value=1, value=30)

    # Advanced Options
    with st.expander("Advanced Options"):
        st.info("If location search doesn't work, you can manually enter coordinates")
        manual_coords = st.checkbox("Enter coordinates manually")

        if manual_coords:
            latitude = st.number_input("Enter Latitude", value=29.27052)
            longitude = st.number_input("Enter Longitude", value=-95.74991)

    if st.button("Search"):
        with st.spinner("Searching for properties..."):
            # Determine coordinates
            if manual_coords:
                lat, lng = latitude, longitude
            else:
                if not location:
                    st.error("Please enter a location")
                    return

                lat, lng = geocode_address(location)
                if lat is None or lng is None:
                    st.error("Could not find coordinates. Try another location or use manual entry.")
                    return

            # Perform search
            properties = real_property_search(lat, lng, radius)

            if properties and "properties" in properties:
                st.subheader(f"Found {len(properties['properties'])} properties")
                st.write("---")
                cols = st.columns(3)  # Changed from 2 to 3 columns

                for i, prop in enumerate(properties.get("properties", [])):
                    with cols[i % 3]:  # Changed from i % 2 to i % 3
                        with st.container():
                            # Address
                            if "address" in prop:
                                st.subheader(f"{prop['address']}")
                            elif "location" in prop and "address" in prop["location"]:
                                addr = prop["location"]["address"]
                                st.subheader(f"{addr['line']} {addr.get('city', '')}, {addr.get('state_code', '')}")
                            else:
                                st.subheader("Address not available")

                            # Image
                            img_url = None
                            if "primary_photo" in prop and "href" in prop["primary_photo"]:
                                img_url = prop["primary_photo"]["href"]
                            elif "photos" in prop and prop["photos"] and "href" in prop["photos"][0]:
                                img_url = prop["photos"][0]["href"]

                            if img_url:
                                st.image(img_url, use_container_width=True)
                            else:
                                st.markdown("📷 *No image available*")

                            # Basic Info
                            col1, col2 = st.columns(2)

                            # Get property price
                            list_price = prop.get('list_price', 0)
                            if isinstance(list_price, str) and list_price.isdigit():
                                list_price = int(list_price)

                            with col1:
                                st.markdown(f"**Price:** ${list_price:,}")
                            beds = "N/A"
                            baths = "N/A"
                            if "description" in prop:
                                beds = prop["description"].get("beds", "N/A")
                                baths = prop["description"].get("baths_consolidated",
                                                                prop["description"].get("baths", "N/A"))
                            elif "beds" in prop:
                                beds = prop["beds"]
                            if "baths" in prop:
                                baths = prop["baths"]
                            with col2:
                                st.markdown(f"**Beds/Baths:** {beds}/{baths}")

                            sqft = "N/A"
                            if "description" in prop and "sqft" in prop["description"]:
                                sqft = prop["description"]["sqft"]
                            elif "building_size" in prop:
                                sqft = prop.get("building_size", {}).get("size", "N/A")
                            st.markdown(f"**Area:** {sqft} sqft")

                            # View More Details - REPLACED WITH RISK ANALYSIS
                            with st.expander("View Risk Analysis", expanded=False):
                                st.markdown("### Buyer Risk Analysis")

                                # Get user data from session state
                                min_price = st.session_state.user_data.get('min_price', 0)
                                max_price = st.session_state.user_data.get('max_price', 0)
                                credit_score = st.session_state.user_data.get('credit_score', 0)
                                dti_ratio = st.session_state.user_data.get('dti_ratio', 0)
                                savings = st.session_state.user_data.get('savings', 0)

                                # Calculate risk factors

                                # 1. Price Range Risk
                                price_risk = "low"
                                if list_price > max_price:
                                    price_risk = "high"
                                elif list_price > (max_price * 0.9):
                                    price_risk = "moderate"

                                # 2. Credit Score Risk
                                credit_risk = "high"
                                if credit_score >= 740:
                                    credit_risk = "low"
                                elif credit_score >= 660:
                                    credit_risk = "moderate"

                                # 3. DTI Risk
                                dti_risk = "high"
                                if dti_ratio < 36:
                                    dti_risk = "low"
                                elif dti_ratio <= 45:
                                    dti_risk = "moderate"

                                # 4. Down Payment Risk
                                down_payment_percentage = 0
                                if list_price > 0:
                                    down_payment_percentage = (savings / list_price) * 100

                                down_payment_risk = "high"
                                if down_payment_percentage >= 20:
                                    down_payment_risk = "low"
                                elif down_payment_percentage >= 5:
                                    down_payment_risk = "moderate"

                                # Calculate overall risk level
                                risk_scores = {"low": 1, "moderate": 2, "high": 3}
                                avg_risk_score = (risk_scores[price_risk] +
                                                  risk_scores[credit_risk] +
                                                  risk_scores[dti_risk] +
                                                  risk_scores[down_payment_risk]) / 4

                                overall_risk = "high"
                                if avg_risk_score <= 1.5:
                                    overall_risk = "low"
                                elif avg_risk_score <= 2.5:
                                    overall_risk = "moderate"

                                # Display risk analysis
                                risk_color = {
                                    "low": "green",
                                    "moderate": "orange",
                                    "high": "red"
                                }

                                st.markdown(
                                    f"### Overall Risk: <span style='color:{risk_color[overall_risk]};'>{overall_risk.upper()}</span>",
                                    unsafe_allow_html=True)

                                # Show risk breakdown
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("#### Risk Factors:")
                                    st.markdown(
                                        f"- **Price Range**: <span style='color:{risk_color[price_risk]};'>{price_risk}</span>",
                                        unsafe_allow_html=True)
                                    st.markdown(
                                        f"- **Credit Score**: <span style='color:{risk_color[credit_risk]};'>{credit_risk}</span>",
                                        unsafe_allow_html=True)

                                with col2:
                                    st.markdown("&nbsp;")
                                    st.markdown(
                                        f"- **DTI Ratio**: <span style='color:{risk_color[dti_risk]};'>{dti_risk}</span>",
                                        unsafe_allow_html=True)
                                    st.markdown(
                                        f"- **Down Payment**: <span style='color:{risk_color[down_payment_risk]};'>{down_payment_risk}</span>",
                                        unsafe_allow_html=True)

                                # Display risk description based on overall risk
                                st.markdown("### What This Means")

                                if overall_risk == "low":
                                    st.markdown("""
                                    You're a **low-risk buyer** with a strong financial foundation. This includes a high credit score (usually 740+), 
                                    a stable income history, a low debt-to-income (DTI) ratio (below 36%), and the ability to put down a sizable 
                                    down payment (20% or more). As a low-risk buyer, you're attractive to lenders because you've demonstrated 
                                    financial responsibility and have the resources to weather potential market fluctuations or unexpected costs.
                                    """)
                                    st.success("This property appears to be a good match for your financial profile!")

                                elif overall_risk == "moderate":
                                    st.markdown("""
                                    You're a **moderate-risk buyer** with some solid financial indicators but also a few red flags. 
                                    For instance, you may have a decent credit score (around 660–739), a moderate DTI ratio (36–45%), 
                                    or a smaller down payment (5–19%). While you may qualify for a mortgage, you might not get the most 
                                    favorable interest rates or loan terms. Lenders may also require private mortgage insurance (PMI) 
                                    if the down payment is under 20%, adding to the monthly cost.
                                    """)
                                    st.warning(
                                        "You might face some challenges with financing this property. Consider improving your financial situation before proceeding.")

                                else:  # high risk
                                    st.markdown("""
                                    You're a **high-risk buyer** typically with a lower credit score (under 660), inconsistent income, 
                                    a high DTI ratio (above 45%), and minimal savings for a down payment. As a high-risk buyer, you may 
                                    struggle to qualify for traditional loans or may only qualify for high-interest options. In addition, 
                                    you are more vulnerable to financial shocks, such as job loss or unexpected repairs, which increases 
                                    the risk for both you and the lender.
                                    """)
                                    st.error(
                                        "This property may be difficult to finance with your current financial profile. Consider improving your credit score, reducing debt, or increasing your savings before proceeding.")

                                # Show recommendations based on risk factors
                                st.markdown("### Recommendations")

                                recommendations = []

                                if price_risk != "low":
                                    recommendations.append(
                                        "Consider properties within your budget range to avoid overextending financially.")

                                if credit_risk != "low":
                                    recommendations.append(
                                        "Work on improving your credit score to qualify for better interest rates.")

                                if dti_risk != "low":
                                    recommendations.append("Reduce existing debt to improve your debt-to-income ratio.")

                                if down_payment_risk != "low":
                                    recommendations.append(
                                        "Continue saving for a larger down payment to avoid PMI and reduce your loan amount.")

                                if not recommendations:
                                    st.success("You're in great financial shape for this property!")
                                else:
                                    for rec in recommendations:
                                        st.markdown(f"- {rec}")
            else:
                st.error("No properties found or failed to fetch data.")


# --------------------------------------------------------------------------------------------------------- #

def render_loan_tracker():
    st.title("Mortgage & Loan Tracker")

    if not st.session_state.loan_info['principal']:
        st.info("No loan information yet. Either search for a property first or enter loan details manually.")

    with st.form("loan_info_form"):
        st.subheader("Loan Details")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.loan_info['principal'] = st.number_input(
                "Loan Amount ($)",
                min_value=0.0,
                value=float(st.session_state.loan_info['principal']),
                step=10000.0
            )

            st.session_state.loan_info['interest_rate'] = st.number_input(
                "Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=float(st.session_state.loan_info['interest_rate'] or 6.5),
                step=0.1
            )

        with col2:
            st.session_state.loan_info['term_years'] = st.selectbox(
                "Loan Term (years)",
                options=[15, 20, 30],
                index=2 if st.session_state.loan_info['term_years'] == 30 else (
                    1 if st.session_state.loan_info['term_years'] == 20 else 0)
            )

            st.session_state.loan_info['start_date'] = st.date_input(
                "Loan Start Date",
                value=datetime.strptime(st.session_state.loan_info['start_date'], "%Y-%m-%d") if
                st.session_state.loan_info['start_date'] else datetime.now()
            ).strftime("%Y-%m-%d")

        if st.form_submit_button("Calculate Payment"):
            st.session_state.show_amortization = True

    if st.session_state.loan_info['principal'] > 0 and getattr(st.session_state, 'show_amortization', False):
        monthly_payment = calculate_mortgage_payment(
            st.session_state.loan_info['principal'],
            st.session_state.loan_info['interest_rate'],
            st.session_state.loan_info['term_years']
        )

        total_interest = (monthly_payment * 12 * st.session_state.loan_info['term_years']) - st.session_state.loan_info[
            'principal']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Monthly Payment", f"${monthly_payment:,.2f}")

        with col2:
            st.metric("Total Interest", f"${total_interest:,.2f}")

        with col3:
            total_cost = st.session_state.loan_info['principal'] + total_interest
            st.metric("Total Cost", f"${total_cost:,.2f}")

        st.subheader("Amortization Schedule")

        tab1, tab2 = st.tabs(["Overview", "Full Schedule"])

        with tab1:
            # Create amortization schedule
            schedule = generate_amortization_schedule(
                st.session_state.loan_info['principal'],
                st.session_state.loan_info['interest_rate'],
                st.session_state.loan_info['term_years'],
                st.session_state.loan_info['start_date']
            )

            # Prepare data for visualization
            years = [1, 5, 10, 15, 20, 30]
            years = [y for y in years if y <= st.session_state.loan_info['term_years']]

            # Extract data points for visualization
            balance_data = []
            principal_paid_data = []
            interest_paid_data = []

            initial_principal = st.session_state.loan_info['principal']

            for year in years:
                payment_index = year * 12 - 1
                if payment_index < len(schedule):
                    payment = schedule[payment_index]
                    balance_data.append(payment['remaining_balance'])

                    # Calculate cumulative principal and interest paid
                    principal_paid = initial_principal - payment['remaining_balance']
                    principal_paid_data.append(principal_paid)

                    interest_paid = payment['payment_number'] * monthly_payment - principal_paid
                    interest_paid_data.append(interest_paid)

            # Create a line chart showing remaining balance over time
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(years, balance_data, marker='o', linestyle='-', color='blue', label='Remaining Balance')
            ax.set_xlabel('Years')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Mortgage Balance Over Time')
            ax.grid(True)

            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

            st.pyplot(fig)

            # Create a stacked bar chart showing principal vs interest
            fig, ax = plt.subplots(figsize=(10, 6))
            width = 0.5

            ax.bar(years, principal_paid_data, width, label='Principal Paid', color='green')
            ax.bar(years, interest_paid_data, width, bottom=principal_paid_data, label='Interest Paid', color='red')

            ax.set_xlabel('Years')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Principal vs. Interest Paid Over Time')
            ax.legend()

            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

            st.pyplot(fig)

        with tab2:
            # Display full amortization schedule
            schedule = generate_amortization_schedule(
                st.session_state.loan_info['principal'],
                st.session_state.loan_info['interest_rate'],
                st.session_state.loan_info['term_years'],
                st.session_state.loan_info['start_date']
            )

            # Create a DataFrame for display
            df = pd.DataFrame(schedule)
            # Format the columns for better display
            df['payment'] = df['payment'].map('${:,.2f}'.format)
            df['principal'] = df['principal'].map('${:,.2f}'.format)
            df['interest'] = df['interest'].map('${:,.2f}'.format)
            df['remaining_balance'] = df['remaining_balance'].map('${:,.2f}'.format)

            # Display in chunks of years to avoid overwhelming the UI
            years_to_show = st.slider("Select years to display:", 1, st.session_state.loan_info['term_years'], 5)
            payments_to_show = years_to_show * 12

            st.dataframe(df.head(payments_to_show), hide_index=True)

            # Option to download full schedule as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full Amortization Schedule",
                data=csv,
                file_name="amortization_schedule.csv",
                mime="text/csv",
            )


# ---------------------------- Chatbot integration ----------------------------- #

from google import genai

# Initialize Gemini Client
client = genai.Client(api_key="AIzaSyC12WmkNvUM5Y49rbJ_uU6rfrk32IG4CiI")


def generate_gemini_response(prompt):
    """
    Function to send a prompt to Gemini API and return the generated response.
    """
    try:
        # Call the Gemini API to generate a response
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # You can adjust this based on the specific model you want to use
            contents=prompt,
        )
        # Return the text content of the response
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# Replace your existing render_chatbot function with this:
def render_chatbot():
    st.sidebar.markdown("---")
    if st.sidebar.checkbox("Open Finance Chatbot"):
        # Create a container for the chat
        chat_container = st.container()

        with chat_container:
            st.subheader("Finance Chatbot")
            st.write("Ask me anything about your property buying journey!")

            # Initialize chat history if needed
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Display chat history in the chat interface
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # Chat input
            if prompt := st.chat_input("Ask about financing, budgeting, or property buying"):
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": prompt})

                # Display user message
                with st.chat_message("user"):
                    st.write(prompt)

                # Generate response using Gemini
                with st.spinner("Thinking..."):
                    response = generate_gemini_response(prompt)

                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

                # Display assistant response
                with st.chat_message("assistant"):
                    st.write(response)



# ----------------------------------------------------------------------------------- #

# Main app logic
def main():
    configure_page()

    # Initialize show_chat in session state if it doesn't exist
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False

    # Render sidebar
    render_sidebar()

    if st.session_state.show_chat:
        st.info("Chat window is open at the bottom of the page. Scroll down to chat with BudgetBuddy!")

    # Render the appropriate page based on session state
    if st.session_state.page == "Home":
        render_home()
    elif st.session_state.page == "Quiz":
        render_quiz()
    elif st.session_state.page == "Budgeting":
        render_budgeting()
    elif st.session_state.page == "Property Search":
        render_property_search()
    elif st.session_state.page == "Loan Tracker":
        render_loan_tracker()

    # Add the chat interface at the bottom if enabled
    if st.session_state.show_chat:
        st.markdown("---")
        st.markdown("### Chat with BudgetBuddy:")
        with st.expander("", expanded=True):
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # First, create a container and display all existing messages
            chat_container = st.container()
            with chat_container:
                # Display all messages from history
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

            # Then, handle new input *after* displaying history
            if prompt := st.chat_input("Ask about financing, budgeting, or property buying"):
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": prompt})

                # Display user message in the container
                with chat_container.chat_message("user"):
                    st.write(prompt)

                # Generate response using Gemini
                with st.spinner("BudgetBuddy is coming up with a response..."):
                    response = generate_gemini_response(prompt)

                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

                # Display assistant response in the container
                with chat_container.chat_message("assistant"):
                    st.write(response)

                # Add the auto scroll JavaScript after updating the chat
                auto_scroll_js()

                # Force a rerun to update the chat history display
                st.rerun()

            # Add auto-scroll even when just displaying history (helps with initial load)
            if st.session_state.chat_history:
                auto_scroll_js()

if __name__ == "__main__":
    main()
