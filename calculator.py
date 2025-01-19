import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import webbrowser
import tempfile
import os
from datetime import datetime as dt


class MortgageLoan:
    def __init__(self, loan_amount, interest_rate, term_years, is_fixed=True, prime_spread=0):
        self.loan_amount = loan_amount
        self.base_interest_rate = interest_rate
        self.term_years = term_years
        self.is_fixed = is_fixed
        self.prime_spread = prime_spread
        self.monthly_payment = self._calculate_initial_payment()

    def _calculate_initial_payment(self):
        n = self.term_years * 12
        r = self.base_interest_rate / 12 / 100
        return self.loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    def get_payment_at_year(self, year, inflation_rate, prime_base_rate):
        if self.is_fixed:
            return self.monthly_payment
        else:
            # For variable rate: prime + spread
            # Prime typically follows inflation plus some base rate
            effective_rate = (prime_base_rate + inflation_rate + self.prime_spread) / 12 / 100
            remaining_term = (self.term_years - year) * 12
            remaining_balance = self._calculate_remaining_balance(year)

            if remaining_term <= 0:
                return 0

            return (remaining_balance * (effective_rate * (1 + effective_rate) ** remaining_term) /
                    ((1 + effective_rate) ** remaining_term - 1))

    def _calculate_remaining_balance(self, year):
        n = self.term_years * 12
        t = year * 12
        r = self.base_interest_rate / 12 / 100
        if t >= n:
            return 0
        return self.loan_amount * ((1 + r) ** n - (1 + r) ** t) / ((1 + r) ** n - 1)


