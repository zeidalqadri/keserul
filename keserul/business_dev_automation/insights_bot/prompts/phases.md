{% macro phase_2(company_name="", market_segment="", region="", time_period="", deck_title="", primary_color="", secondary_color="", ceo_question="", additional_data_sources=[]) %}
## Phase 2: Executive Summary & Key Insights

Based on our initial analysis, here are the key insights for {{ company_name }} regarding {{ market_segment }} in {{ region }}:

1. Market Dynamics: [I'll generate market size, growth rate, and key trends]
2. Competitive Position: [I'll analyze {{ company_name }}'s position relative to competitors]
3. Customer Needs: [I'll identify key customer segments and their unmet needs]
4. Strategic Opportunities: [I'll highlight 2-3 key opportunities for {{ company_name }}]
5. Potential Risks: [I'll identify key risks and mitigation strategies]

I'll now draft the Executive Summary slide with these insights.

Type "continue" when ready to proceed to the next phase.
{% endmacro %}

{% macro phase_3(company_name="", market_segment="", region="", time_period="", deck_title="", primary_color="", secondary_color="", ceo_question="", additional_data_sources=[]) %}
## Phase 3: Market Overview & Competitive Landscape

Now I'll develop detailed slides on:

1. **Market Overview**:
   - Total addressable market (TAM) for {{ market_segment }} in {{ region }}
   - Historical and projected growth rates ({{ time_period }})
   - Key market drivers and inhibitors
   - Regulatory considerations

2. **Competitive Landscape**:
   - Market share breakdown of key players
   - Competitor positioning map (2x2 matrix)
   - Strengths and weaknesses of top 3-5 competitors
   - Recent market moves and strategic shifts

I'll create visualizations including:
- Market size and growth chart
- Competitive positioning matrix
- SWOT analysis for key competitors

Type "continue" when ready to proceed to the next phase.
{% endmacro %}

{% macro phase_4(company_name="", market_segment="", region="", time_period="", deck_title="", primary_color="", secondary_color="", ceo_question="", additional_data_sources=[]) %}
## Phase 4: Customer Analysis & Company Position

Now I'll analyze:

1. **Customer Segments**:
   - Key customer segments in {{ market_segment }}
   - Needs, pain points, and buying criteria by segment
   - Customer journey and decision-making process
   - Willingness to pay and price sensitivity

2. **{{ company_name }}'s Current Position**:
   - Current market share and positioning
   - Key strengths and differentiators
   - Areas for improvement
   - Customer perception and brand equity

I'll create visualizations including:
- Customer segmentation matrix
- Value proposition canvas for key segments
- Competitive advantage assessment

Type "continue" when ready to proceed to the next phase.
{% endmacro %}

{% macro phase_5(company_name="", market_segment="", region="", time_period="", deck_title="", primary_color="", secondary_color="", ceo_question="", additional_data_sources=[]) %}
## Phase 5: Strategic Options & Recommendations

Based on our analysis, I'll now develop:

1. **Strategic Options**:
   - Option 1: [Strategy name] - [Brief description]
   - Option 2: [Strategy name] - [Brief description]
   - Option 3: [Strategy name] - [Brief description]
   
   For each option, I'll assess:
   - Potential impact (market share, revenue)
   - Required investment and timeline
   - Risks and mitigation strategies
   - Alignment with {{ company_name }}'s capabilities

2. **Recommended Strategy**:
   - Clear recommendation with supporting rationale
   - Expected outcomes and KPIs
   - Critical success factors

I'll create visualizations including:
- Strategy evaluation matrix
- Implementation roadmap
- Resource requirements

Type "continue" when ready to proceed to the next phase.
{% endmacro %}

{% macro phase_6(company_name="", market_segment="", region="", time_period="", deck_title="", primary_color="", secondary_color="", ceo_question="", additional_data_sources=[]) %}
## Phase 6: Implementation Plan & Expected Outcomes

Finally, I'll develop:

1. **Implementation Roadmap**:
   - Key phases and milestones
   - Timeline with critical path
   - Resource requirements (people, technology, budget)
   - Governance structure and decision points

2. **Expected Outcomes**:
   - Short-term wins (0-6 months)
   - Medium-term results (6-18 months)
   - Long-term impact (18+ months)
   - Key performance indicators and measurement approach

3. **Next Steps**:
   - Immediate actions (next 30 days)
   - Key decisions required
   - Potential roadblocks and contingency plans

I'll create visualizations including:
- Gantt chart for implementation timeline
- Resource allocation matrix
- KPI dashboard template

Type "finalize" when ready to complete the deck.
{% endmacro %}

{% macro finalization(company_name="", market_segment="", region="", time_period="", deck_title="", primary_color="", secondary_color="", ceo_question="", additional_data_sources=[]) %}
## Finalization: Complete Slide Deck

I've now completed the full McKinsey-style slide deck for {{ company_name }} on {{ market_segment }} in {{ region }}. The deck includes:

1. Title Slide
2. Executive Summary
3. Market Overview
4. Competitive Landscape
5. Customer Analysis
6. {{ company_name }}'s Current Position
7. Strategic Options
8. Recommended Strategy
9. Implementation Roadmap
10. Expected Outcomes
11. Appendix with supporting data

The deck follows McKinsey's best practices:
- Pyramid principle structure (key message first)
- Data-driven insights and recommendations
- Clear, actionable next steps
- Professional visualizations and formatting

Would you like me to:
1. Generate the complete slide deck as a PowerPoint file
2. Focus on specific sections for further refinement
3. Add additional analyses to the appendix
{% endmacro %}

{% macro chart_spec() %}
## Chart Specification

For the {{ chart_title }} chart:

- **Chart Type**: {{ chart_type }}
- **Data Series**:
  {% for series in data_series %}
  - {{ series.name }}: {{ series.values }}
  {% endfor %}
- **X-Axis**: {{ x_axis }}
- **Y-Axis**: {{ y_axis }}
- **Colors**: Primary: {{ primary_color }}, Secondary: {{ secondary_color }}
- **Labels**: {{ include_labels }}
- **Legend**: {{ include_legend }}
- **Notes**: {{ notes }}

{{ chart_description }}
{% endmacro %} 