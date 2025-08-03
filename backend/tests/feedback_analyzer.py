#!/usr/bin/env python3
"""
Feedback Analyzer for UAT Step 15.4
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any


def analyze_feedback_files():
    """Analyze all feedback files in the test_results directory."""
    print("📊 Feedback Analysis - Step 15.4")
    print("=" * 50)
    
    # Find all feedback files
    feedback_files = glob.glob("data/test_results/feedback_*.json")
    
    if not feedback_files:
        print("❌ No feedback files found in data/test_results/")
        return
    
    all_feedback = []
    for filename in feedback_files:
        try:
            with open(filename, 'r') as f:
                feedback = json.load(f)
                all_feedback.append(feedback)
        except Exception as e:
            print(f"⚠️  Error reading {filename}: {e}")
    
    if not all_feedback:
        print("❌ No valid feedback data found")
        return
    
    # Analyze feedback
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'total_responses': len(all_feedback),
        'roles': {},
        'average_scores': {},
        'common_issues': [],
        'improvement_suggestions': []
    }
    
    # Analyze by role
    for feedback in all_feedback:
        role = feedback.get('role', 'unknown')
        if role not in analysis['roles']:
            analysis['roles'][role] = 0
        analysis['roles'][role] += 1
    
    # Calculate average scores
    scores = {
        'validation_confidence': [],
        'performance_rating': [],
        'overall_satisfaction': []
    }
    
    for feedback in all_feedback:
        for score_type in scores:
            if score_type in feedback:
                scores[score_type].append(feedback[score_type])
    
    for score_type, values in scores.items():
        if values:
            analysis['average_scores'][score_type] = sum(values) / len(values)
    
    # Collect improvement suggestions
    for feedback in all_feedback:
        if 'additional_features' in feedback and feedback['additional_features']:
            analysis['improvement_suggestions'].append(feedback['additional_features'])
    
    # Identify common issues
    for feedback in all_feedback:
        if feedback.get('error_message_clarity') == 'No':
            analysis['common_issues'].append('Error message clarity')
        if feedback.get('workflow_impact') == 'Negative':
            analysis['common_issues'].append('Workflow disruption')
    
    analysis['common_issues'] = list(set(analysis['common_issues']))
    
    # Print analysis results
    print(f"📈 Analysis Results:")
    print(f"   Total Responses: {analysis['total_responses']}")
    print(f"   Roles: {dict(analysis['roles'])}")
    print(f"   Average Validation Confidence: {analysis['average_scores'].get('validation_confidence', 0):.2f}/5.0")
    print(f"   Average Performance Rating: {analysis['average_scores'].get('performance_rating', 0):.2f}/5.0")
    print(f"   Average Overall Satisfaction: {analysis['average_scores'].get('overall_satisfaction', 0):.2f}/5.0")
    print(f"   Common Issues: {', '.join(analysis['common_issues'])}")
    print(f"   Improvement Suggestions: {len(analysis['improvement_suggestions'])} collected")
    
    # Save analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_filename = f"data/test_results/feedback_analysis_{timestamp}.json"
    
    with open(analysis_filename, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {analysis_filename}")
    
    return analysis


if __name__ == '__main__':
    analyze_feedback_files() 