class RealEstateInvestmentAnalysis:
    def __init__(self, property_value, down_payment_percent, fixed_rate, variable_rate,
                 loan_term_years, rental_income, annual_appreciation_rate, years,
                 central_rent, monthly_savings, savings_return_rate, inflation_rate=0,
                 fixed_portion=30, prime_base_rate=3.5):
        # Initial parameters
        self.property_value = property_value
        self.down_payment_percent = down_payment_percent
        self.fixed_rate = fixed_rate
        self.variable_rate = variable_rate
        self.loan_term_years = loan_term_years
        self.rental_income = rental_income
        self.annual_appreciation_rate = annual_appreciation_rate
        self.years = years
        self.central_rent = central_rent
        self.monthly_savings = monthly_savings
        self.savings_return_rate = savings_return_rate
        self.inflation_rate = inflation_rate
        self.fixed_portion = fixed_portion
        self.prime_base_rate = prime_base_rate

        # Calculate loan amounts
        self.down_payment = property_value * (down_payment_percent / 100)
        self.loan_amount = property_value - self.down_payment  # Add this for HTML report compatibility
        self.fixed_loan_amount = self.loan_amount * (fixed_portion / 100)
        self.variable_loan_amount = self.loan_amount * ((100 - fixed_portion) / 100)

        # Create loan objects
        self.fixed_loan = MortgageLoan(
            self.fixed_loan_amount,
            fixed_rate,
            loan_term_years,
            is_fixed=True
        )
        self.variable_loan = MortgageLoan(
            self.variable_loan_amount,
            variable_rate,
            loan_term_years,
            is_fixed=False,
            prime_spread=variable_rate - prime_base_rate
        )

    def _calculate_total_mortgage_payment(self, year):
        """Calculate total mortgage payment for a given year, considering both loans"""
        fixed_payment = self.fixed_loan.get_payment_at_year(year, self.inflation_rate, self.prime_base_rate)
        variable_payment = self.variable_loan.get_payment_at_year(year, self.inflation_rate, self.prime_base_rate)
        return fixed_payment + variable_payment

    def _calculate_remaining_balance(self, year):
        """Calculate total remaining balance for both loans"""
        fixed_balance = self.fixed_loan._calculate_remaining_balance(year)
        variable_balance = self.variable_loan._calculate_remaining_balance(year)
        return fixed_balance + variable_balance

    def _calculate_inflation_adjusted_value(self, nominal_value, years):
        """Calculate real (inflation-adjusted) value"""
        return nominal_value / ((1 + self.inflation_rate / 100) ** years)

    def _calculate_inflated_income_stream(self, monthly_amount, years):
        """Calculate sum of income stream adjusted for inflation each year"""
        total = 0
        for year in range(years):
            yearly_amount = monthly_amount * 12 * ((1 + self.inflation_rate / 100) ** year)
            total += yearly_amount
        return total

    def calculate_buy_scenario(self, property_value_change=0, show_real_values=False):
        """Calculate complete buying scenario metrics with inflation adjustment"""
        # Nominal calculations
        current_value = self.property_value * (1 + property_value_change / 100)
        nominal_future_value = current_value * (1 + self.annual_appreciation_rate / 100) ** self.years

        remaining_balance = self._calculate_remaining_balance(self.years)
        final_monthly_payment = self._calculate_total_mortgage_payment(self.years - 1)

        # Calculate final year's rental income for monthly cash flow
        final_year_monthly_rental = self.rental_income * ((1 + self.inflation_rate / 100) ** (self.years - 1))
        final_year_monthly_central_rent = self.central_rent * ((1 + self.inflation_rate / 100) ** (self.years - 1))

        nominal_monthly_net_income = final_year_monthly_rental - final_monthly_payment
        nominal_nav = nominal_future_value - remaining_balance

        current_ltv = (remaining_balance / nominal_future_value) * 100
        default_risk = "High" if current_ltv > 90 else "Medium" if current_ltv > 80 else "Low"

        result = {
            'property_value': {
                'nominal': nominal_future_value,
                'real': self._calculate_inflation_adjusted_value(nominal_future_value, self.years)
            },
            'remaining_balance': {
                'nominal': remaining_balance,
                'real': remaining_balance  # Mortgage balance is not adjusted for inflation
            },
            'nav': {
                'nominal': nominal_nav,
                'real': self._calculate_inflation_adjusted_value(nominal_nav, self.years)
            },
            'mortgage_payment': {
                'nominal': final_monthly_payment,
                'real': self._calculate_inflation_adjusted_value(final_monthly_payment, self.years)
            },
            'rental_income': {
                'nominal': final_year_monthly_rental,
                'real': self._calculate_inflation_adjusted_value(final_year_monthly_rental, self.years)
            },
            'monthly_net_income': {
                'nominal': nominal_monthly_net_income,
                'real': self._calculate_inflation_adjusted_value(nominal_monthly_net_income, self.years)
            },
            'central_rent': {
                'nominal': final_year_monthly_central_rent,
                'real': self._calculate_inflation_adjusted_value(final_year_monthly_central_rent, self.years)
            },
            'total_monthly_cashflow': {
                'nominal': -(final_year_monthly_central_rent + abs(nominal_monthly_net_income)),
                'real': -self._calculate_inflation_adjusted_value(
                    final_year_monthly_central_rent + abs(nominal_monthly_net_income),
                    self.years
                )
            },
            'ltv': current_ltv,
            'default_risk': default_risk,
            'mortgage_breakdown': {
                'fixed_payment': self.fixed_loan.get_payment_at_year(self.years - 1, self.inflation_rate,
                                                                     self.prime_base_rate),
                'variable_payment': self.variable_loan.get_payment_at_year(self.years - 1, self.inflation_rate,
                                                                           self.prime_base_rate),
                'fixed_balance': self.fixed_loan._calculate_remaining_balance(self.years),
                'variable_balance': self.variable_loan._calculate_remaining_balance(self.years)
            }
        }

        # Format results
        formatted_results = {}
        for k, v in result.items():
            if isinstance(v, dict) and 'nominal' in v and 'real' in v:
                formatted_results[k] = v['real'] if show_real_values else v['nominal']
            elif k == 'mortgage_breakdown':
                formatted_results[k] = v  # Keep mortgage breakdown as is
            else:
                formatted_results[k] = v
        return formatted_results

    def calculate_rent_scenario(self, show_real_values=False):
        """Calculate renting scenario metrics with inflation adjustment"""
        # Calculate nominal future value of monthly savings with inflation-adjusted contributions
        total_savings = self._calculate_inflated_income_stream(
            self.monthly_savings,
            self.years
        )

        nominal_future_savings = total_savings * (1 + self.savings_return_rate / 100) ** self.years

        # Calculate nominal future value of down payment investment
        nominal_future_down_payment = self.down_payment * (1 + self.savings_return_rate / 100) ** self.years

        # Calculate final year's monthly rent for cash flow
        final_year_monthly_rent = self.central_rent * ((1 + self.inflation_rate / 100) ** (self.years - 1))
        final_year_monthly_savings = self.monthly_savings * ((1 + self.inflation_rate / 100) ** (self.years - 1))

        result = {
            'future_monthly_savings': {
                'nominal': nominal_future_savings,
                'real': self._calculate_inflation_adjusted_value(nominal_future_savings, self.years)
            },
            'future_down_payment': {
                'nominal': nominal_future_down_payment,
                'real': self._calculate_inflation_adjusted_value(nominal_future_down_payment, self.years)
            },
            'nav': {
                'nominal': nominal_future_savings + nominal_future_down_payment,
                'real': self._calculate_inflation_adjusted_value(
                    nominal_future_savings + nominal_future_down_payment,
                    self.years
                )
            },
            'monthly_rent': {
                'nominal': final_year_monthly_rent,
                'real': self._calculate_inflation_adjusted_value(final_year_monthly_rent, self.years)
            },
            'monthly_savings': {
                'nominal': final_year_monthly_savings,
                'real': self._calculate_inflation_adjusted_value(final_year_monthly_savings, self.years)
            },
            'total_monthly_cashflow': {
                'nominal': -(final_year_monthly_rent + final_year_monthly_savings),
                'real': -self._calculate_inflation_adjusted_value(
                    final_year_monthly_rent + final_year_monthly_savings,
                    self.years
                )
            }
        }

        # Format results
        formatted_results = {}
        for k, v in result.items():
            if isinstance(v, dict) and 'nominal' in v and 'real' in v:
                formatted_results[k] = v['real'] if show_real_values else v['nominal']
            else:
                formatted_results[k] = v
        return formatted_results

    def generate_risk_scenarios(self, show_real_values=False):
        """Generate different market scenarios for risk analysis"""
        base_appreciation = self.annual_appreciation_rate

        scenarios = [
            {
                'name': 'Base Case',
                'description': f'Normal market conditions ({base_appreciation}% annual growth)',
                'value_change': 0,
                'growth_rate': base_appreciation
            },
            {
                'name': 'Market Crash',
                'description': f'Immediate 20% drop, slow recovery ({base_appreciation - 1}% annual growth)',
                'value_change': -20,
                'growth_rate': base_appreciation - 1
            },
            {
                'name': 'Stagnant Market',
                'description': f'No initial drop, but slow growth ({base_appreciation - 1}% annual growth)',
                'value_change': 0,
                'growth_rate': base_appreciation - 1
            },
            {
                'name': 'Strong Market',
                'description': f'5% initial gain, strong growth ({base_appreciation + 1}% annual growth)',
                'value_change': 5,
                'growth_rate': base_appreciation + 1
            }
        ]

        results = []
        original_appreciation = self.annual_appreciation_rate

        for scenario in scenarios:
            self.annual_appreciation_rate = scenario['growth_rate']
            result = self.calculate_buy_scenario(scenario['value_change'], show_real_values)

            results.append({
                'Market Scenario': scenario['name'],
                'Description': scenario['description'],
                'Final Property Value': result['property_value'],
                'Net Asset Value': result['nav'],
                'Risk Level': result['default_risk']
            })

        self.annual_appreciation_rate = original_appreciation
        return pd.DataFrame(results)


