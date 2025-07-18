#!/usr/bin/env python3
"""
Deployment Configuration Validation Script
Validates environment configuration before deployment
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.config.environment import validate_deployment_config, get_config_summary
from src.helpers.utils import setup_logger

def main():
    """Main validation function"""
    logger = setup_logger(__name__)
    
    print("🔍 XOFlowers AI Agent - Deployment Configuration Validation")
    print("=" * 60)
    
    try:
        # Validate configuration
        validation_result = validate_deployment_config()
        
        # Print configuration summary
        print("\n📋 Configuration Summary:")
        print("-" * 30)
        config_summary = get_config_summary()
        for key, value in config_summary.items():
            print(f"  {key}: {value}")
        
        # Print validation results
        print(f"\n✅ Configuration Valid: {validation_result['valid']}")
        
        if validation_result['issues']:
            print(f"\n❌ Critical Issues ({len(validation_result['issues'])}):")
            for issue in validation_result['issues']:
                print(f"  • {issue}")
        
        if validation_result['warnings']:
            print(f"\n⚠️  Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result['warnings']:
                print(f"  • {warning}")
        
        # Exit with appropriate code
        if validation_result['valid']:
            if validation_result['warnings']:
                print(f"\n🟡 Configuration is valid but has {len(validation_result['warnings'])} warnings")
                print("   Consider addressing warnings before production deployment")
                sys.exit(1)  # Exit with warning code
            else:
                print("\n🟢 Configuration is valid and ready for deployment!")
                sys.exit(0)  # Success
        else:
            print(f"\n🔴 Configuration has {len(validation_result['issues'])} critical issues")
            print("   Fix these issues before deployment")
            sys.exit(2)  # Critical error
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n💥 Validation Error: {e}")
        sys.exit(3)  # Validation error

if __name__ == "__main__":
    main()