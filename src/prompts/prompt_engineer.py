from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PromptEngineer:
    """Dynamic prompt engineering for different analysis types and content."""
    
    def __init__(self):
        self.prompt_templates = {
            "themes": {
                "base": """Analyze the themes and motifs in the following works:
{works}

Focus on:
1. Core themes and their development
2. Symbolism and allegory
3. Philosophical implications
4. Social commentary
5. Moral questions

Provide a detailed comparative analysis.""",
                "enhanced": """As an expert in literary analysis, examine the themes and motifs in these works:
{works}

Consider:
1. Core themes and their evolution
2. Symbolic elements and their significance
3. Philosophical underpinnings
4. Social and cultural commentary
5. Ethical dilemmas and moral questions
6. Historical context and relevance
7. Impact on the genre

Provide a comprehensive comparative analysis with specific examples."""
            },
            "world_building": {
                "base": """Analyze the world-building elements in these works:
{works}

Focus on:
1. Setting consistency and depth
2. Cultural development
3. Technological/magical systems
4. Political structures
5. Environmental factors

Provide a detailed comparative analysis.""",
                "enhanced": """As a world-building expert, examine these works:
{works}

Consider:
1. Setting consistency and depth
2. Cultural systems and development
3. Technological/magical frameworks
4. Political and social structures
5. Environmental and ecological factors
6. Historical context and evolution
7. Impact on the genre

Provide a comprehensive comparative analysis with specific examples."""
            },
            "characters": {
                "base": """Analyze the character development in these works:
{works}

Focus on:
1. Character arcs and growth
2. Relationships and dynamics
3. Motivations and conflicts
4. Archetypes and roles
5. Impact on the story

Provide a detailed comparative analysis.""",
                "enhanced": """As a character analysis expert, examine these works:
{works}

Consider:
1. Character arcs and development
2. Relationships and interpersonal dynamics
3. Motivations and internal conflicts
4. Archetypes and their subversion
5. Impact on narrative and themes
6. Historical and cultural context
7. Influence on the genre

Provide a comprehensive comparative analysis with specific examples."""
            },
            "plot": {
                "base": """Analyze the plot structure in these works:
{works}

Focus on:
1. Narrative techniques
2. Pacing and tension
3. Conflict resolution
4. Story arcs
5. Climax and resolution

Provide a detailed comparative analysis.""",
                "enhanced": """As a narrative structure expert, examine these works:
{works}

Consider:
1. Narrative techniques and style
2. Pacing and tension building
3. Conflict development and resolution
4. Story arcs and their integration
5. Climax and resolution effectiveness
6. Historical context and influence
7. Impact on the genre

Provide a comprehensive comparative analysis with specific examples."""
            }
        }
    
    def format_work(self, work: Dict[str, Any]) -> str:
        """Format a work for inclusion in the prompt."""
        parts = []
        if "title" in work:
            parts.append(f"Title: {work['title']}")
        if "author" in work:
            parts.append(f"Author: {work['author']}")
        if "year" in work:
            parts.append(f"Year: {work['year']}")
        if "content" in work:
            parts.append(f"Content: {work['content']}")
        return "\n".join(parts)
    
    def generate_prompt(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str,
        enhanced: bool = False,
        historical_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a dynamic prompt based on the analysis type and content."""
        if analysis_type not in self.prompt_templates:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        # Format works for the prompt
        formatted_works = "\n\n".join(self.format_work(work) for work in works)
        
        # Select template based on enhancement level
        template = self.prompt_templates[analysis_type]["enhanced" if enhanced else "base"]
        
        # Add historical context if provided
        if historical_context:
            context_str = "\nHistorical Context:\n"
            for key, value in historical_context.items():
                context_str += f"{key}: {value}\n"
            template = template.replace("{works}", f"{formatted_works}\n{context_str}")
        else:
            template = template.replace("{works}", formatted_works)
        
        return template
    
    def get_available_analysis_types(self) -> List[str]:
        """Get list of available analysis types."""
        return list(self.prompt_templates.keys()) 