def format_currency(value):
    """Format number as currency string without ₪ sign"""
    return f"{abs(value):,.0f}"

def format_percent(value):
    """Format number as percentage string"""
    return f"{value:.1f}%"

def get_color_class(value):
    """Return CSS class based on value"""
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    return ""

def get_trend_icon(value):
    """Return trend icon based on value"""
    if value > 0:
        return "↑"
    elif value < 0:
        return "↓"
    return "→"


def generate_yearly_comparison(analysis, show_real_values=False):
    """Generate yearly comparison data for both scenarios"""

    def get_year_data(year):
        """Calculate data for a specific year"""
        # Store original years value
        original_years = analysis.years
        analysis.years = year

        # Get results for both scenarios
        buy_results = analysis.calculate_buy_scenario(show_real_values=show_real_values)
        rent_results = analysis.calculate_rent_scenario(show_real_values=show_real_values)

        # Get mortgage breakdown
        mortgage_breakdown = buy_results.get('mortgage_breakdown', {})
        total_remaining_mortgage = (mortgage_breakdown.get('fixed_balance', 0) +
                                    mortgage_breakdown.get('variable_balance', 0))

        # Calculate difference
        nav_difference = buy_results['nav'] - rent_results['nav']

        # Restore original years
        analysis.years = original_years

        return {
            'property_value': buy_results['property_value'],
            'total_mortgage': total_remaining_mortgage,
            'buy_nav': buy_results['nav'],
            'rent_nav': rent_results['nav'],
            'nav_difference': nav_difference
        }

    # Generate HTML table
    table_rows = ""
    for year in range(analysis.years + 1):  # Include year 0
        data = get_year_data(year)
        nav_difference_class = "positive" if data['nav_difference'] > 0 else "negative"

        table_rows += f"""
        <tr>
            <td class="text-center">{year}</td>
            <td class="text-right">₪ {format_currency(data['property_value'])}</td>
            <td class="text-right negative">-₪ {format_currency(data['total_mortgage'])}</td>
            <td class="text-right">₪ {format_currency(data['buy_nav'])}</td>
            <td class="text-right">₪ {format_currency(data['rent_nav'])}</td>
            <td class="text-right {nav_difference_class}">₪ {format_currency(data['nav_difference'])}</td>
        </tr>
        """

    table_html = f"""
    <div class="card">
        <h2>Year by Year Analysis</h2>
        <table class="table yearly-comparison">
            <thead>
                <tr>
                    <th rowspan="2">Year</th>
                    <th colspan="3">Scenario 1: Buy Suburban Property</th>
                    <th>Scenario 2: Rent + Invest</th>
                    <th rowspan="2">NAV Difference<br/>(Buy - Rent)</th>
                </tr>
                <tr>
                    <th>Property Value</th>
                    <th>Remaining Mortgage</th>
                    <th>Net Asset Value</th>
                    <th>Net Asset Value</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """

    return table_html

