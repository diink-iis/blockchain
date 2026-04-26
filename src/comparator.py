"""
Comparator module for DFA vs Bonds analysis.
Performs comparative analysis and calculates spreads.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from config import DFA_PARAMS, ANALYSIS_CONFIG


class DFAvsBondsComparator:
    """
    Compares DFA parameters with comparable bonds.
    """

    def __init__(self, dfa_analyzer, bonds_analyzer):
        """
        Initialize comparator.

        Args:
            dfa_analyzer: DFAAnalyzer instance
            bonds_analyzer: BondsAnalyzer instance
        """
        self.dfa = dfa_analyzer
        self.bonds = bonds_analyzer
        self.comparison_results = {}

    def calculate_spread(self,
                        dfa_yield: float,
                        bond_yield: float) -> Dict[str, float]:
        """
        Calculate spread between DFA and bond yields.

        Args:
            dfa_yield: DFA yield
            bond_yield: Bond yield

        Returns:
            Dictionary with spread metrics
        """
        absolute_spread = dfa_yield - bond_yield
        relative_spread = (dfa_yield / bond_yield - 1) * 100 if bond_yield != 0 else 0

        return {
            'absolute_spread_bps': absolute_spread * 100,  # basis points
            'absolute_spread_pct': absolute_spread,
            'relative_spread_pct': relative_spread,
        }

    def compare_primary_market_yields(self) -> pd.DataFrame:
        """
        Compare DFA yield with bond yields on primary market.

        Returns:
            DataFrame with comparison results
        """
        dfa_summary = self.dfa.get_dfa_summary()
        bonds_analysis = self.bonds.analyze_all_bonds()

        dfa_yield = dfa_summary['yield_metrics']['nominal_yield_pct']

        comparisons = []

        for _, bond in bonds_analysis.iterrows():
            spread = self.calculate_spread(dfa_yield, bond['ytm_primary'])

            comparison = {
                'bond_secid': bond['secid'],
                'bond_name': bond['name'],
                'dfa_yield': dfa_yield,
                'bond_yield': bond['ytm_primary'],
                'absolute_spread_pct': spread['absolute_spread_pct'],
                'relative_spread_pct': spread['relative_spread_pct'],
                'is_significant': abs(spread['absolute_spread_pct']) > ANALYSIS_CONFIG['spread_significant'],
                'bond_credit_rating': bond['credit_rating'],
                'bond_volume': bond['volume'],
                'bond_liquidity_score': bond['liquidity_score'],
            }

            comparisons.append(comparison)

        df = pd.DataFrame(comparisons)
        return df

    def compare_after_tax_yields(self) -> pd.DataFrame:
        """
        Compare after-tax yields.

        Returns:
            DataFrame with after-tax comparison
        """
        dfa_summary = self.dfa.get_dfa_summary()
        bonds_analysis = self.bonds.analyze_all_bonds()

        dfa_after_tax = dfa_summary['yield_metrics']['after_tax_yield_pct']

        comparisons = []

        for _, bond in bonds_analysis.iterrows():
            spread = self.calculate_spread(dfa_after_tax, bond['after_tax_yield'])

            comparison = {
                'bond_secid': bond['secid'],
                'dfa_after_tax': dfa_after_tax,
                'bond_after_tax': bond['after_tax_yield'],
                'after_tax_spread': spread['absolute_spread_pct'],
                'tax_advantage_dfa': spread['absolute_spread_pct'] > 0,
            }

            comparisons.append(comparison)

        df = pd.DataFrame(comparisons)
        return df

    def analyze_liquidity_impact(self) -> Dict:
        """
        Analyze how liquidity affects the spread.

        Returns:
            Dictionary with liquidity impact analysis
        """
        dfa_summary = self.dfa.get_dfa_summary()
        bonds_analysis = self.bonds.analyze_all_bonds()

        dfa_liquidity_yield = dfa_summary['yield_metrics']['liquidity_adjusted_yield_pct']

        # Average liquidity-adjusted yield for bonds
        avg_bond_liquidity_yield = bonds_analysis['liquidity_adjusted_yield'].mean()

        # Calculate liquidity spread
        liquidity_spread = dfa_liquidity_yield - avg_bond_liquidity_yield

        return {
            'dfa_liquidity_adjusted_yield': dfa_liquidity_yield,
            'avg_bond_liquidity_adjusted_yield': avg_bond_liquidity_yield,
            'liquidity_spread': liquidity_spread,
            'dfa_illiquidity_premium': ANALYSIS_CONFIG['liquidity_discount_dfa'],
            'avg_bond_illiquidity_discount': bonds_analysis['liquidity_score'].mean() *
                                               ANALYSIS_CONFIG['liquidity_discount_bonds'],
        }

    def analyze_risk_return_profile(self) -> Dict:
        """
        Compare risk-return profiles.

        Returns:
            Dictionary with risk-return analysis
        """
        dfa_summary = self.dfa.get_dfa_summary()
        bonds_analysis = self.bonds.analyze_all_bonds()

        # DFA metrics
        dfa_return = dfa_summary['yield_metrics']['nominal_yield_pct']
        dfa_risk_premium = dfa_summary['risk_metrics']['risk_premium']
        dfa_sharpe = dfa_summary['risk_metrics']['sharpe_ratio']

        # Bond metrics (average)
        avg_bond_return = bonds_analysis['ytm_primary'].mean()
        avg_bond_risk_premium = bonds_analysis['risk_premium'].mean()
        avg_bond_sharpe = bonds_analysis['sharpe_ratio'].mean()

        return {
            'return_comparison': {
                'dfa_return': dfa_return,
                'avg_bond_return': avg_bond_return,
                'return_advantage': dfa_return - avg_bond_return,
            },
            'risk_comparison': {
                'dfa_risk_premium': dfa_risk_premium,
                'avg_bond_risk_premium': avg_bond_risk_premium,
                'risk_premium_diff': dfa_risk_premium - avg_bond_risk_premium,
            },
            'efficiency_comparison': {
                'dfa_sharpe': dfa_sharpe,
                'avg_bond_sharpe': avg_bond_sharpe,
                'sharpe_advantage': dfa_sharpe - avg_bond_sharpe,
            },
        }

    def identify_spread_drivers(self) -> Dict[str, float]:
        """
        Identify key drivers of the DFA-Bond spread.

        Returns:
            Dictionary with spread drivers and their impact
        """
        primary_comparison = self.compare_primary_market_yields()
        liquidity_impact = self.analyze_liquidity_impact()

        avg_spread = primary_comparison['absolute_spread_pct'].mean()

        # Decompose spread into factors
        drivers = {
            'total_spread': avg_spread,
            'liquidity_component': liquidity_impact['liquidity_spread'],
            'credit_component': 0.0,  # Would need credit rating data for DFA
            'technology_component': 0.5,  # Estimated DFA platform risk premium
            'regulatory_component': 0.3,  # Estimated regulatory uncertainty premium
            'unexplained': avg_spread - liquidity_impact['liquidity_spread'] - 0.8,
        }

        return drivers

    def generate_investment_recommendation(self) -> Dict:
        """
        Generate investment recommendation based on analysis.

        Returns:
            Dictionary with recommendation
        """
        risk_return = self.analyze_risk_return_profile()
        spread_drivers = self.identify_spread_drivers()

        dfa_sharpe = risk_return['efficiency_comparison']['dfa_sharpe']
        avg_bond_sharpe = risk_return['efficiency_comparison']['avg_bond_sharpe']

        # Simple decision logic
        if dfa_sharpe > avg_bond_sharpe:
            recommendation = "DFA offers better risk-adjusted returns"
            preference = "DFA"
        else:
            recommendation = "Bonds offer better risk-adjusted returns"
            preference = "Bonds"

        # Consider investor profile
        suggestions = {
            'conservative': {
                'preferred': 'Bonds',
                'reason': 'Higher liquidity, established market, lower regulatory risk',
            },
            'balanced': {
                'preferred': preference,
                'reason': recommendation,
            },
            'aggressive': {
                'preferred': 'DFA',
                'reason': 'Higher yield potential, diversification benefit',
            }
        }

        return {
            'overall_recommendation': preference,
            'reasoning': recommendation,
            'investor_suggestions': suggestions,
            'key_factors': {
                'yield_advantage': risk_return['return_comparison']['return_advantage'],
                'sharpe_advantage': risk_return['efficiency_comparison']['sharpe_advantage'],
                'liquidity_disadvantage': spread_drivers['liquidity_component'],
            }
        }

    def print_comparison_report(self):
        """Print comprehensive comparison report."""
        print("\n" + "=" * 70)
        print("DFA vs BONDS COMPARATIVE ANALYSIS")
        print("=" * 70)

        # Primary market comparison
        print("\n--- PRIMARY MARKET YIELD COMPARISON ---")
        primary = self.compare_primary_market_yields()
        print(primary[['bond_secid', 'dfa_yield', 'bond_yield', 'absolute_spread_pct']].to_string(index=False))

        print(f"\nAverage Spread: {primary['absolute_spread_pct'].mean():.2f}%")
        print(f"Significant Spreads: {primary['is_significant'].sum()} out of {len(primary)}")

        # Liquidity impact
        print("\n--- LIQUIDITY IMPACT ANALYSIS ---")
        liquidity = self.analyze_liquidity_impact()
        print(f"DFA Liquidity-Adjusted Yield: {liquidity['dfa_liquidity_adjusted_yield']:.2f}%")
        print(f"Avg Bond Liquidity-Adjusted Yield: {liquidity['avg_bond_liquidity_adjusted_yield']:.2f}%")
        print(f"Liquidity Spread: {liquidity['liquidity_spread']:.2f}%")

        # Risk-Return profile
        print("\n--- RISK-RETURN PROFILE ---")
        risk_return = self.analyze_risk_return_profile()
        print(f"DFA Return: {risk_return['return_comparison']['dfa_return']:.2f}%")
        print(f"Avg Bond Return: {risk_return['return_comparison']['avg_bond_return']:.2f}%")
        print(f"Return Advantage: {risk_return['return_comparison']['return_advantage']:.2f}%")
        print(f"\nDFA Sharpe: {risk_return['efficiency_comparison']['dfa_sharpe']:.3f}")
        print(f"Avg Bond Sharpe: {risk_return['efficiency_comparison']['avg_bond_sharpe']:.3f}")

        # Spread drivers
        print("\n--- SPREAD DRIVERS ---")
        drivers = self.identify_spread_drivers()
        for driver, value in drivers.items():
            print(f"{driver.replace('_', ' ').title()}: {value:.2f}%")

        # Recommendation
        print("\n--- INVESTMENT RECOMMENDATION ---")
        recommendation = self.generate_investment_recommendation()
        print(f"Overall: {recommendation['overall_recommendation']}")
        print(f"Reasoning: {recommendation['reasoning']}")

        print("\n" + "=" * 70)
