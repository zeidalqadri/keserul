"""
Business Development Automation System

A comprehensive automation platform for lead generation, outreach campaigns,
and market research targeting Singapore and Malaysia SME markets.
"""

__version__ = "1.0.0"
__author__ = "Business Development Team"

# Make key components available at package level
try:
    from .system_coordinator import SystemCoordinator
except ImportError:
    # Handle case where dependencies aren't available
    SystemCoordinator = None

__all__ = [
    "SystemCoordinator"
] 