def generate_html_report(analysis, show_real_values=False):
    """Generate HTML report with all analysis results"""
    value_type = "Real" if show_real_values else "Nominal"

    style_section = """
    <style>
        body { font-size: 19.2px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .card.buy { border-left: 4px solid #3b82f6; }
        .card.rent { border-left: 4px solid #22c55e; }
        .table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        .table td, .table th { border: 1px solid #e5e7eb; padding: 12px; }
        .table th { background-color: #f9fafb; }
        .text-right { text-align: right; }
        .positive { color: #16a34a; }
        .negative { color: #dc2626; }
        h1 { font-size: 2.4em; margin-bottom: 24px; }
        h2 { color: #1f2937; margin-bottom: 20px; font-size: 1.92em; }
        h3 { color: #374151; margin-bottom: 16px; font-size: 1.32em; }
        .disclaimer { 
            color: #374151; 
            font-style: italic; 
            margin-bottom: 16px; 
            font-size: 1.1em;
        }
        .highlight {
            background-color: #fef9c3;
        }
        .yearly-comparison th { 
            background-color: #f8fafc;
            text-align: center;
            padding: 12px;
        }
        .yearly-comparison td {
            padding: 8px 12px;
        }
    </style>
    """

    buy_results = analysis.calculate_buy_scenario(show_real_values=show_real_values)
    rent_results = analysis.calculate_rent_scenario(show_real_values=show_real_values)
    risk_scenarios = analysis.generate_risk_scenarios(show_real_values=show_real_values)

    params_html = f"""
    <div class="card">
        <h2>Input Parameters</h2>
        <div class="disclaimer">
            All monetary values are in {value_type} Israeli Shekels (₪)<br>
            {f'Inflation Rate: {analysis.inflation_rate}% per year' if analysis.inflation_rate > 0 else 'No inflation adjustment'}
        </div>
        <div class="grid-2">
            <!-- Property Parameters -->
            <div>
                <h3>Property Parameters</h3>
                <table class="table">
                    <tr>
                        <td>Property Value</td>
                        <td class="text-right">₪ {format_currency(analysis.property_value)}</td>
                    </tr>
                    <tr>
                        <td>Down Payment</td>
                        <td class="text-right">{analysis.down_payment_percent}%</td>
                    </tr>
                    <tr>
                        <td>Rental Income</td>
                        <td class="text-right">₪ {format_currency(analysis.rental_income)}/month</td>
                    </tr>
                    <tr>
                        <td>Expected Property Appreciation</td>
                        <td class="text-right">{analysis.annual_appreciation_rate}%/year</td>
                    </tr>
                </table>
            </div>

            <!-- Loan Parameters -->
            <div>
                <h3>Loan Parameters</h3>
                <table class="table">
                    <tr>
                        <td>Total Loan Amount</td>
                        <td class="text-right">₪ {format_currency(analysis.loan_amount)}</td>
                    </tr>
                    <tr>
                        <td>Fixed Rate Portion ({analysis.fixed_portion}%)</td>
                        <td class="text-right">₪ {format_currency(analysis.fixed_loan_amount)}</td>
                    </tr>
                    <tr>
                        <td>Variable Rate Portion ({100 - analysis.fixed_portion}%)</td>
                        <td class="text-right">₪ {format_currency(analysis.variable_loan_amount)}</td>
                    </tr>
                    <tr>
                        <td>Fixed Interest Rate</td>
                        <td class="text-right">{analysis.fixed_rate}%</td>
                    </tr>
                    <tr>
                        <td>Prime Rate</td>
                        <td class="text-right">{analysis.prime_base_rate}%</td>
                    </tr>
                    <tr>
                        <td>Variable Interest Rate</td>
                        <td class="text-right">Prime + {analysis.variable_rate - analysis.prime_base_rate}%</td>
                    </tr>
                    <tr>
                        <td>Loan Term</td>
                        <td class="text-right">{analysis.loan_term_years} years</td>
                    </tr>
                </table>
            </div>

            <!-- Investment Parameters -->
            <div>
                <h3>Investment Parameters</h3>
                <table class="table">
                    <tr>
                        <td>Analysis Period</td>
                        <td class="text-right">{analysis.years} years</td>
                    </tr>
                    <tr>
                        <td>Initial Investment (Down Payment)</td>
                        <td class="text-right">₪ {format_currency(analysis.down_payment)}</td>
                    </tr>
                    <tr>
                        <td>Expected Investment Return</td>
                        <td class="text-right">{analysis.savings_return_rate}%/year</td>
                    </tr>
                </table>
            </div>

            <!-- Current Living Parameters -->
            <div>
                <h3>Current Living Parameters</h3>
                <table class="table">
                    <tr>
                        <td>Current Central Rent</td>
                        <td class="text-right">₪ {format_currency(analysis.central_rent)}/month</td>
                    </tr>
                    <tr>
                        <td>Monthly Investment Capacity</td>
                        <td class="text-right">₪ {format_currency(analysis.monthly_savings)}/month</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
    """

    # Generate scenario sections
    buy_scenario = generate_buy_scenario_html(analysis, buy_results)
    rent_scenario = generate_rent_scenario_html(analysis, rent_results)

    # Generate yearly comparison table
    yearly_comparison = generate_yearly_comparison(analysis, show_real_values)

    # Final HTML assembly
    html = f"""
    {style_section}
    <div class="container">
        <h1>Real Estate Investment Analysis</h1>

        {params_html}

        <div class="grid">
            {buy_scenario}
            {rent_scenario}
        </div>

        <!-- Risk Scenarios -->
        <div class="card">
            <h2>Risk Scenarios Analysis</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Market Scenario</th>
                        <th>Description</th>
                        <th class="text-right">Final Property Value</th>
                        <th class="text-right">Net Asset Value</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {risk_scenarios.apply(lambda row: f'''
                    <tr>
                        <td>{row['Market Scenario']}</td>
                        <td>{row['Description']}</td>
                        <td class="text-right">₪ {format_currency(row['Final Property Value'])}</td>
                        <td class="text-right">₪ {format_currency(row['Net Asset Value'])}</td>
                        <td>{row['Risk Level']}</td>
                    </tr>
                    ''', axis=1).str.cat(sep='')}
                </tbody>
            </table>
        </div>

        <!-- Yearly Comparison -->
        {yearly_comparison}

        <!-- Key Observations -->
        <div class="card">
            <h2>Key Observations</h2>
            <ul>
                <li>Both scenarios include the current central rent payment of ₪ {format_currency(analysis.central_rent)}</li>
                <li>Buy scenario requires an additional ₪ {format_currency(abs(buy_results['monthly_net_income']))} monthly (difference between mortgage payments and rental income)</li>
                <li>Rent + Invest scenario requires ₪ {format_currency(analysis.monthly_savings)} monthly investment</li>
                <li>Final NAV is {format_currency(abs(buy_results['nav'] - rent_results['nav']))} {'higher' if buy_results['nav'] > rent_results['nav'] else 'lower'} in the {'Buy' if buy_results['nav'] > rent_results['nav'] else 'Rent'} scenario</li>
                <li>Variable rate portion ({100 - analysis.fixed_portion}% of mortgage) is sensitive to changes in inflation and interest rates</li>
            </ul>
        </div>
    </div>
    """

    return html


