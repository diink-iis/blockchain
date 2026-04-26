"""
Bonds analyzer module.
Analyzes bond parameters and calculates comparable metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from config import ANALYSIS_CONFIG


class BondsAnalyzer:
    """
    Analyzes bond parameters and calculates metrics comparable to DFA.
    """

    def __init__(self, bonds_data: pd.DataFrame):
        """
        Initialize bonds analyzer with bonds data.

        Args:
            bonds_data: DataFrame with bonds information
        """
        self.bonds_data = bonds_data
        self.results = {}

    def calculate_effective_yield(self,
                                 coupon_rate: float,
                                 price: float,
                                 face_value: float,
                                 years_to_maturity: float,
                                 tax_rate: float = None) -> float:
        """
        Calculate effective after-tax yield for a bond.

        Args:
            coupon_rate: Annual coupon rate (%)
            price: Current/Placement price
            face_value: Face value
            years_to_maturity: Years until maturity
            tax_rate: Tax rate (default: from config)

        Returns:
            After-tax yield as percentage
        """
        if tax_rate is None:
            tax_rate = ANALYSIS_CONFIG['tax_bonds']

        # Calculate pre-tax YTM (simplified)
        annual_coupon = face_value * (coupon_rate / 100)
        capital_gain = face_value - price

        total_annual_return = annual_coupon + (capital_gain / years_to_maturity)
        avg_investment = (face_value + price) / 2

        pre_tax_yield = (total_annual_return / avg_investment) * 100

        # Apply tax
        after_tax_yield = pre_tax_yield * (1 - tax_rate / 100)

        return after_tax_yield

    def calculate_liquidity_adjusted_yield(self,
                                         nominal_yield: float,
                                         liquidity_score: float,
                                         liquidity_discount: float = None) -> float:
        """
        Calculate yield adjusted for liquidity.

        Args:
            nominal_yield: Nominal yield
            liquidity_score: Liquidity score (0-1, higher = more liquid)
            liquidity_discount: Base liquidity discount (default: from config)

        Returns:
            Liquidity-adjusted yield
        """
        if liquidity_discount is None:
            liquidity_discount = ANALYSIS_CONFIG['liquidity_discount_bonds']

        # Higher liquidity score → lower discount
        # If liquidity_score = 1, discount = 0
        # If liquidity_score = 0, discount = full liquidity_discount
        actual_discount = liquidity_discount * (1 - liquidity_score)

        adjusted_yield = nominal_yield - actual_discount

        return adjusted_yield

    def calculate_risk_adjusted_metrics(self,
                                       yield_rate: float,
                                       credit_rating: str,
                                       risk_free_rate: float = None) -> Dict:
        """
        Calculate risk-adjusted metrics for a bond.

        Args:
            yield_rate: Bond yield
            credit_rating: Credit rating (e.g., 'BBB', 'B+')
            risk_free_rate: Risk-free rate (default: from config)

        Returns:
            Dictionary with risk-adjusted metrics
        """
        if risk_free_rate is None:
            risk_free_rate = ANALYSIS_CONFIG['risk_free_rate']

        # Credit spread over risk-free
        credit_spread = yield_rate - risk_free_rate

        # Estimate beta based on credit rating
        # Higher quality (AAA/AA) → beta ~0.5
        # Lower quality (B/CCC) → beta ~1.5
        rating_beta_map = {
            'AAA': 0.3, 'AA': 0.4, 'A': 0.5,
            'BBB': 0.7, 'BB': 1.0, 'B': 1.3,
            'CCC': 1.6, 'CC': 1.8, 'C': 2.0,
        }

        # Extract base rating (remove + or -)
        base_rating = credit_rating.replace('+', '').replace('-', '').upper()
        beta = rating_beta_map.get(base_rating, 1.0)

        # Calculate Sharpe ratio (simplified)
        excess_return = yield_rate - risk_free_rate
        # Assume bond volatility ~8% annual for investment grade, 12% for junk
        volatility = 0.08 if base_rating in ['AAA', 'AA', 'A', 'BBB'] else 0.12
        sharpe_ratio = excess_return / (volatility * 100) if volatility > 0 else 0

        return {
            'credit_spread': credit_spread,
            'beta': beta,
            'sharpe_ratio': sharpe_ratio,
            'excess_return': excess_return,
        }

    def analyze_all_bonds(self) -> pd.DataFrame:
        """
        Analyze all bonds and calculate comprehensive metrics.

        Returns:
            DataFrame with analysis results for all bonds
        """
        results = []

        for _, bond in self.bonds_data.iterrows():
            # Extract parameters
            coupon_rate = bond['coupon_rate']
            price = bond.get('placement_price', bond['face_value'])
            face_value = bond['face_value']
            years = bond.get('years_to_maturity', bond['maturity_months'] / 12)

            # Calculate effective yield
            effective_yield = self.calculate_effective_yield(
                coupon_rate, price, face_value, years
            )

            # Calculate liquidity-adjusted yield
            liquidity_score = bond.get('liquidity_score', 0.7)
            liquidity_adjusted_yield = self.calculate_liquidity_adjusted_yield(
                bond['ytm_primary'], liquidity_score
            )

            # Calculate risk-adjusted metrics
            risk_metrics = self.calculate_risk_adjusted_metrics(
                bond['ytm_primary'],
                bond.get('credit_rating', 'B'),
            )

            result = {
                'secid': bond['secid'],
                'name': bond['name'],
                'issuer': bond['issuer'],
                'coupon_rate': coupon_rate,
                'face_value': face_value,
                'placement_price': price,
                'ytm_primary': bond['ytm_primary'],
                'after_tax_yield': effective_yield,
                'liquidity_adjusted_yield': liquidity_adjusted_yield,
                'credit_rating': bond.get('credit_rating', 'B'),
                'liquidity_score': liquidity_score,
                'volume': bond.get('volume', 0),
                'maturity_date': bond['maturity_date'],
                'placement_date': bond['placement_date'],
                'risk_premium': risk_metrics['credit_spread'],
                'sharpe_ratio': risk_metrics['sharpe_ratio'],
                'beta': risk_metrics['beta'],
            }

            results.append(result)

        df = pd.DataFrame(results)
        return df

    def get_summary_statistics(self, analysis_df: pd.DataFrame = None) -> Dict:
        """
        Calculate summary statistics for bonds.

        Args:
            analysis_df: DataFrame with analysis results (default: analyze all)

        Returns:
            Dictionary with summary statistics
        """
        if analysis_df is None:
            analysis_df = self.analyze_all_bonds()

        stats = {
            'count': len(analysis_df),
            'yield_stats': {
                'mean_ytm': analysis_df['ytm_primary'].mean(),
                'median_ytm': analysis_df['ytm_primary'].median(),
                'std_ytm': analysis_df['ytm_primary'].std(),
                'min_ytm': analysis_df['ytm_primary'].min(),
                'max_ytm': analysis_df['ytm_primary'].max(),
            },
            'after_tax_stats': {
                'mean_after_tax': analysis_df['after_tax_yield'].mean(),
                'median_after_tax': analysis_df['after_tax_yield'].median(),
            },
            'risk_stats': {
                'mean_risk_premium': analysis_df['risk_premium'].mean(),
                'mean_sharpe': analysis_df['sharpe_ratio'].mean(),
            },
            'volume_stats': {
                'total_volume': analysis_df['volume'].sum(),
                'mean_volume': analysis_df['volume'].mean(),
            }
        }

        return stats

    def print_summary(self):
        """Print bonds analysis summary."""
        analysis = self.analyze_all_bonds()
        stats = self.get_summary_statistics(analysis)

        print("=" * 70)
        print("BONDS ANALYSIS SUMMARY")
        print("=" * 70)

        print(f"\nTotal Bonds Analyzed: {stats['count']}")

        print(f"\n--- Yield Statistics (Primary Market) ---")
        print(f"Mean YTM: {stats['yield_stats']['mean_ytm']:.2f}%")
        print(f"Median YTM: {stats['yield_stats']['median_ytm']:.2f}%")
        print(f"Std Dev: {stats['yield_stats']['std_ytm']:.2f}%")
        print(f"Range: {stats['yield_stats']['min_ytm']:.2f}% - {stats['yield_stats']['max_ytm']:.2f}%")

        print(f"\n--- After-Tax Yield ---")
        print(f"Mean After-Tax Yield: {stats['after_tax_stats']['mean_after_tax']:.2f}%")
        print(f"Median After-Tax Yield: {stats['after_tax_stats']['median_after_tax']:.2f}%")

        print(f"\n--- Risk Metrics ---")
        print(f"Mean Risk Premium: {stats['risk_stats']['mean_risk_premium']:.2f}%")
        print(f"Mean Sharpe Ratio: {stats['risk_stats']['mean_sharpe']:.3f}")

        print("\n" + "=" * 70)

        print("\nIndividual Bond Details:")
        print(analysis[['secid', 'ytm_primary', 'after_tax_yield', 'sharpe_ratio']].to_string(index=False))
        print("\n" + "=" * 70)
