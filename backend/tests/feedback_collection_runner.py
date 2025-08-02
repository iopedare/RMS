#!/usr/bin/env python3
"""
Feedback Collection Runner for UAT Step 15.4
This script helps collect and analyze user feedback for validation improvements.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.validation import validate_device_registration_data, validate_sync_event_data


class FeedbackCollector:
    """Collect and analyze user feedback for validation improvements."""
    
    def __init__(self):
        self.feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'validation_feedback': [],
            'sync_feedback': [],
            'performance_feedback': [],
            'overall_satisfaction': {}
        }
        
    def collect_admin_feedback(self) -> Dict[str, Any]:
        """Collect feedback from system administrators."""
        print("\n🔐 ADMIN FEEDBACK COLLECTION")
        print("=" * 50)
        
        feedback = {
            'role': 'admin',
            'timestamp': datetime.now().isoformat(),
            'validation_confidence': self._get_rating("How confident are you in the system's data validation? (1-5)"),
            'error_message_clarity': self._get_yes_no("Are error messages clear and actionable?"),
            'master_election_reliability': self._get_yes_no("Does the master election process work reliably?"),
            'audit_log_sufficiency': self._get_yes_no("Are audit logs sufficient for compliance?"),
            'additional_features': self._get_text("What additional validation features do you need?"),
            'security_concerns': self._get_text("Any security concerns with the current validation?"),
            'compliance_requirements': self._get_text("Any compliance requirements not met?")
        }
        
        self.feedback_data['validation_feedback'].append(feedback)
        return feedback
    
    def collect_manager_feedback(self) -> Dict[str, Any]:
        """Collect feedback from store managers."""
        print("\n👔 MANAGER FEEDBACK COLLECTION")
        print("=" * 50)
        
        feedback = {
            'role': 'manager',
            'timestamp': datetime.now().isoformat(),
            'workflow_impact': self._get_choice("How does the validation affect your daily workflow?", 
                                              ["Positive", "Negative", "Neutral"]),
            'conflict_resolution': self._get_yes_no("Are data conflicts resolved satisfactorily?"),
            'sync_status_helpful': self._get_yes_no("Is the sync status display helpful?"),
            'team_improvements': self._get_text("What validation improvements would help your team?"),
            'data_consistency': self._get_rating("Rate data consistency across devices (1-5)"),
            'operational_efficiency': self._get_rating("Rate operational efficiency with current validation (1-5)")
        }
        
        self.feedback_data['validation_feedback'].append(feedback)
        return feedback
    
    def collect_assistant_manager_feedback(self) -> Dict[str, Any]:
        """Collect feedback from assistant managers."""
        print("\n👨‍💼 ASSISTANT MANAGER FEEDBACK COLLECTION")
        print("=" * 50)
        
        feedback = {
            'role': 'assistant_manager',
            'timestamp': datetime.now().isoformat(),
            'team_monitoring': self._get_yes_no("Can you effectively monitor team activities?"),
            'error_handling': self._get_yes_no("Are validation errors handled gracefully?"),
            'peak_performance': self._get_yes_no("Is the system responsive during peak usage?"),
            'oversight_features': self._get_text("What additional oversight features do you need?"),
            'communication_effectiveness': self._get_rating("Rate communication effectiveness (1-5)"),
            'coordination_ease': self._get_rating("Rate team coordination ease (1-5)")
        }
        
        self.feedback_data['validation_feedback'].append(feedback)
        return feedback
    
    def collect_sales_assistant_feedback(self) -> Dict[str, Any]:
        """Collect feedback from sales assistants."""
        print("\n🛍️ SALES ASSISTANT FEEDBACK COLLECTION")
        print("=" * 50)
        
        feedback = {
            'role': 'sales_assistant',
            'timestamp': datetime.now().isoformat(),
            'work_slowdown': self._get_choice("Do validation errors slow down your work?", 
                                            ["Yes", "No", "Sometimes"]),
            'error_understanding': self._get_yes_no("Are error messages easy to understand?"),
            'transaction_speed': self._get_choice("Does the system respond quickly during transactions?", 
                                                ["Yes", "No", "Sometimes"]),
            'usability_improvements': self._get_text("What would make the system easier to use?"),
            'training_needs': self._get_text("What training do you need for the validation system?"),
            'transaction_efficiency': self._get_rating("Rate transaction efficiency (1-5)")
        }
        
        self.feedback_data['validation_feedback'].append(feedback)
        return feedback
    
    def test_validation_scenarios(self) -> Dict[str, Any]:
        """Test validation scenarios and collect feedback."""
        print("\n🧪 VALIDATION SCENARIO TESTING")
        print("=" * 50)
        
        scenarios = [
            {
                'name': 'Invalid Device ID',
                'data': {'device_id': 'test<script>', 'role': 'admin', 'priority': 100},
                'expected': False
            },
            {
                'name': 'Invalid Role',
                'data': {'device_id': 'test', 'role': 'invalid_role', 'priority': 100},
                'expected': False
            },
            {
                'name': 'Invalid Priority',
                'data': {'device_id': 'test', 'role': 'admin', 'priority': 150},
                'expected': False
            },
            {
                'name': 'Missing Fields',
                'data': {'device_id': 'test', 'role': 'admin'},
                'expected': False
            },
            {
                'name': 'Valid Registration',
                'data': {'device_id': 'test_device', 'role': 'admin', 'priority': 100},
                'expected': True
            }
        ]
        
        scenario_results = []
        for scenario in scenarios:
            print(f"\nTesting: {scenario['name']}")
            is_valid, error_msg, validated_data = validate_device_registration_data(scenario['data'])
            
            result = {
                'scenario': scenario['name'],
                'data': scenario['data'],
                'expected_valid': scenario['expected'],
                'actual_valid': is_valid,
                'error_message': error_msg,
                'passed': (is_valid == scenario['expected'])
            }
            
            if result['passed']:
                print(f"✅ PASS: {scenario['name']}")
            else:
                print(f"❌ FAIL: {scenario['name']}")
                print(f"   Expected: {scenario['expected']}, Got: {is_valid}")
                if error_msg:
                    print(f"   Error: {error_msg}")
            
            scenario_results.append(result)
            
            # Collect feedback on error messages
            if not is_valid and error_msg:
                clarity = self._get_rating(f"How clear is this error message? (1-5): '{error_msg}'")
                helpfulness = self._get_rating(f"How helpful is this error message? (1-5): '{error_msg}'")
                
                result['error_clarity'] = clarity
                result['error_helpfulness'] = helpfulness
        
        self.feedback_data['validation_feedback'].append({
            'type': 'scenario_testing',
            'timestamp': datetime.now().isoformat(),
            'scenarios': scenario_results
        })
        
        return {'scenarios': scenario_results}
    
    def collect_performance_feedback(self) -> Dict[str, Any]:
        """Collect performance-related feedback."""
        print("\n⚡ PERFORMANCE FEEDBACK COLLECTION")
        print("=" * 50)
        
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'registration_speed': self._get_rating("Rate device registration speed (1-5)"),
            'sync_speed': self._get_rating("Rate data sync speed (1-5)"),
            'error_recovery_speed': self._get_rating("Rate error recovery speed (1-5)"),
            'system_responsiveness': self._get_rating("Rate overall system responsiveness (1-5)"),
            'performance_issues': self._get_text("Any specific performance issues?"),
            'optimization_suggestions': self._get_text("Suggestions for performance improvements?")
        }
        
        self.feedback_data['performance_feedback'].append(feedback)
        return feedback
    
    def collect_overall_satisfaction(self) -> Dict[str, Any]:
        """Collect overall satisfaction metrics."""
        print("\n😊 OVERALL SATISFACTION SURVEY")
        print("=" * 50)
        
        satisfaction = {
            'timestamp': datetime.now().isoformat(),
            'overall_satisfaction': self._get_rating("Overall satisfaction with validation system (1-5)"),
            'system_reliability': self._get_rating("Rate system reliability (1-5)"),
            'ease_of_use': self._get_rating("Rate ease of use (1-5)"),
            'feature_completeness': self._get_rating("Rate feature completeness (1-5)"),
            'recommendation_likelihood': self._get_rating("Likelihood to recommend to others (1-5)"),
            'improvement_priority': self._get_choice("What should be the top priority for improvement?",
                                                   ["Performance", "Usability", "Features", "Security", "Documentation"])
        }
        
        self.feedback_data['overall_satisfaction'] = satisfaction
        return satisfaction
    
    def analyze_feedback(self) -> Dict[str, Any]:
        """Analyze collected feedback and generate insights."""
        print("\n📊 FEEDBACK ANALYSIS")
        print("=" * 50)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_responses': len(self.feedback_data['validation_feedback']),
            'average_satisfaction': 0,
            'common_issues': [],
            'improvement_suggestions': [],
            'priority_areas': []
        }
        
        # Calculate average satisfaction
        satisfaction_scores = []
        for feedback in self.feedback_data['validation_feedback']:
            if 'overall_satisfaction' in feedback:
                satisfaction_scores.append(feedback['overall_satisfaction'])
        
        if satisfaction_scores:
            analysis['average_satisfaction'] = sum(satisfaction_scores) / len(satisfaction_scores)
        
        # Identify common issues
        issues = []
        for feedback in self.feedback_data['validation_feedback']:
            if 'error_understanding' in feedback and feedback['error_understanding'] == 'No':
                issues.append('Error message clarity')
            if 'workflow_impact' in feedback and feedback['workflow_impact'] == 'Negative':
                issues.append('Workflow disruption')
            if 'transaction_speed' in feedback and feedback['transaction_speed'] == 'No':
                issues.append('Transaction speed')
        
        analysis['common_issues'] = list(set(issues))
        
        # Collect improvement suggestions
        suggestions = []
        for feedback in self.feedback_data['validation_feedback']:
            if 'additional_features' in feedback and feedback['additional_features']:
                suggestions.append(feedback['additional_features'])
            if 'usability_improvements' in feedback and feedback['usability_improvements']:
                suggestions.append(feedback['usability_improvements'])
        
        analysis['improvement_suggestions'] = suggestions
        
        print(f"📈 Analysis Results:")
        print(f"   Total Responses: {analysis['total_responses']}")
        print(f"   Average Satisfaction: {analysis['average_satisfaction']:.2f}/5.0")
        print(f"   Common Issues: {', '.join(analysis['common_issues'])}")
        print(f"   Improvement Suggestions: {len(analysis['improvement_suggestions'])} collected")
        
        return analysis
    
    def save_feedback(self, filename: str = None) -> str:
        """Save feedback data to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/test_results/feedback_collection_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
        
        print(f"\n💾 Feedback saved to: {filename}")
        return filename
    
    def _get_rating(self, question: str) -> int:
        """Get a rating from 1-5."""
        while True:
            try:
                response = input(f"{question} (1-5): ").strip()
                rating = int(response)
                if 1 <= rating <= 5:
                    return rating
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_yes_no(self, question: str) -> str:
        """Get a Yes/No/Partially response."""
        while True:
            response = input(f"{question} (Yes/No/Partially): ").strip().lower()
            if response in ['yes', 'no', 'partially']:
                return response.capitalize()
            else:
                print("Please enter Yes, No, or Partially.")
    
    def _get_choice(self, question: str, choices: List[str]) -> str:
        """Get a choice from a list of options."""
        print(f"{question}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                response = int(input(f"Enter choice (1-{len(choices)}): ").strip())
                if 1 <= response <= len(choices):
                    return choices[response - 1]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("Please enter a valid number.")
    
    def _get_text(self, question: str) -> str:
        """Get a text response."""
        return input(f"{question}: ").strip()


def main():
    """Main function to run feedback collection."""
    print("📊 UAT Feedback Collection Runner")
    print("=" * 50)
    print("This tool will help collect user feedback for validation improvements.")
    print("Follow the prompts to provide feedback for your role.")
    
    collector = FeedbackCollector()
    
    # Collect role-specific feedback
    print("\n🎯 Select your role for feedback collection:")
    print("1. System Administrator")
    print("2. Store Manager")
    print("3. Assistant Manager")
    print("4. Sales Assistant")
    print("5. Test All Scenarios")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (1-5): ").strip())
            if 1 <= choice <= 5:
                break
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")
    
    if choice == 1:
        collector.collect_admin_feedback()
    elif choice == 2:
        collector.collect_manager_feedback()
    elif choice == 3:
        collector.collect_assistant_manager_feedback()
    elif choice == 4:
        collector.collect_sales_assistant_feedback()
    elif choice == 5:
        # Test all scenarios
        collector.test_validation_scenarios()
    
    # Collect performance feedback
    collector.collect_performance_feedback()
    
    # Collect overall satisfaction
    collector.collect_overall_satisfaction()
    
    # Analyze feedback
    analysis = collector.analyze_feedback()
    
    # Save feedback
    filename = collector.save_feedback()
    
    print(f"\n✅ Feedback collection completed!")
    print(f"📄 Results saved to: {filename}")
    print(f"📊 Analysis completed with {analysis['total_responses']} responses")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 