def generate_buy_scenario_html(analysis, buy_results):
    """Generate HTML for buy scenario section"""
    mortgage_breakdown = buy_results.get('mortgage_breakdown', {})

    return f"""
    <div class="card buy">
        <h2>Scenario 1: Buy Suburban Property</h2>

        <h3>Net Asset Value (After {analysis.years} Years)</h3>
        <table class="table">
            <tr>
                <td>Property Value</td>
                <td class="text-right positive">₪ {format_currency(buy_results['property_value'])}</td>
            </tr>
            <tr>
                <td>Remaining Fixed-Rate Mortgage</td>
                <td class="text-right negative">-₪ {format_currency(mortgage_breakdown.get('fixed_balance', 0))}</td>
            </tr>
            <tr>
                <td>Remaining Variable-Rate Mortgage</td>
                <td class="text-right negative">-₪ {format_currency(mortgage_breakdown.get('variable_balance', 0))}</td>
            </tr>
            <tr class="highlight">
                <td><strong>Final Net Asset Value</strong></td>
                <td class="text-right"><strong>₪ {format_currency(buy_results['nav'])}</strong></td>
            </tr>
        </table>

        <h3>Monthly Cash Flow</h3>
        <table class="table">
            <tr>
                <td colspan="2"><strong>Current Living Expenses</strong></td>
            </tr>
            <tr>
                <td>Central Rent Payment</td>
                <td class="text-right negative">-₪ {format_currency(analysis.central_rent)}</td>
            </tr>
            <tr>
                <td colspan="2"><strong>Investment Property</strong></td>
            </tr>
            <tr>
                <td>Fixed-Rate Mortgage Payment</td>
                <td class="text-right negative">-₪ {format_currency(mortgage_breakdown.get('fixed_payment', 0))}</td>
            </tr>
            <tr>
                <td>Variable-Rate Mortgage Payment</td>
                <td class="text-right negative">-₪ {format_currency(mortgage_breakdown.get('variable_payment', 0))}</td>
            </tr>
            <tr>
                <td>Rental Income</td>
                <td class="text-right positive">₪ {format_currency(buy_results['rental_income'])}</td>
            </tr>
            <tr>
                <td>Net Investment Cash Flow</td>
                <td class="text-right {get_color_class(buy_results['monthly_net_income'])}">
                    ₪ {format_currency(buy_results['monthly_net_income'])}
                </td>
            </tr>
            <tr class="highlight">
                <td><strong>Total Monthly Cash Flow</strong></td>
                <td class="text-right negative"><strong>₪ {format_currency(buy_results['total_monthly_cashflow'])}</strong></td>
            </tr>
        </table>
    </div>
    """

