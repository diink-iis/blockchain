"""
Configuration module for DFA vs Bonds analysis project.
Contains all constants and configuration parameters.
"""

# ============================================================================
# DFA PARAMETERS (Digital Financial Asset)
# ============================================================================
DFA_PARAMS = {
    "id": "A1202FB5",
    "name": "денежное требование с купонным доходом",
    "issuer": "ООО 'ЦЕНТР НЕДВИЖИМОСТИ 'МАЯК'",
    "website": "https://new.ural-mayak.ru",

    # Financial parameters
    "face_value": 1000.0,  # ₽
    "placement_price": 1000.0,  # ₽
    "yield_rate": 17.0,  # % annual
    "coupon_type": "fixed",  # fixed/floating
    "coupon_frequency": "quarterly",  # quarterly/monthly/annual
    "coupon_periods": 4,

    # Issue parameters
    "issue_volume": 50_000_000.0,  # ₽ total
    "min_investment": 1000.0,  # ₽
    "min_lot": 1000.0,  # ₽
    "max_lot": 50_000_000.0,  # ₽

    # Dates
    "placement_start": "2026-04-14",
    "placement_end": "2026-04-30",
    "maturity_date": "2027-05-03",
    "distribution_date": "2026-05-04",

    # Terms
    "collateral": "без обеспечения",
    "purpose": "пополнение оборотных средств",
    "investors_count": 73,
}

# ============================================================================
# BONDS SELECTION CRITERIA
# ============================================================================
BONDS_FILTER = {
    # Time criteria
    "maturity_min_months": 10,  # minimum maturity
    "maturity_max_months": 14,  # maximum maturity

    "placement_month_min": "2026-03",  # earliest placement
    "placement_month_max": "2026-05",  # latest placement

    # Credit quality
    "min_credit_rating": "B",  # minimum credit rating

    # Issue size
    "min_issue_volume": 10_000_000.0,  # ₽
    "max_issue_volume": 500_000_000.0,  # ₽
}

# ============================================================================
# DATA SOURCES
# ============================================================================
MOEX_URL = "https://www.moex.com"
MOEX_API_BONDS = "https://iss.moex.com/iss/securities.json"

# ============================================================================
# ANALYSIS PARAMETERS
# ============================================================================
ANALYSIS_CONFIG = {
    # Risk-free rate for comparison
    "risk_free_rate": 12.0,  # % (CBR key rate)

    # Liquidity adjustment
    "liquidity_discount_bonds": 0.5,  # % - premium for liquidity
    "liquidity_discount_dfa": 0.0,  # % - illiquid instrument

    # Tax adjustments
    "tax_bonds": 13.0,  # % - standard tax on coupon income
    "tax_dfa": 13.0,  # % - standard tax on DFA income

    # Comparison thresholds
    "spread_significant": 2.0,  # % - spread considered significant
}

# ============================================================================
# VISUALIZATION CONFIG
# ============================================================================
VIZ_CONFIG = {
    "style": "seaborn-v0_8-darkgrid",
    "figsize": (12, 8),
    "dpi": 300,
    "colors": {
        "dfa": "#FF6B6B",
        "bonds": "#4ECDC4",
        "spread": "#45B7D1",
        "risk_free": "#96CEB4",
    },
    "font_scale": 1.2,
}

# ============================================================================
# OUTPUT CONFIG
# ============================================================================
OUTPUT_CONFIG = {
    "reports_dir": "reports",
    "figures_dir": "figures",
    "data_dir": "data",
    "timestamp_format": "%Y%m%d_%H%M%S",
}
