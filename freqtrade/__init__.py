"""
Freqtrade Integration for Enhanced Elliott Wave Analyzer

This package provides Freqtrade strategies and helper functions for
Elliott Wave pattern detection and trading.

Available Strategies:
- SimpleElliotWaveStrategy: Beginner-friendly, fixed parameters
- EnhancedElliotWaveStrategy: Advanced, optimizable parameters

Helper Module:
- elliott_wave_helpers: Utility functions for indicator conversion
"""

__version__ = "2.0.0"
__author__ = "Enhanced Elliott Wave Analyzer"

from .elliott_wave_helpers import FreqtradeElliotWaveHelper

__all__ = [
    'FreqtradeElliotWaveHelper',
]