def generate_rent_scenario_html(analysis, rent_results):
    """Generate HTML for rent scenario section"""
    return f"""
    <div class="card rent">
        <h2>Scenario 2: Rent + Invest</h2>

        <h3>Net Asset Value (After {analysis.years} Years)</h3>
        <table class="table">
            <tr>
                <td>Future Value of Monthly Savings</td>
                <td class="text-right positive">₪ {format_currency(rent_results['future_monthly_savings'])}</td>
            </tr>
            <tr>
                <td>Future Value of Down Payment Investment</td>
                <td class="text-right positive">₪ {format_currency(rent_results['future_down_payment'])}</td>
            </tr>
            <tr class="highlight">
                <td><strong>Final Net Asset Value</strong></td>
                <td class="text-right"><strong>₪ {format_currency(rent_results['nav'])}</strong></td>
            </tr>
        </table>

        <h3>Monthly Cash Flow</h3>
        <table class="table">
            <tr>
                <td colspan="2"><strong>Current Living Expenses</strong></td>
            </tr>
            <tr>
                <td>Central Rent Payment</td>
                <td class="text-right negative">-₪ {format_currency(analysis.central_rent)}</td>
            </tr>
            <tr>
                <td colspan="2"><strong>Investment Strategy</strong></td>
            </tr>
            <tr>
                <td>Monthly Investment</td>
                <td class="text-right negative">-₪ {format_currency(analysis.monthly_savings)}</td>
            </tr>
            <tr class="highlight">
                <td><strong>Total Monthly Cash Flow</strong></td>
                <td class="text-right negative"><strong>₪ {format_currency(rent_results['total_monthly_cashflow'])}</strong></td>
            </tr>
        </table>
    </div>
    """


