"""
Search Strategy Module

This module implements fallback strategies for entity extraction when initial
searches yield insufficient results. It provides multi-pass search logic and
alternative search term generation.

Architecture: This is used by the API to enhance agent instructions, not to
replace agent functionality. The agent still does the actual searching.
"""
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SearchStrategy:
    """
    Search strategy generator for entity extraction
    
    Provides fallback strategies when initial searches fail:
    1. Multi-pass search (broader → narrower)
    2. Alternative search terms
    3. Language-specific strategies
    """
    
    @staticmethod
    def analyze_topic(topic: str) -> Dict[str, Any]:
        """
        Analyze topic to determine search strategy
        
        Args:
            topic: Research topic
            
        Returns:
            Dictionary with topic analysis:
            - language: Detected language (de, en, mixed)
            - specificity: Level of specificity (broad, medium, specific, very_specific)
            - domain: Topic domain (government, social, technical, general)
            - has_year: Whether topic includes a specific year
            - has_location: Whether topic includes a location
        """
        topic_lower = topic.lower()
        
        # Detect language
        german_indicators = ['ä', 'ö', 'ü', 'ß', 'baden-württemberg', 'deutschland']
        has_german = any(ind in topic_lower for ind in german_indicators)
        has_english = bool(re.search(r'\b(the|and|of|in|for|to)\b', topic_lower))
        
        if has_german and not has_english:
            language = "de"
        elif has_english and not has_german:
            language = "en"
        else:
            language = "mixed"
        
        # Detect specificity
        word_count = len(topic.split())
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', topic))
        
        if word_count <= 2 and not has_year:
            specificity = "broad"
        elif word_count <= 4 and not has_year:
            specificity = "medium"
        elif has_year or word_count > 6:
            specificity = "very_specific"
        else:
            specificity = "specific"
        
        # Detect domain
        government_terms = ['ministerium', 'ministry', 'gesetz', 'law', 'policy', 'politik', 
                           'regierung', 'government', 'behörde', 'agency']
        social_terms = ['armut', 'poverty', 'sozial', 'social', 'integration', 'jugend', 
                       'youth', 'kinder', 'children', 'familie', 'family']
        technical_terms = ['wasserstoff', 'hydrogen', 'netz', 'network', 'technik', 
                          'technology', 'infrastruktur', 'infrastructure']
        
        if any(term in topic_lower for term in government_terms):
            domain = "government"
        elif any(term in topic_lower for term in social_terms):
            domain = "social"
        elif any(term in topic_lower for term in technical_terms):
            domain = "technical"
        else:
            domain = "general"
        
        # Detect location
        locations = ['baden-württemberg', 'bayern', 'hessen', 'deutschland', 'germany', 
                    'europe', 'eu', 'berlin', 'münchen', 'stuttgart']
        has_location = any(loc in topic_lower for loc in locations)
        
        return {
            "language": language,
            "specificity": specificity,
            "domain": domain,
            "has_year": has_year,
            "has_location": has_location
        }
    
    @staticmethod
    def generate_alternative_terms(topic: str, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate alternative search terms for fallback searches
        
        Args:
            topic: Original research topic
            analysis: Topic analysis from analyze_topic()
            
        Returns:
            List of alternative search terms (broader to narrower)
        """
        alternatives = []
        
        # Strategy 1: Remove year for very specific topics
        if analysis["has_year"]:
            topic_without_year = re.sub(r'\b(19|20)\d{2}\b', '', topic).strip()
            alternatives.append(topic_without_year)
            logger.info(f"Alternative (no year): {topic_without_year}")
        
        # Strategy 2: Broaden by removing modifiers
        # Remove adjectives and specific qualifiers
        if analysis["specificity"] in ["specific", "very_specific"]:
            # Remove words like "Lagebericht", "Sachstand", "Report", "Analysis"
            report_terms = ['lagebericht', 'sachstand', 'report', 'analysis', 'bericht', 
                           'studie', 'study', 'übersicht', 'overview']
            broader_topic = topic
            for term in report_terms:
                broader_topic = re.sub(rf'\b{term}\b', '', broader_topic, flags=re.IGNORECASE)
            broader_topic = broader_topic.strip()
            if broader_topic != topic and broader_topic:
                alternatives.append(broader_topic)
                logger.info(f"Alternative (broader): {broader_topic}")
        
        # Strategy 3: Focus on core concept
        # Extract main noun phrases
        words = topic.split()
        if len(words) > 3:
            # Take first 2-3 meaningful words
            core_words = [w for w in words if len(w) > 3][:3]
            core_topic = ' '.join(core_words)
            if core_topic != topic:
                alternatives.append(core_topic)
                logger.info(f"Alternative (core): {core_topic}")
        
        # Strategy 4: Add context for very broad topics
        if analysis["specificity"] == "broad":
            if analysis["language"] == "de":
                alternatives.append(f"{topic} Deutschland")
                alternatives.append(f"{topic} Organisationen")
            else:
                alternatives.append(f"{topic} organizations")
                alternatives.append(f"{topic} officials")
        
        # Strategy 5: Domain-specific alternatives
        if analysis["domain"] == "government" and analysis["language"] == "de":
            # Add "Ministerium" or "Behörde" to help find government entities
            alternatives.append(f"{topic} Ministerium")
            alternatives.append(f"{topic} Behörde")
        elif analysis["domain"] == "social" and analysis["language"] == "de":
            # Add "NGO" or "Verein" to help find organizations
            alternatives.append(f"{topic} NGO")
            alternatives.append(f"{topic} Verein")
        
        # Remove duplicates and empty strings
        alternatives = [alt.strip() for alt in alternatives if alt.strip()]
        alternatives = list(dict.fromkeys(alternatives))  # Remove duplicates, preserve order
        
        return alternatives
    
    @staticmethod
    def generate_multi_pass_instructions(
        topic: str,
        analysis: Dict[str, Any],
        alternatives: List[str]
    ) -> str:
        """
        Generate instructions for multi-pass search strategy
        
        Args:
            topic: Original research topic
            analysis: Topic analysis
            alternatives: Alternative search terms
            
        Returns:
            Instructions string for agent
        """
        instructions = f"""
MULTI-PASS SEARCH STRATEGY:

Your initial search for "{topic}" may yield limited results. If so, try these fallback strategies:

TOPIC ANALYSIS:
- Language: {analysis['language'].upper()}
- Specificity: {analysis['specificity']}
- Domain: {analysis['domain']}
- Has specific year: {'Yes' if analysis['has_year'] else 'No'}
- Has location: {'Yes' if analysis['has_location'] else 'No'}

FALLBACK SEARCH TERMS (try in order if initial search yields <3 entities):
"""
        
        for i, alt in enumerate(alternatives, 1):
            instructions += f"{i}. \"{alt}\"\n"
        
        instructions += """
SEARCH STRATEGY:
1. Start with the original topic
2. If you find <3 entities, try the first alternative term
3. If still <3 entities, try the next alternative term
4. Continue until you find sufficient entities or exhaust alternatives
5. Combine results from all successful searches

WHEN TO USE ALTERNATIVES:
- Initial search returns 0 entities → Try alternative 1
- Initial search returns 1-2 entities → Try alternative 1, combine results
- Initial search returns 3+ entities → No need for alternatives

IMPORTANT:
- Always try at least 2 search terms before giving up
- Combine entities from multiple searches (deduplicate by name)
- Prefer more specific entities over generic ones
- Always include real source URLs
"""
        
        return instructions
    
    @staticmethod
    def generate_helpful_feedback(
        topic: str,
        analysis: Dict[str, Any],
        entity_count: int
    ) -> str:
        """
        Generate helpful feedback when no entities are found
        
        Args:
            topic: Research topic
            analysis: Topic analysis
            entity_count: Number of entities extracted
            
        Returns:
            Helpful feedback message
        """
        if entity_count == 0:
            feedback = f"No entities found for topic: {topic}\n\n"
            feedback += "Possible reasons:\n"
            
            if analysis["specificity"] == "very_specific":
                feedback += "- Topic is very specific (includes year or many qualifiers)\n"
                feedback += "  → Try a broader search without the year or specific qualifiers\n"
            
            if analysis["language"] == "de":
                feedback += "- Topic is in German, which may have limited online sources\n"
                feedback += "  → Try searching for related English terms or broader German topics\n"
            
            if analysis["domain"] == "technical":
                feedback += "- Technical topics may have limited entity-rich content\n"
                feedback += "  → Try searching for organizations or officials in this domain\n"
            
            if analysis["has_location"]:
                feedback += "- Regional topics may have limited coverage\n"
                feedback += "  → Try searching without the specific location\n"
            
            feedback += "\nSuggestions:\n"
            alternatives = SearchStrategy.generate_alternative_terms(topic, analysis)
            for alt in alternatives[:3]:
                feedback += f"- Try searching: \"{alt}\"\n"
            
        elif entity_count < 3:
            feedback = f"Only {entity_count} entity(ies) found for topic: {topic}\n\n"
            feedback += "This is a low number. Consider:\n"
            feedback += "- Trying broader search terms\n"
            feedback += "- Searching for related organizations or officials\n"
            feedback += "- Checking if the topic has sufficient online coverage\n"
        else:
            feedback = f"Found {entity_count} entities for topic: {topic}\n"
            feedback += "This is a good result!"
        
        return feedback
    
    @staticmethod
    def enhance_agent_instructions(
        topic: str,
        base_instructions: str
    ) -> str:
        """
        Enhance agent instructions with fallback strategies
        
        Args:
            topic: Research topic
            base_instructions: Base agent instructions
            
        Returns:
            Enhanced instructions with fallback strategies
        """
        # Analyze topic
        analysis = SearchStrategy.analyze_topic(topic)
        
        # Generate alternatives
        alternatives = SearchStrategy.generate_alternative_terms(topic, analysis)
        
        # Generate multi-pass instructions
        if alternatives:
            multi_pass = SearchStrategy.generate_multi_pass_instructions(
                topic, analysis, alternatives
            )
            
            # Insert multi-pass instructions before output format
            enhanced = base_instructions
            if "OUTPUT FORMAT" in enhanced:
                parts = enhanced.split("OUTPUT FORMAT")
                enhanced = parts[0] + multi_pass + "\n\nOUTPUT FORMAT" + parts[1]
            else:
                enhanced = base_instructions + "\n\n" + multi_pass
            
            logger.info(f"Enhanced instructions with {len(alternatives)} alternative search terms")
            return enhanced
        else:
            logger.info("No alternative search terms generated")
            return base_instructions


# Convenience functions for use in other modules

def analyze_topic(topic: str) -> Dict[str, Any]:
    """Analyze topic to determine search strategy"""
    return SearchStrategy.analyze_topic(topic)


def generate_alternative_terms(topic: str) -> List[str]:
    """Generate alternative search terms"""
    analysis = SearchStrategy.analyze_topic(topic)
    return SearchStrategy.generate_alternative_terms(topic, analysis)


def enhance_instructions(topic: str, base_instructions: str) -> str:
    """Enhance agent instructions with fallback strategies"""
    return SearchStrategy.enhance_agent_instructions(topic, base_instructions)


def generate_feedback(topic: str, entity_count: int) -> str:
    """Generate helpful feedback based on results"""
    analysis = SearchStrategy.analyze_topic(topic)
    return SearchStrategy.generate_helpful_feedback(topic, analysis, entity_count)
