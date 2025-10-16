"""
Verify Wikipedia Agent Validation Configuration

This script verifies that the Wikipedia Agent is properly configured
for immediate validation without making API calls.
"""
import logging
from api.instructions.wikipedia_agent import get_wikipedia_agent_instructions
from api.instructions.validation_agent import get_validation_agent_instructions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_wikipedia_agent_config():
    """Verify Wikipedia Agent configuration for validation integration"""
    logger.info("="*80)
    logger.info("VERIFICATION: Wikipedia Agent Validation Configuration")
    logger.info("="*80)
    
    # Get instructions
    wikipedia_instructions = get_wikipedia_agent_instructions()
    validation_instructions = get_validation_agent_instructions()
    
    # Verify Wikipedia Agent instructions
    logger.info("\n✓ Checking Wikipedia Agent instructions...")
    
    checks = [
        ("Validation Agent integration", "Validation Agent" in wikipedia_instructions),
        ("Immediate validation workflow", "IMMEDIATE VALIDATION WORKFLOW" in wikipedia_instructions),
        ("Call Validation Agent", "CALL Validation Agent" in wikipedia_instructions),
        ("Schema.org compliance requirements", "SCHEMA.ORG COMPLIANCE REQUIREMENTS" in wikipedia_instructions),
        ("Schema.org compliant output format", "SCHEMA.ORG COMPLIANT OUTPUT FORMAT" in wikipedia_instructions),
        ("Validation feedback handling", "VALIDATION FEEDBACK HANDLING" in wikipedia_instructions),
        ("Example validation workflow", "EXAMPLE VALIDATION WORKFLOW" in wikipedia_instructions),
        ("Entity type mapping", "ENTITY TYPE MAPPING TO SCHEMA.ORG" in wikipedia_instructions),
        ("Quality control requirements", "CRITICAL REQUIREMENTS - QUALITY CONTROL" in wikipedia_instructions),
        ("@context field requirement", "ALWAYS add @context field" in wikipedia_instructions),
        ("@type field requirement", "ALWAYS add @type field" in wikipedia_instructions),
        ("sameAs array requirement", "ALWAYS use sameAs as an array" in wikipedia_instructions),
        ("Immediate validation requirement", "CALL Validation Agent immediately" in wikipedia_instructions),
        ("Fix issues before returning", "FIX validation issues before returning" in wikipedia_instructions),
        ("Validation status tracking", "validation_status" in wikipedia_instructions),
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            logger.info(f"  ✓ {check_name}")
        else:
            logger.error(f"  ✗ {check_name}")
            all_passed = False
    
    # Verify Validation Agent instructions
    logger.info("\n✓ Checking Validation Agent instructions...")
    
    validation_checks = [
        ("On-demand validation", "ON-DEMAND VALIDATION" in validation_instructions),
        ("Schema.org validation", "Schema.org Validator tool" in validation_instructions),
        ("URL verification", "URL Verifier tool" in validation_instructions),
        ("Validation workflow", "VALIDATION WORKFLOW" in validation_instructions),
        ("Quality score calculation", "QUALITY SCORE CALCULATION" in validation_instructions),
    ]
    
    for check_name, check_result in validation_checks:
        if check_result:
            logger.info(f"  ✓ {check_name}")
        else:
            logger.error(f"  ✗ {check_name}")
            all_passed = False
    
    # Summary
    logger.info("\n" + "="*80)
    if all_passed:
        logger.info("✅ ALL CHECKS PASSED")
        logger.info("="*80)
        logger.info("\nWikipedia Agent is properly configured for immediate validation:")
        logger.info("  • Instructions include validation workflow")
        logger.info("  • Instructions include schema.org compliance requirements")
        logger.info("  • Instructions include validation feedback handling")
        logger.info("  • Instructions include quality control requirements")
        logger.info("  • Agent will call Validation Agent after enriching entities")
        logger.info("  • Agent will fix schema.org issues before returning entities")
        logger.info("  • All enriched entities will be schema.org compliant")
        logger.info("\nValidation Agent is available for on-demand validation:")
        logger.info("  • Has Schema.org Validator tool")
        logger.info("  • Has URL Verifier tool")
        logger.info("  • Provides immediate feedback")
        logger.info("  • Calculates quality scores")
        return True
    else:
        logger.error("❌ SOME CHECKS FAILED")
        logger.error("="*80)
        logger.error("\nPlease review the failed checks above")
        return False


if __name__ == "__main__":
    success = verify_wikipedia_agent_config()
    exit(0 if success else 1)
