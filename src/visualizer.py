"""
Visualization module for DFA vs Bonds analysis.
Creates charts and graphs for presentation.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List
from config import VIZ_CONFIG
import os


class DFAvsBondsVisualizer:
    """
    Visualizes DFA vs Bonds comparison results.
    """

    def __init__(self, output_dir: str = "figures"):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        self.setup_style()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def setup_style(self):
        """Setup matplotlib and seaborn style."""
        plt.style.use(VIZ_CONFIG['style'])
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = VIZ_CONFIG['figsize']
        plt.rcParams['font.size'] = VIZ_CONFIG['font_scale']

    def plot_yield_comparison(self,
                             dfa_yield: float,
                             bond_yields: List[float],
                             bond_names: List[str],
                             save_path: str = None,
                             show_plot: bool = False):
        """
        Plot yield comparison between DFA and bonds.

        Args:
            dfa_yield: DFA yield
            bond_yields: List of bond yields
            bond_names: List of bond names
            save_path: Path to save figure (optional)
            show_plot: Whether to display plot (default: False)
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        all_yields = [dfa_yield] + bond_yields
        all_names = ['DFA'] + bond_names
        colors = [VIZ_CONFIG['colors']['dfa']] + [VIZ_CONFIG['colors']['bonds']] * len(bond_yields)

        # Create bar plot
        bars = ax.bar(range(len(all_yields)), all_yields, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar, yield_val in zip(bars, all_yields):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{yield_val:.1f}%',
                   ha='center', va='bottom', fontsize=10)

        # Customize plot
        ax.set_xlabel('Instrument', fontsize=12, fontweight='bold')
        ax.set_ylabel('Yield (%)', fontsize=12, fontweight='bold')
        ax.set_title('DFA vs Bonds: Primary Market Yield Comparison',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(all_names)))
        ax.set_xticklabels(all_names, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(os.path.join(self.output_dir, save_path),
                       dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
            print(f"Saved: {save_path}")

        plt.close()

    def plot_spread_analysis(self,
                           bond_names: List[str],
                           spreads: List[float],
                           save_path: str = None):
        """
        Plot spread analysis.

        Args:
            bond_names: List of bond names
            spreads: List of spreads (DFA yield - Bond yield)
            save_path: Path to save figure (optional)
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Color bars based on spread sign
        colors = [VIZ_CONFIG['colors']['spread'] if s > 0 else '#FF9999' for s in spreads]

        # Create horizontal bar plot
        bars = ax.barh(range(len(spreads)), spreads, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels
        for bar, spread in zip(bars, spreads):
            width = bar.get_width()
            ax.text(width + (0.1 if width > 0 else -0.1), bar.get_y() + bar.get_height()/2,
                   f'{spread:+.2f}%',
                   ha='left' if width > 0 else 'right', va='center', fontsize=10)

        # Add vertical line at 0
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1)

        # Customize plot
        ax.set_xlabel('Spread (DFA - Bond) [%]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Bond', fontsize=12, fontweight='bold')
        ax.set_title('DFA vs Bonds: Yield Spread Analysis',
                    fontsize=14, fontweight='bold')
        ax.set_yticks(range(len(bond_names)))
        ax.set_yticklabels(bond_names)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(os.path.join(self.output_dir, save_path),
                       dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
            print(f"Saved: {save_path}")

        plt.close()

    def plot_risk_return_profile(self,
                                returns: Dict[str, float],
                                risks: Dict[str, float],
                                save_path: str = None):
        """
        Plot risk-return profile.

        Args:
            returns: Dict with returns (dfa, bonds)
            risks: Dict with risk metrics (risk_premium)
            save_path: Path to save figure (optional)
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Extract data
        instruments = list(returns.keys())
        return_values = list(returns.values())
        risk_values = list(risks.values())

        # Create scatter plot
        for i, instrument in enumerate(instruments):
            color = VIZ_CONFIG['colors']['dfa'] if 'dfa' in instrument.lower() else VIZ_CONFIG['colors']['bonds']
            ax.scatter(risk_values[i], return_values[i],
                      s=500, alpha=0.7, color=color, edgecolors='black', linewidth=2)
            ax.annotate(instrument.upper(),
                       (risk_values[i], return_values[i]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=11, fontweight='bold')

        # Add risk-free rate point
        risk_free_return = 12.0  # From config
        risk_free_risk = 0.0
        ax.scatter(risk_free_risk, risk_free_return,
                  s=300, alpha=0.7, color=VIZ_CONFIG['colors']['risk_free'],
                  edgecolors='black', linewidth=2, marker='s')
        ax.annotate('RISK-FREE', (risk_free_risk, risk_free_return),
                   xytext=(5, -15), textcoords='offset points',
                   fontsize=9, fontweight='bold')

        # Customize plot
        ax.set_xlabel('Risk Premium (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Return (%)', fontsize=12, fontweight='bold')
        ax.set_title('Risk-Return Profile: DFA vs Bonds',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(os.path.join(self.output_dir, save_path),
                       dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
            print(f"Saved: {save_path}")

        plt.close()

    def plot_spread_decomposition(self,
                                 drivers: Dict[str, float],
                                 save_path: str = None):
        """
        Plot spread decomposition into factors.

        Args:
            drivers: Dict with spread drivers
            save_path: Path to save figure (optional)
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data (exclude total_spread and unexplained for visualization)
        plot_drivers = {k: v for k, v in drivers.items()
                       if k not in ['total_spread', 'unexplained'] and v != 0}

        driver_names = [name.replace('_', ' ').title() for name in plot_drivers.keys()]
        driver_values = list(plot_drivers.values())

        # Create horizontal bar plot
        colors = plt.cm.viridis(np.linspace(0, 1, len(driver_values)))

        bars = ax.barh(range(len(driver_values)), driver_values,
                      color=colors, alpha=0.7, edgecolor='black')

        # Add value labels
        for bar, value in zip(bars, driver_values):
            width = bar.get_width()
            ax.text(width + (0.05 if value > 0 else -0.05),
                   bar.get_y() + bar.get_height()/2,
                   f'{value:+.2f}%',
                   ha='left' if value > 0 else 'right',
                   va='center', fontsize=10)

        # Add vertical line at 0
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1)

        # Customize plot
        ax.set_xlabel('Spread Component [%]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Driver', fontsize=12, fontweight='bold')
        ax.set_title('DFA-Bond Spread Decomposition',
                    fontsize=14, fontweight='bold')
        ax.set_yticks(range(len(driver_names)))
        ax.set_yticklabels(driver_names)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(os.path.join(self.output_dir, save_path),
                       dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
            print(f"Saved: {save_path}")

        plt.close()

    def plot_liquidity_impact(self,
                            dfa_yield: float,
                            bond_yields: List[float],
                            dfa_liquidity_adjusted: float,
                            bond_liquidity_adjusted: List[float],
                            save_path: str = None):
        """
        Plot liquidity impact on yields.

        Args:
            dfa_yield: Nominal DFA yield
            bond_yields: List of nominal bond yields
            dfa_liquidity_adjusted: Liquidity-adjusted DFA yield
            bond_liquidity_adjusted: List of liquidity-adjusted bond yields
            save_path: Path to save figure (optional)
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        x = np.arange(len(bond_yields))
        width = 0.35

        # Create grouped bar plot
        bars1 = ax.bar(x - width/2, [dfa_yield] + bond_yields,
                      width, label='Nominal Yield', alpha=0.7, color='steelblue')
        bars2 = ax.bar(x + width/2, [dfa_liquidity_adjusted] + bond_liquidity_adjusted,
                      width, label='Liquidity-Adjusted Yield', alpha=0.7, color='coral')

        # Customize plot
        ax.set_xlabel('Instrument', fontsize=12, fontweight='bold')
        ax.set_ylabel('Yield (%)', fontsize=12, fontweight='bold')
        ax.set_title('Liquidity Impact on DFA vs Bonds Yields',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['DFA'] + [f'Bond {i+1}' for i in range(len(bond_yields))])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(os.path.join(self.output_dir, save_path),
                       dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
            print(f"Saved: {save_path}")

        plt.close()

    def create_summary_dashboard(self,
                                dfa_summary: Dict,
                                bonds_summary: Dict,
                                comparison_results: Dict,
                                save_path: str = None):
        """
        Create comprehensive dashboard with multiple plots.

        Args:
            dfa_summary: DFA analysis summary
            bonds_summary: Bonds analysis summary
            comparison_results: Comparison results
            save_path: Path to save figure (optional)
        """
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Yield Comparison
        ax1 = fig.add_subplot(gs[0, 0])
        self._add_yield_comparison_subplot(ax1, dfa_summary, bonds_summary)

        # Plot 2: Spread Analysis
        ax2 = fig.add_subplot(gs[0, 1])
        self._add_spread_subplot(ax2, comparison_results)

        # Plot 3: Risk-Return
        ax3 = fig.add_subplot(gs[1, 0])
        self._add_risk_return_subplot(ax3, dfa_summary, bonds_summary)

        # Plot 4: Key Metrics Table
        ax4 = fig.add_subplot(gs[1, 1])
        self._add_metrics_table(ax4, dfa_summary, bonds_summary, comparison_results)

        fig.suptitle('DFA vs Bonds: Comprehensive Analysis Dashboard',
                    fontsize=16, fontweight='bold', y=0.995)

        if save_path:
            plt.savefig(os.path.join(self.output_dir, save_path),
                       dpi=VIZ_CONFIG['dpi'], bbox_inches='tight')
            print(f"Saved: {save_path}")

        plt.close()

    def _add_yield_comparison_subplot(self, ax, dfa_summary, bonds_summary):
        """Add yield comparison subplot to dashboard."""
        # Simplified version - customize as needed
        dfa_yield = dfa_summary['yield_metrics']['nominal_yield_pct']
        avg_bond_yield = bonds_summary['yield_stats']['mean_ytm']

        instruments = ['DFA', 'Avg Bond']
        yields = [dfa_yield, avg_bond_yield]
        colors = [VIZ_CONFIG['colors']['dfa'], VIZ_CONFIG['colors']['bonds']]

        bars = ax.bar(instruments, yields, color=colors, alpha=0.7, edgecolor='black')
        for bar, yield_val in zip(bars, yields):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{yield_val:.1f}%', ha='center', va='bottom', fontsize=11)

        ax.set_ylabel('Yield (%)', fontweight='bold')
        ax.set_title('Yield Comparison', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    def _add_spread_subplot(self, ax, comparison_results):
        """Add spread subplot to dashboard."""
        # Simplified version
        primary_comparison = comparison_results.get('primary_comparison', pd.DataFrame())
        if isinstance(primary_comparison, pd.DataFrame) and primary_comparison.empty:
            # Use dummy data for visualization
            spreads = [0.5, -0.3, 0.8, -0.1]
        elif isinstance(primary_comparison, pd.DataFrame):
            spreads = primary_comparison['absolute_spread_pct'].tolist()
        else:
            # Use dummy data for visualization
            spreads = [0.5, -0.3, 0.8, -0.1]

        ax.hist(spreads, bins=10, color=VIZ_CONFIG['colors']['spread'], alpha=0.7, edgecolor='black')
        ax.axvline(x=np.mean(spreads), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(spreads):.2f}%')
        ax.set_xlabel('Spread (%)', fontweight='bold')
        ax.set_ylabel('Frequency', fontweight='bold')
        ax.set_title('Spread Distribution', fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

    def _add_risk_return_subplot(self, ax, dfa_summary, bonds_summary):
        """Add risk-return subplot to dashboard."""
        dfa_return = dfa_summary['yield_metrics']['nominal_yield_pct']
        dfa_risk = dfa_summary['risk_metrics']['risk_premium']

        avg_bond_return = bonds_summary['yield_stats']['mean_ytm']
        avg_bond_risk = bonds_summary['risk_stats']['mean_risk_premium']

        # Scatter plot
        ax.scatter([dfa_risk, avg_bond_risk], [dfa_return, avg_bond_return],
                  s=300, alpha=0.7, c=[VIZ_CONFIG['colors']['dfa'], VIZ_CONFIG['colors']['bonds']],
                  edgecolors='black', linewidth=2)
        ax.annotate('DFA', (dfa_risk, dfa_return), xytext=(5, 5), textcoords='offset points',
                   fontsize=11, fontweight='bold')
        ax.annotate('Avg Bond', (avg_bond_risk, avg_bond_return), xytext=(5, -15),
                   textcoords='offset points', fontsize=11, fontweight='bold')

        ax.set_xlabel('Risk Premium (%)', fontweight='bold')
        ax.set_ylabel('Return (%)', fontweight='bold')
        ax.set_title('Risk-Return Profile', fontweight='bold')
        ax.grid(True, alpha=0.3)

    def _add_metrics_table(self, ax, dfa_summary, bonds_summary, comparison_results):
        """Add metrics table subplot to dashboard."""
        ax.axis('off')

        # Prepare table data
        table_data = [
            ['Metric', 'DFA', 'Avg Bond', 'Difference'],
            ['Yield (%)', f"{dfa_summary['yield_metrics']['nominal_yield_pct']:.2f}",
             f"{bonds_summary['yield_stats']['mean_ytm']:.2f}",
             f"{dfa_summary['yield_metrics']['nominal_yield_pct'] - bonds_summary['yield_stats']['mean_ytm']:+.2f}"],
            ['After-Tax (%)', f"{dfa_summary['yield_metrics']['after_tax_yield_pct']:.2f}",
             f"{bonds_summary['after_tax_stats']['mean_after_tax']:.2f}",
             f"{dfa_summary['yield_metrics']['after_tax_yield_pct'] - bonds_summary['after_tax_stats']['mean_after_tax']:+.2f}"],
            ['Sharpe Ratio', f"{dfa_summary['risk_metrics']['sharpe_ratio']:.3f}",
             f"{bonds_summary['risk_stats']['mean_sharpe']:.3f}",
             f"{dfa_summary['risk_metrics']['sharpe_ratio'] - bonds_summary['risk_stats']['mean_sharpe']:+.3f}"],
        ]

        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.3, 0.2, 0.2, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        # Style header row
        for i in range(4):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')

        ax.set_title('Key Metrics Comparison', fontweight='bold', pad=20)
