"""
Prompt Template Manager for McKinsey-Insights Bot

This module provides functionality to manage, load, and render Jinja templates
for the McKinsey-style market analysis and slide deck generation.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import jinja2
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jinja2"])
    import jinja2


class PromptTemplateManager:
    """
    Manager for loading and rendering Jinja templates for McKinsey-Insights prompts.
    
    This class handles:
    - Loading templates from the prompts directory
    - Rendering templates with variables
    - Managing the conversation flow through phases
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the PromptTemplateManager.
        
        Args:
            templates_dir: Directory containing prompt templates.
                           Defaults to '../prompts' relative to this file.
        """
        if templates_dir is None:
            # Default to the prompts directory in the insights_bot package
            templates_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "prompts"
            )
        
        self.templates_dir = Path(templates_dir)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
    
    def get_template(self, template_name: str) -> jinja2.Template:
        """
        Get a Jinja template by name.
        
        Args:
            template_name: Name of the template file (e.g., 'base_prompt.md')
            
        Returns:
            Jinja Template object
            
        Raises:
            jinja2.exceptions.TemplateNotFound: If template doesn't exist
        """
        return self.env.get_template(template_name)
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a template with the provided variables.
        
        Args:
            template_name: Name of the template file
            variables: Dictionary of variables to inject into the template
            
        Returns:
            Rendered template as a string
        """
        template = self.get_template(template_name)
        return template.render(**variables)
    
    def render_base_prompt(self, variables: Dict[str, Any]) -> str:
        """
        Render the base prompt template with the provided variables.
        
        Args:
            variables: Dictionary containing all required variables:
                - company_name: Name of the company
                - market_segment: Target market segment
                - region: Geographic region for analysis
                - time_period: Time period for analysis
                - primary_color: Primary brand color
                - secondary_color: Secondary brand color
                - deck_title: Title of the slide deck
                
                Optional variables:
                - ceo_question: Specific question from the CEO
                - additional_data_sources: List of additional data sources
                
        Returns:
            Rendered base prompt as a string
        """
        required_vars = [
            "company_name", "market_segment", "region", "time_period",
            "primary_color", "secondary_color", "deck_title"
        ]
        
        # Validate required variables
        missing_vars = [var for var in required_vars if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        return self.render_template("base_prompt.md", variables)
    
    def render_phase(self, phase_number: int, variables: Dict[str, Any]) -> str:
        """
        Render a specific phase template with the provided variables.
        
        Args:
            phase_number: Phase number (2-6)
            variables: Dictionary of variables to inject into the template
            
        Returns:
            Rendered phase template as a string
            
        Raises:
            ValueError: If phase_number is not between 2 and 6
        """
        if not 2 <= phase_number <= 6:
            raise ValueError("Phase number must be between 2 and 6")
        
        # Load the phases template
        phases_template = self.get_template("phases.md")
        
        # Get the macro name for the requested phase
        macro_name = f"phase_{phase_number}"
        
        # Call the macro with the variables
        return phases_template.module.__dict__[macro_name](**variables)
    
    def render_finalization(self, variables: Dict[str, Any]) -> str:
        """
        Render the finalization template with the provided variables.
        
        Args:
            variables: Dictionary of variables to inject into the template
            
        Returns:
            Rendered finalization template as a string
        """
        phases_template = self.get_template("phases.md")
        return phases_template.module.finalization(**variables)
    
    def render_chart_spec(self, variables: Dict[str, Any]) -> str:
        """
        Render a chart specification template with the provided variables.
        
        Args:
            variables: Dictionary containing chart specification:
                - chart_title: Title of the chart
                - chart_type: Type of chart (bar, line, pie, etc.)
                - data_series: List of data series
                - x_axis: X-axis label
                - y_axis: Y-axis label
                - primary_color: Primary color
                - secondary_color: Secondary color
                - include_labels: Whether to include data labels
                - include_legend: Whether to include a legend
                - notes: Additional notes
                - chart_description: Description of the chart
                
        Returns:
            Rendered chart specification as a string
        """
        phases_template = self.get_template("phases.md")
        return phases_template.module.chart_spec(**variables)
    
    def get_available_templates(self) -> List[str]:
        """
        Get a list of available template files.
        
        Returns:
            List of template filenames
        """
        return [f.name for f in self.templates_dir.glob("*.md")] 