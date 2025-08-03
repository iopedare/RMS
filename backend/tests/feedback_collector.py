#!/usr/bin/env python3
"""
Simple Feedback Collector for UAT Step 15.4
"""

import json
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.validation import validate_device_registration_data


def collect_feedback():
    """Collect user feedback for validation improvements."""
    print("📊 UAT Feedback Collection - Step 15.4")
    print("=" * 50)
    
    feedback = {
        'timestamp': datetime.now().isoformat(),
        'role': input("Enter your role (admin/manager/assistant_manager/sales_assistant): "),
        'validation_confidence': int(input("How confident are you in the system's data validation? (1-5): ")),
        'error_message_clarity': input("Are error messages clear and actionable? (Yes/No/Partially): "),
        'workflow_impact': input("How does validation affect your workflow? (Positive/Negative/Neutral): "),
        'additional_features': input("What additional validation features do you need? "),
        'performance_rating': int(input("Rate system performance (1-5): ")),
        'overall_satisfaction': int(input("Overall satisfaction with validation system (1-5): "))
    }
    
    # Test validation scenarios
    print("\n🧪 Testing Validation Scenarios...")
    scenarios = [
        {'name': 'Invalid Device ID', 'data': {'device_id': 'test<script>', 'role': 'admin', 'priority': 100}},
        {'name': 'Valid Registration', 'data': {'device_id': 'test_device', 'role': 'admin', 'priority': 100}}
    ]
    
    scenario_results = []
    for scenario in scenarios:
        is_valid, error_msg, validated_data = validate_device_registration_data(scenario['data'])
        result = {
            'scenario': scenario['name'],
            'valid': is_valid,
            'error_message': error_msg
        }
        scenario_results.append(result)
        print(f"✅ {scenario['name']}: {'PASS' if is_valid == (scenario['name'] == 'Valid Registration') else 'FAIL'}")
    
    feedback['scenario_results'] = scenario_results
    
    # Save feedback
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/test_results/feedback_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(feedback, f, indent=2)
    
    print(f"\n💾 Feedback saved to: {filename}")
    return feedback


if __name__ == '__main__':
    collect_feedback() 