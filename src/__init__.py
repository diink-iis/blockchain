"""
DFA vs Bonds: Comparative Analysis Package

Модульная система для сравнительного анализа
цифровых финансовых активов (ЦФА) и облигаций.
"""

__version__ = "1.0.0"
__author__ = "Blockchain Course Project"

from .dfa_analyzer import DFAAnalyzer
from .bonds_analyzer import BondsAnalyzer
from .comparator import DFAvsBondsComparator
from .visualizer import DFAvsBondsVisualizer
from .report_generator import ReportGenerator
from .data_fetcher import BondsDataFetcher, create_sample_bonds_data

__all__ = [
    'DFAAnalyzer',
    'BondsAnalyzer',
    'DFAvsBondsComparator',
    'DFAvsBondsVisualizer',
    'ReportGenerator',
    'BondsDataFetcher',
    'create_sample_bonds_data',
]