def display_report_in_browser(analysis, show_real_values=False):
    """Generate HTML report and display it in the default browser"""
    report = generate_html_report(analysis, show_real_values)
    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
    value_type = "real" if show_real_values else "nominal"
    temp_path = os.path.join(tempfile.gettempdir(),
                             f'real_estate_analysis_{value_type}_{timestamp}.html')

    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(report)

    webbrowser.open('file://' + os.path.realpath(temp_path))
    return temp_path


def main():
    # Input parameters
    params = {
        'property_value': 900000,
        'down_payment_percent': 25,
        'fixed_rate': 5.0,  # Fixed portion rate
        'variable_rate': 4.5,  # Initial variable rate
        'loan_term_years': 30,
        'rental_income': 3500,
        'annual_appreciation_rate': 3.5,
        'years': 10,
        'central_rent': 7000,
        'monthly_savings': 0,
        'savings_return_rate': 7.5,
        'inflation_rate': 2,
        'fixed_portion': 30,  # 30% fixed, 70% variable
        'prime_base_rate': 6
    }

    # Create analysis object
    analysis = RealEstateInvestmentAnalysis(**params)

    # Display both nominal and real value reports
    nominal_path = display_report_in_browser(analysis, show_real_values=False)
    real_path = display_report_in_browser(analysis, show_real_values=True)

    print(f"Analysis complete. Two reports have been generated:")
    print(f"1. Nominal values report: {nominal_path}")
    print(f"2. Real (inflation-adjusted) values report: {real_path}")


if __name__ == "__main__":
    main()