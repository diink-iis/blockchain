"""
Report generator module for DFA vs Bonds analysis.
Creates presentation slides and summary reports.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List
import os
from config import OUTPUT_CONFIG


class ReportGenerator:
    """
    Generates reports and presentation materials.
    """

    def __init__(self, output_dir: str = None):
        """
        Initialize report generator.

        Args:
            output_dir: Directory for reports (default: from config)
        """
        if output_dir is None:
            output_dir = OUTPUT_CONFIG['reports_dir']

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.timestamp = datetime.now().strftime(OUTPUT_CONFIG['timestamp_format'])

    def generate_markdown_report(self,
                                dfa_summary: Dict,
                                bonds_summary: Dict,
                                comparison_results: Dict,
                                recommendation: Dict) -> str:
        """
        Generate comprehensive markdown report.

        Args:
            dfa_summary: DFA analysis summary
            bonds_summary: Bonds analysis summary
            comparison_results: Comparison results
            recommendation: Investment recommendation

        Returns:
            Path to generated report
        """
        filename = f"dfa_vs_bonds_report_{self.timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Title
            f.write("# DFA vs Bonds: Comparative Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            self._write_executive_summary(f, dfa_summary, bonds_summary, comparison_results, recommendation)

            # DFA Analysis
            f.write("## DFA Analysis\n\n")
            self._write_dfa_analysis(f, dfa_summary)

            # Bonds Analysis
            f.write("## Bonds Analysis\n\n")
            self._write_bonds_analysis(f, bonds_summary)

            # Comparative Analysis
            f.write("## Comparative Analysis\n\n")
            self._write_comparative_analysis(f, comparison_results)

            # Risk Factors
            f.write("## Risk Factors\n\n")
            self._write_risk_factors(f, dfa_summary, bonds_summary)

            # Investment Recommendation
            f.write("## Investment Recommendation\n\n")
            self._write_recommendation(f, recommendation)

            # Conclusion
            f.write("## Conclusion\n\n")
            self._write_conclusion(f, comparison_results, recommendation)

        print(f"Report generated: {filepath}")
        return filepath

    def _write_executive_summary(self, f, dfa_summary, bonds_summary, comparison_results, recommendation):
        """Write executive summary section."""
        f.write("### Key Findings\n\n")

        dfa_yield = dfa_summary['yield_metrics']['nominal_yield_pct']
        avg_bond_yield = bonds_summary['yield_stats']['mean_ytm']
        spread = dfa_yield - avg_bond_yield

        f.write(f"- **DFA Yield:** {dfa_yield:.2f}% p.a.\n")
        f.write(f"- **Average Bond Yield:** {avg_bond_yield:.2f}% p.a.\n")
        f.write(f"- **Spread:** {spread:+.2f} percentage points\n")

        dfa_sharpe = dfa_summary['risk_metrics']['sharpe_ratio']
        avg_bond_sharpe = bonds_summary['risk_stats']['mean_sharpe']

        f.write(f"- **DFA Sharpe Ratio:** {dfa_sharpe:.3f}\n")
        f.write(f"- **Average Bond Sharpe Ratio:** {avg_bond_sharpe:.3f}\n")

        f.write(f"\n### Recommendation\n\n")
        f.write(f"**Overall Preference:** {recommendation['overall_recommendation'].upper()}\n\n")
        f.write(f"{recommendation['reasoning']}\n\n")

    def _write_dfa_analysis(self, f, dfa_summary):
        """Write DFA analysis section."""
        f.write("### DFA Parameters\n\n")

        params = dfa_summary['basic_params']
        f.write(f"- **Issuer:** {params['issuer']}\n")
        f.write(f"- **DFA ID:** {params['id']}\n")
        f.write(f"- **Face Value:** {params['face_value']:,.2f} ₽\n")
        f.write(f"- **Placement Price:** {params['placement_price']:,.2f} ₽\n")
        f.write(f"- **Issue Volume:** {params['issue_volume']:,.0f} ₽\n")
        f.write(f"- **Placement Period:** {params['placement_start']} - {params['placement_end']}\n")
        f.write(f"- **Maturity Date:** {params['maturity_date']}\n\n")

        f.write("### DFA Returns\n\n")
        returns = dfa_summary['return_metrics']
        f.write(f"- **Nominal Yield:** {dfa_summary['yield_metrics']['nominal_yield_pct']:.2f}%\n")
        f.write(f"- **After-Tax Yield:** {dfa_summary['yield_metrics']['after_tax_yield_pct']:.2f}%\n")
        f.write(f"- **Total Coupon Income:** {returns['total_coupon']:,.2f} ₽\n")
        f.write(f"- **Total Return:** {returns['total_return_pct']:.2f}%\n\n")

    def _write_bonds_analysis(self, f, bonds_summary):
        """Write bonds analysis section."""
        f.write(f"### Sample Size\n\n")
        f.write(f"**Total Bonds Analyzed:** {bonds_summary['count']}\n\n")

        f.write("### Yield Statistics\n\n")
        yield_stats = bonds_summary['yield_stats']
        f.write(f"- **Mean YTM:** {yield_stats['mean_ytm']:.2f}%\n")
        f.write(f"- **Median YTM:** {yield_stats['median_ytm']:.2f}%\n")
        f.write(f"- **Std Deviation:** {yield_stats['std_ytm']:.2f}%\n")
        f.write(f"- **Range:** {yield_stats['min_ytm']:.2f}% - {yield_stats['max_ytm']:.2f}%\n\n")

        f.write("### Risk Metrics\n\n")
        risk_stats = bonds_summary['risk_stats']
        f.write(f"- **Mean Risk Premium:** {risk_stats['mean_risk_premium']:.2f}%\n")
        f.write(f"- **Mean Sharpe Ratio:** {risk_stats['mean_sharpe']:.3f}\n\n")

    def _write_comparative_analysis(self, f, comparison_results):
        """Write comparative analysis section."""
        risk_return = comparison_results.get('risk_return_comparison', {})

        if risk_return:
            f.write("### Return Comparison\n\n")
            f.write(f"- **DFA Return:** {risk_return['dfa_return']:.2f}%\n")
            f.write(f"- **Avg Bond Return:** {risk_return['avg_bond_return']:.2f}%\n")
            f.write(f"- **Return Advantage:** {risk_return['return_advantage']:+.2f}%\n\n")

            f.write("### Efficiency Comparison\n\n")
            efficiency = comparison_results.get('efficiency_comparison', {})
            f.write(f"- **DFA Sharpe Ratio:** {efficiency.get('dfa_sharpe', 0):.3f}\n")
            f.write(f"- **Avg Bond Sharpe Ratio:** {efficiency.get('avg_bond_sharpe', 0):.3f}\n")
            f.write(f"- **Sharpe Advantage:** {efficiency.get('sharpe_advantage', 0):+.3f}\n\n")

        # Spread drivers
        f.write("### Spread Drivers\n\n")
        drivers = comparison_results.get('spread_drivers', {})
        for driver, value in drivers.items():
            if driver not in ['total_spread', 'unexplained']:
                f.write(f"- **{driver.replace('_', ' ').title()}:** {value:+.2f}%\n")
        f.write("\n")

    def _write_risk_factors(self, f, dfa_summary, bonds_summary):
        """Write risk factors section."""
        f.write("### DFA-Specific Risks\n\n")
        f.write("**Liquidity Risk:**\n")
        f.write("- DFA market is less liquid than bond market\n")
        f.write("- Limited secondary market activity\n")
        f.write("- Higher bid-ask spreads expected\n\n")

        f.write("**Technology Risk:**\n")
        f.write("- Platform dependency and smart contract risks\n")
        f.write("- Potential operational issues\n")
        f.write("- Cybersecurity threats\n\n")

        f.write("**Regulatory Risk:**\n")
        f.write("- Evolving regulatory framework for digital assets\n")
        f.write("- Potential changes in tax treatment\n")
        f.write("- Uncertainty in legal enforcement\n\n")

        f.write("### Bond-Specific Risks\n\n")
        f.write("**Market Risk:**\n")
        f.write("- Interest rate risk\n")
        f.write("- Credit risk of issuer\n")
        f.write("- Inflation risk\n\n")

    def _write_recommendation(self, f, recommendation):
        """Write investment recommendation section."""
        f.write(f"### Overall Recommendation: {recommendation['overall_recommendation'].upper()}\n\n")
        f.write(f"{recommendation['reasoning']}\n\n")

        f.write("### Investor Profile Recommendations\n\n")
        for profile, advice in recommendation['investor_suggestions'].items():
            f.write(f"**{profile.title()} Investor:**\n")
            f.write(f"- Preferred: {advice['preferred']}\n")
            f.write(f"- Reason: {advice['reason']}\n\n")

    def _write_conclusion(self, f, comparison_results, recommendation):
        """Write conclusion section."""
        f.write("### Key Takeaways\n\n")

        key_factors = recommendation.get('key_factors', {})
        yield_advantage = key_factors.get('yield_advantage', 0)

        if yield_advantage > 0:
            f.write(f"1. **Yield Advantage:** DFA offers {yield_advantage:+.2f}% higher yield ")
            f.write("compared to average bond\n\n")
        else:
            f.write(f"1. **Yield Disadvantage:** DFA offers {yield_advantage:+.2f}% lower yield ")
            f.write("compared to average bond\n\n")

        f.write("2. **Risk-Return Efficiency:** ")
        sharpe_advantage = key_factors.get('sharpe_advantage', 0)
        if sharpe_advantage > 0:
            f.write(f"DFA shows superior risk-adjusted returns (Sharpe: {sharpe_advantage:+.3f})\n\n")
        else:
            f.write(f"Bonds show superior risk-adjusted returns (Sharpe: {sharpe_advantage:+.3f})\n\n")

        f.write("3. **Liquidity Consideration:** Bonds offer significantly better liquidity ")
        f.write("and market depth\n\n")

        f.write("### Final Assessment\n\n")
        f.write("The choice between DFA and bonds depends on investor objectives:\n\n")
        f.write("- **Yield-focused investors** may prefer DFA for higher returns\n")
        f.write("- **Liquidity-focused investors** should choose bonds\n")
        f.write("- **Balanced investors** should consider diversifying across both instruments\n\n")

    def generate_presentation_outline(self) -> str:
        """
        Generate presentation outline for slides.

        Returns:
            Path to generated outline
        """
        filename = f"presentation_outline_{self.timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# DFA vs Bonds: Presentation Outline\n\n")
            f.write("## Slide 1: Title Slide\n\n")
            f.write("- **Title:** Comparative Analysis: DFA vs Bonds\n")
            f.write("- **Subtitle:** Yield, Risk, and Liquidity Assessment\n")
            f.write("- **Date:** [Current Date]\n")
            f.write("- **Author:** [Your Name]\n\n")

            f.write("## Slide 2: Research Objective\n\n")
            f.write("- Compare yield of DFA with comparable bonds\n")
            f.write("- Identify and explain yield spread\n")
            f.write("- Assess risk-return profiles\n")
            f.write("- Provide investment recommendations\n\n")

            f.write("## Slide 3: Methodology\n\n")
            f.write("- **Data Sources:**\n")
            f.write("  - DFA: Platform dfa.sber.ru\n")
            f.write("  - Bonds: Moscow Exchange (MOEX)\n")
            f.write("- **Analysis Period:** April 2026 - May 2027\n")
            f.write("- **Comparison Metrics:**\n")
            f.write("  - Primary market yield\n")
            f.write("  - After-tax yield\n")
            f.write("  - Risk-adjusted return (Sharpe ratio)\n")
            f.write("  - Liquidity impact\n\n")

            f.write("## Slide 4: DFA Overview\n\n")
            f.write("- **Issuer:** ООО 'ЦЕНТР НЕДВИЖИМОСТИ МАЯК'\n")
            f.write("- **Type:** Coupon-bearing digital financial asset\n")
            f.write("- **Yield:** 17% p.a.\n")
            f.write("- **Term:** ~12 months\n")
            f.write("- **Volume:** 50M ₽\n\n")

            f.write("## Slide 5: Comparable Bonds\n\n")
            f.write("- Selection criteria:\n")
            f.write("  - Similar maturity (10-14 months)\n")
            f.write("  - Similar credit quality\n")
            f.write("  - Placement in Q2 2026\n")
            f.write("- Sample: 4 corporate bonds\n\n")

            f.write("## Slide 6: Yield Comparison\n\n")
            f.write("- **[INSERT CHART: Bar chart comparing DFA vs Bond yields]**\n")
            f.write("- DFA: 17.0%\n")
            f.write("- Bonds: 15.9% - 18.5%\n")
            f.write("- Average bond yield: ~17.0%\n\n")

            f.write("## Slide 7: Spread Analysis\n\n")
            f.write("- **[INSERT CHART: Horizontal bar plot of spreads]**\n")
            f.write("- DFA vs individual bonds: -1.5% to +1.1%\n")
            f.write("- Average spread: ~0.0%\n")
            f.write("- Conclusion: DFA yield comparable to bonds\n\n")

            f.write("## Slide 8: Risk-Return Profile\n\n")
            f.write("- **[INSERT CHART: Scatter plot]**\n")
            f.write("- DFA: Higher return, higher risk\n")
            f.write("- Bonds: Varying risk-return profiles\n")
            f.write("- Sharpe ratio comparison\n\n")

            f.write("## Slide 9: Spread Decomposition\n\n")
            f.write("- **[INSERT CHART: Decomposition of spread factors]**\n")
            f.write("- Liquidity component\n")
            f.write("- Technology risk premium\n")
            f.write("- Regulatory uncertainty\n\n")

            f.write("## Slide 10: Risk Factors\n\n")
            f.write("**DFA Risks:**\n")
            f.write("- Limited liquidity\n")
            f.write("- Technology/smart contract risk\n")
            f.write("- Regulatory uncertainty\n\n")
            f.write("**Bond Risks:**\n")
            f.write("- Credit risk\n")
            f.write("- Interest rate risk\n\n")

            f.write("## Slide 11: Investment Recommendation\n\n")
            f.write("- **Conservative:** Bonds (better liquidity)\n")
            f.write("- **Balanced:** DFA (comparable yield, diversification)\n")
            f.write("- **Aggressive:** DFA (higher return potential)\n\n")

            f.write("## Slide 12: Conclusion\n\n")
            f.write("- DFA yield is competitive with bonds\n")
            f.write("- Spread explained by liquidity and risk factors\n")
            f.write("- Choice depends on investor profile\n")
            f.write("- DFA offers diversification benefits\n\n")

            f.write("## Slide 13: Q&A\n\n")

        print(f"Presentation outline generated: {filepath}")
        return filepath

    def generate_excel_report(self,
                            dfa_summary: Dict,
                            bonds_analysis: pd.DataFrame,
                            comparison_results: pd.DataFrame) -> str:
        """
        generate Excel report with multiple sheets.

        Args:
            dfa_summary: DFA analysis summary
            bonds_analysis: Bonds analysis DataFrame
            comparison_results: Comparison results DataFrame

        Returns:
            Path to generated Excel file
        """
        filename = f"dfa_vs_bonds_analysis_{self.timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # DFA Summary sheet
            dfa_data = {
                'Parameter': ['Issuer', 'DFA ID', 'Face Value (₽)', 'Placement Price (₽)',
                            'Yield (%)', 'After-Tax Yield (%)', 'Maturity Date',
                            'Volume (₽)', 'Sharpe Ratio'],
                'Value': [
                    dfa_summary['basic_params']['issuer'],
                    dfa_summary['basic_params']['id'],
                    dfa_summary['basic_params']['face_value'],
                    dfa_summary['basic_params']['placement_price'],
                    dfa_summary['yield_metrics']['nominal_yield_pct'],
                    dfa_summary['yield_metrics']['after_tax_yield_pct'],
                    dfa_summary['basic_params']['maturity_date'],
                    dfa_summary['basic_params']['issue_volume'],
                    dfa_summary['risk_metrics']['sharpe_ratio'],
                ]
            }
            pd.DataFrame(dfa_data).to_excel(writer, sheet_name='DFA Summary', index=False)

            # Bonds Analysis sheet
            bonds_analysis.to_excel(writer, sheet_name='Bonds Analysis', index=False)

            # Comparison sheet
            if isinstance(comparison_results, pd.DataFrame):
                comparison_results.to_excel(writer, sheet_name='Comparison', index=False)

        print(f"Excel report generated: {filepath}")
        return filepath
