import streamlit as st
from calculator import RealEstateInvestmentAnalysis
import streamlit as st
import pandas as pd  # Add this line
from calculator import RealEstateInvestmentAnalysis

def main():
    st.title("Real Estate Investment Calculator")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")
        property_value = st.number_input(
            "Property Value (₪)",
            value=900000,
            step=10000,
            format="%d"
        )
        down_payment_percent = st.slider(
            "Down Payment (%)",
            min_value=0,
            max_value=100,
            value=25
        )
        rental_income = st.number_input(
            "Monthly Rental Income (₪)",
            value=3500,
            step=100,
            format="%d"
        )
        annual_appreciation_rate = st.number_input(
            "Annual Property Appreciation Rate (%)",
            value=3.5,
            step=0.1,
            format="%.1f"
        )

        st.subheader("Loan Details")
        loan_term_years = st.slider(
            "Loan Term (Years)",
            min_value=5,
            max_value=30,
            value=30
        )
        fixed_portion = st.slider(
            "Fixed Rate Portion (%)",
            min_value=0,
            max_value=100,
            value=30
        )
        fixed_rate = st.number_input(
            "Fixed Interest Rate (%)",
            value=5.0,
            step=0.1,
            format="%.1f"
        )
        variable_rate = st.number_input(
            "Variable Interest Rate (%)",
            value=4.5,
            step=0.1,
            format="%.1f"
        )
        prime_base_rate = st.number_input(
            "Prime Base Rate (%)",
            value=6.0,
            step=0.1,
            format="%.1f"
        )

    with col2:
        st.subheader("Investment Parameters")
        years = st.slider(
            "Analysis Period (Years)",
            min_value=1,
            max_value=30,
            value=10
        )
        central_rent = st.number_input(
            "Current Central Rent (₪)",
            value=7000,
            step=100,
            format="%d"
        )
        monthly_savings = st.number_input(
            "Monthly Investment Capacity (₪)",
            value=0,
            step=100,
            format="%d"
        )
        savings_return_rate = st.number_input(
            "Expected Investment Return Rate (%)",
            value=7.5,
            step=0.1,
            format="%.1f"
        )
        inflation_rate = st.number_input(
            "Inflation Rate (%)",
            value=2.0,
            step=0.1,
            format="%.1f"
        )

    # Create parameter dictionary
    params = {
        'property_value': property_value,
        'down_payment_percent': down_payment_percent,
        'fixed_rate': fixed_rate,
        'variable_rate': variable_rate,
        'loan_term_years': loan_term_years,
        'rental_income': rental_income,
        'annual_appreciation_rate': annual_appreciation_rate,
        'years': years,
        'central_rent': central_rent,
        'monthly_savings': monthly_savings,
        'savings_return_rate': savings_return_rate,
        'inflation_rate': inflation_rate,
        'fixed_portion': fixed_portion,
        'prime_base_rate': prime_base_rate
    }

    if st.button("Calculate"):
        try:
            # Create analysis object
            analysis = RealEstateInvestmentAnalysis(**params)

            # Get results
            buy_results = analysis.calculate_buy_scenario(show_real_values=False)
            rent_results = analysis.calculate_rent_scenario(show_real_values=False)

            # Display results
            st.header("Results")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """<h3 style='
                        color: #4ade80;
                        margin-bottom: 10px;
                        font-size: 24px;
                    '>Buy Scenario</h3>""",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""<div style='
                                    background-color: #fef9c3; 
                                    padding: 15px; 
                                    border-radius: 10px; 
                                    color: #000000;
                                    font-weight: bold;
                                    font-size: 18px;
                                    margin: 10px 0;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                '>
                                    Net Asset Value:<br/>
                                    <span style='font-size: 24px;'>₪{buy_results['nav']:,.0f}</span>
                                </div>""",
                    unsafe_allow_html=True
                )
                st.metric("Monthly Net Income", f"₪{buy_results['monthly_net_income']:,.0f}")
                st.metric("Total Monthly Cash Flow", f"₪{buy_results['total_monthly_cashflow']:,.0f}")

            with col2:
                st.markdown(
                    """<h3 style='
                        color: #fb923c;
                        margin-bottom: 10px;
                        font-size: 24px;
                    '>Rent Scenario</h3>""",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""<div style='
                                    background-color: #fef9c3; 
                                    padding: 15px; 
                                    border-radius: 10px; 
                                    color: #000000;
                                    font-weight: bold;
                                    font-size: 18px;
                                    margin: 10px 0;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                '>
                                    Net Asset Value:<br/>
                                    <span style='font-size: 24px;'>₪{rent_results['nav']:,.0f}</span>
                                </div>""",
                    unsafe_allow_html=True
                )
                st.metric("Total Monthly Cash Flow", f"₪{rent_results['total_monthly_cashflow']:,.0f}")

            # Risk Analysis
            st.subheader("Risk Analysis")
            risk_scenarios = analysis.generate_risk_scenarios()
            st.dataframe(risk_scenarios)

            # Add Year by Year Analysis
            st.subheader("Year by Year Analysis")
            years_df = pd.DataFrame()
            for year in range(analysis.years + 1):
                # Store original years value
                original_years = analysis.years
                analysis.years = year

                # Get results for both scenarios
                buy_results = analysis.calculate_buy_scenario(show_real_values=False)
                rent_results = analysis.calculate_rent_scenario(show_real_values=False)

                # Get mortgage breakdown
                mortgage_breakdown = buy_results.get('mortgage_breakdown', {})
                total_remaining_mortgage = (mortgage_breakdown.get('fixed_balance', 0) +
                                            mortgage_breakdown.get('variable_balance', 0))

                # Add to dataframe
                years_df = pd.concat([years_df, pd.DataFrame({
                    'Year': [year],
                    'Property Value': [buy_results['property_value']],
                    'Remaining Mortgage': [total_remaining_mortgage],
                    'Buy NAV': [buy_results['nav']],
                    'Rent NAV': [rent_results['nav']],
                    'NAV Difference': [buy_results['nav'] - rent_results['nav']]
                })])

                # Restore original years
                analysis.years = original_years

            st.dataframe(years_df.set_index('Year').style.format("₪{:,.0f}"))

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Real Estate Calculator",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()