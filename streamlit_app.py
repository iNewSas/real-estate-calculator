import streamlit as st
import pandas as pd
from calculator import RealEstateInvestmentAnalysis

st.set_page_config(
    page_title="מחשבון השקעות נדל\"ן",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add RTL support with custom CSS
# Add this to your CSS section at the top of streamlit_app.py
st.markdown("""
    <style>
        .element-container, .stMarkdown, .stButton, .stText, .stNumberInput {
            direction: rtl;
            text-align: right;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            text-align: right;
        }
        /* Fix slider container */
        .stSlider {
            direction: ltr !important;  /* Keep slider direction left-to-right */
            padding: 1rem 0;  /* Add some padding */
        }
        /* Fix slider label */
        .stSlider > label {
            direction: rtl !important;
            text-align: right !important;
            display: block !important;
            width: 100% !important;
        }
        /* Adjust slider width */
        .stSlider > div > div {
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)


def main():
    st.title("מחשבון השקעות נדל\"ן")

    # Add description with explicit color and visibility settings
    st.markdown("""
        <div style='
            direction: rtl;
            text-align: right;
            padding: 20px;
            margin: 10px 0;
            border-right: 4px solid #4ade80;
            background-color: #f8fafc;
            border-radius: 5px;
            color: #1f2937;  /* Dark gray color for text */
            font-size: 16px;
            opacity: 1;
            display: block;
            visibility: visible;
            line-height: 1.6;
        '>
            מחשבון זה משמש לצורך חישוב והשוואה בין שתי אלטרנטיבות.<br><br>
            האחת השכרת דירה במרכז וחסכון חודשי קבוע לאורך תקופת ההשקעה. החלופה השנייה מניחה המשך שכירת דירה במרכז אך במקביל כוללת רכישת נכס נדלן בפריפריה.<br><br>
            המחשבון משווה מה קורה להון העצמי במהלך השנים הראשונות ומשווה בין החלופות, ניתן להשתמש בסליידרים ולהכניס ערכים המתאימים למקרים פרטיים, לחישוב תסריטים שונים.
        </div>
    """, unsafe_allow_html=True)


    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("פרטי הנכס")
        property_value = st.number_input(
            "שווי הנכס בקנייה (₪)",
            value=900000,
            step=10000,
            format="%d"
        )
        down_payment_percent = st.slider(
            "הון עצמי המושקע בנכס(%)",
            min_value=0,
            max_value=100,
            value=25
        )
        rental_income = st.number_input(
            "הכנסה חודשית מהשכרת הנכס (₪)",
            value=3500,
            step=100,
            format="%d"
        )
        annual_appreciation_rate = st.number_input(
            "שיעור עליית ערך הנכס בחישוב ממוצע שנתי (%)",
            value=3.5,
            step=0.1,
            format="%.1f"
        )

        st.subheader("פרטי המשכנתא")
        loan_term_years = st.slider(
            "תקופת המשכנתא (שנים)",
            min_value=5,
            max_value=30,
            value=30
        )
        fixed_portion = st.slider(
            "אחוז המשכנתא בריבית קבועה (%)",
            min_value=0,
            max_value=100,
            value=30
        )
        fixed_rate = st.number_input(
            "שיעור הריבית על המשכנתא בריבית קבועה (%)",
            value=5.0,
            step=0.1,
            format="%.1f"
        )
        variable_rate = st.number_input(
            "שיעור הריבית על המשכנתא בריבית המשתנה (%)",
            value=4.5,
            step=0.1,
            format="%.1f"
        )
        prime_base_rate = st.number_input(
            "ריבית פריים (%)",
            value=6.0,
            step=0.1,
            format="%.1f"
        )

    with col2:
        st.subheader("פרמטרים להשקעה")
        years = st.slider(
            "תקופת הניתוח (שנים)",
            min_value=1,
            max_value=30,
            value=10
        )
        central_rent = st.number_input(
            "שכר דירה נוכחי על דירת המגורים במרכז (₪)",
            value=7000,
            step=100,
            format="%d"
        )
        monthly_savings = st.number_input(
            "סכום ההפרשה לחיסכון חודשי (₪)",
            value=0,
            step=100,
            format="%d"
        )
        savings_return_rate = st.number_input(
            "תשואה צפויה על השקעות של ההון העצמי והחסכון החודשי(%)",
            value=7.5,
            step=0.1,
            format="%.1f"
        )
        inflation_rate = st.number_input(
            "שיעור אינפלציה שנתי ממוצע משוער(%)",
            value=2.0,
            step=0.1,
            format="%.1f"
        )

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

    if st.button("חשב"):
        try:
            analysis = RealEstateInvestmentAnalysis(**params)
            buy_results = analysis.calculate_buy_scenario(show_real_values=False)
            rent_results = analysis.calculate_rent_scenario(show_real_values=False)

            st.header("תוצאות")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """<h3 style='
                        color: #4ade80;
                        margin-bottom: 10px;
                        font-size: 24px;
                        text-align: right;
                    '>תרחיש רכישה</h3>""",
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
                        text-align: right;
                    '>
                        שווי נכסי נטו:<br/>
                        <span style='font-size: 24px;'>₪{buy_results['nav']:,.0f}</span>
                    </div>""",
                    unsafe_allow_html=True
                )
                st.metric("הכנ/הוצ' חודשית נטו", f"₪{buy_results['monthly_net_income']:,.0f}")
                st.metric("תזרים מזומנים חודשי", f"₪{buy_results['total_monthly_cashflow']:,.0f}")

            with col2:
                st.markdown(
                    """<h3 style='
                        color: #fb923c;
                        margin-bottom: 10px;
                        font-size: 24px;
                        text-align: right;
                    '>תרחיש שכירות</h3>""",
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
                        text-align: right;
                    '>
                        שווי נכסי נטו:<br/>
                        <span style='font-size: 24px;'>₪{rent_results['nav']:,.0f}</span>
                    </div>""",
                    unsafe_allow_html=True
                )
                st.metric("תזרים מזומנים חודשי", f"₪{rent_results['total_monthly_cashflow']:,.0f}")

            # Risk Analysis
            st.subheader("ניתוח סיכונים")
            risk_scenarios = analysis.generate_risk_scenarios()
            # Translate column names and values
            risk_scenarios.columns = ['תרחיש שוק', 'תיאור', 'שווי נכס סופי', 'שווי נכסי נטו', 'רמת סיכון']
            risk_scenarios['תרחיש שוק'] = risk_scenarios['תרחיש שוק'].replace({
                'Base Case': 'תרחיש בסיס',
                'Market Crash': 'קריסת שוק',
                'Stagnant Market': 'שוק מתון',
                'Strong Market': 'שוק חזק'
            })
            risk_scenarios['רמת סיכון'] = risk_scenarios['רמת סיכון'].replace({
                'Low': 'נמוך',
                'Medium': 'בינוני',
                'High': 'גבוה'
            })
            st.dataframe(risk_scenarios)

            # Year by Year Analysis
            st.subheader("ניתוח שנה אחר שנה")
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
                    'שנה': [year],
                    'שווי הנכס': [buy_results['property_value']],
                    'יתרת משכנתא': [total_remaining_mortgage],
                    'שווי נכסי נטו - רכישה': [buy_results['nav']],
                    'שווי נכסי נטו - שכירות': [rent_results['nav']],
                    'הפרש': [buy_results['nav'] - rent_results['nav']]
                })])

                # Restore original years
                analysis.years = original_years

            # Format as currency and display
            st.markdown("""
                        <style>
                            .dataframe {
                                direction: rtl;
                                text-align: right;
                            }
                            .dataframe th {
                                text-align: right !important;
                            }
                        </style>
                    """, unsafe_allow_html=True)

            # Format numbers with ₪ and thousands separator
            formatted_df = years_df.set_index('שנה').style.format({
                'שווי הנכס': lambda x: f'₪{x:,.0f}',
                'יתרת משכנתא': lambda x: f'₪{x:,.0f}',
                'שווי נכסי נטו - רכישה': lambda x: f'₪{x:,.0f}',
                'שווי נכסי נטו - שכירות': lambda x: f'₪{x:,.0f}',
                'הפרש': lambda x: f'₪{x:,.0f}'
            })

            st.dataframe(formatted_df)

        except Exception as e:
            st.error(f"אירעה שגיאה: {str(e)}")


if __name__ == "__main__":
    main()