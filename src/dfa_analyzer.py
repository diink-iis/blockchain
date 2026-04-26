"""
DFA (Digital Financial Asset) analyzer module.
Calculates DFA metrics and returns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List
from config import DFA_PARAMS, ANALYSIS_CONFIG


class DFAAnalyzer:
    """
    Analyzes Digital Financial Asset parameters and returns.
    """

    def __init__(self, dfa_params: Dict = None):
        """
        Initialize DFA analyzer with parameters.

        Args:
            dfa_params: Dictionary with DFA parameters (default: from config)
        """
        if dfa_params is None:
            dfa_params = DFA_PARAMS

        self.params = dfa_params
        self.results = {}

    def calculate_time_to_maturity(self) -> float:
        """
        Calculate time to maturity in years.

        Returns:
            Years to maturity
        """
        placement_date = datetime.strptime(self.params['placement_start'], '%Y-%m-%d')
        maturity_date = datetime.strptime(self.params['maturity_date'], '%Y-%m-%d')

        days_to_maturity = (maturity_date - placement_date).days
        years_to_maturity = days_to_maturity / 365.25

        return years_to_maturity

    def calculate_effective_yield(self,
                                 tax_rate: float = None) -> float:
        """
        Calculate effective after-tax yield.

        Args:
            tax_rate: Tax rate (default: from config)

        Returns:
            After-tax yield as percentage
        """
        if tax_rate is None:
            tax_rate = ANALYSIS_CONFIG['tax_dfa']

        pre_tax_yield = self.params['yield_rate']
        after_tax_yield = pre_tax_yield * (1 - tax_rate / 100)

        return after_tax_yield

    def calculate_coupon_payments(self) -> pd.DataFrame:
        """
        Calculate coupon payment schedule.

        Returns:
            DataFrame with coupon payment schedule
        """
        placement_date = datetime.strptime(self.params['placement_start'], '%Y-%m-%d')
        maturity_date = datetime.strptime(self.params['maturity_date'], '%Y-%m-%d')

        face_value = self.params['face_value']
        annual_yield = self.params['yield_rate']
        periods = self.params['coupon_periods']

        # Calculate coupon amount per period
        annual_coupon = face_value * (annual_yield / 100)
        coupon_per_period = annual_coupon / periods

        # Calculate payment dates
        total_days = (maturity_date - placement_date).days
        days_per_period = total_days / periods

        coupon_schedule = []
        payment_date = placement_date

        for i in range(1, periods + 1):
            payment_date = placement_date + timedelta(days=days_per_period * i)

            coupon_schedule.append({
                'period': i,
                'payment_date': payment_date.strftime('%Y-%m-%d'),
                'days_from_placement': int(days_per_period * i),
                'coupon_amount': coupon_per_period,
                'cumulative_coupon': coupon_per_period * i,
            })

        df = pd.DataFrame(coupon_schedule)
        return df

    def calculate_total_return(self) -> Dict[str, float]:
        """
        Calculate total return metrics.

        Returns:
            Dictionary with return metrics
        """
        face_value = self.params['face_value']
        price = self.params['placement_price']
        yield_rate = self.params['yield_rate']
        years = self.calculate_time_to_maturity()

        # Total coupon income
        coupon_schedule = self.calculate_coupon_payments()
        total_coupon = coupon_schedule['coupon_amount'].sum()

        # Capital gain/loss at maturity
        capital_gain = face_value - price

        # Total return in currency
        total_return = total_coupon + capital_gain

        # Total return as percentage
        total_return_pct = (total_return / price) * 100

        # Annualized return
        annualized_return = (total_return_pct / years) if years > 0 else 0

        return {
            'total_coupon': total_coupon,
            'capital_gain': capital_gain,
            'total_return_abs': total_return,
            'total_return_pct': total_return_pct,
            'annualized_return': annualized_return,
            'years_to_maturity': years,
        }

    def calculate_liquidity_adjusted_yield(self,
                                          liquidity_discount: float = None) -> float:
        """
        Calculate yield adjusted for liquidity risk.

        Args:
            liquidity_discount: Liquidity discount in % (default: from config)

        Returns:
            Liquidity-adjusted yield
        """
        if liquidity_discount is None:
            liquidity_discount = ANALYSIS_CONFIG['liquidity_discount_dfa']

        nominal_yield = self.params['yield_rate']
        adjusted_yield = nominal_yield + liquidity_discount

        return adjusted_yield

    def calculate_risk_adjusted_return(self,
                                     risk_free_rate: float = None,
                                     beta: float = 1.2) -> Dict[str, float]:
        """
        Calculate risk-adjusted return metrics.

        Args:
            risk_free_rate: Risk-free rate (default: from config)
            beta: Beta coefficient for DFA (higher than bonds due to illiquidity)

        Returns:
            Dictionary with risk-adjusted metrics
        """
        if risk_free_rate is None:
            risk_free_rate = ANALYSIS_CONFIG['risk_free_rate']

        nominal_yield = self.params['yield_rate']

        # Calculate risk premium
        risk_premium = nominal_yield - risk_free_rate

        # Calculate Sharpe ratio (simplified)
        # In real scenario, would need standard deviation of returns
        excess_return = nominal_yield - risk_free_rate
        # Assume DFA volatility ~15% annual
        volatility = 0.15
        sharpe_ratio = excess_return / (volatility * 100) if volatility > 0 else 0

        return {
            'risk_premium': risk_premium,
            'excess_return': excess_return,
            'sharpe_ratio': sharpe_ratio,
            'beta': beta,
        }

    def get_dfa_summary(self) -> Dict:
        """
        Get comprehensive DFA summary.

        Returns:
            Dictionary with DFA analysis summary
        """
        time_to_maturity = self.calculate_time_to_maturity()
        effective_yield = self.calculate_effective_yield()
        total_return = self.calculate_total_return()
        coupon_schedule = self.calculate_coupon_payments()
        risk_adjusted = self.calculate_risk_adjusted_return()

        summary = {
            'basic_params': self.params,
            'time_metrics': {
                'years_to_maturity': time_to_maturity,
                'days_to_maturity': int(time_to_maturity * 365.25),
            },
            'yield_metrics': {
                'nominal_yield_pct': self.params['yield_rate'],
                'after_tax_yield_pct': effective_yield,
                'liquidity_adjusted_yield_pct': self.calculate_liquidity_adjusted_yield(),
            },
            'return_metrics': total_return,
            'coupon_schedule': coupon_schedule,
            'risk_metrics': risk_adjusted,
        }

        return summary

    def print_summary(self):
        """Print DFA analysis summary."""
        summary = self.get_dfa_summary()

        print("=" * 70)
        print("DFA ANALYSIS SUMMARY")
        print("=" * 70)

        print(f"\nIssuer: {self.params['issuer']}")
        print(f"DFA ID: {self.params['id']}")

        print(f"\n--- Basic Parameters ---")
        print(f"Face Value: {self.params['face_value']:,.2f} ₽")
        print(f"Placement Price: {self.params['placement_price']:,.2f} ₽")
        print(f"Nominal Yield: {self.params['yield_rate']}% p.a.")

        print(f"\n--- Timing ---")
        print(f"Placement: {self.params['placement_start']} - {self.params['placement_end']}")
        print(f"Maturity: {self.params['maturity_date']}")
        print(f"Time to Maturity: {summary['time_metrics']['years_to_maturity']:.2f} years")

        print(f"\n--- Returns ---")
        print(f"Total Coupon: {summary['return_metrics']['total_coupon']:,.2f} ₽")
        print(f"Total Return: {summary['return_metrics']['total_return_pct']:.2f}%")
        print(f"After-tax Yield: {summary['yield_metrics']['after_tax_yield_pct']:.2f}%")

        print(f"\n--- Risk Metrics ---")
        print(f"Risk Premium: {summary['risk_metrics']['risk_premium']:.2f}%")
        print(f"Sharpe Ratio: {summary['risk_metrics']['sharpe_ratio']:.3f}")

        print("\n" + "=" * 70)
