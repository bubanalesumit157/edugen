"""
Partial Credit Module
Intelligent partial credit assignment for student responses
Detects common mistakes and assigns fair credit with justifications
"""

import sys
import os

# Fix imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import re
import warnings
warnings.filterwarnings('ignore')


class PartialCreditEngine:
    """
    Assigns partial credit to student responses based on mistake analysis
    Provides fair, consistent, and justified partial credit
    """

    def __init__(self, strategy: str = 'standard'):
        """
        Initialize partial credit engine

        Args:
            strategy: Grading strategy ('lenient', 'standard', 'strict')
        """
        self.strategy = strategy

        # Partial credit rules by mistake type
        self.mistake_rules = {
            'sign_error': {
                'lenient': 0.80,
                'standard': 0.70,
                'strict': 0.50
            },
            'unit_error': {
                'lenient': 0.85,
                'standard': 0.75,
                'strict': 0.60
            },
            'rounding_error': {
                'lenient': 0.95,
                'standard': 0.90,
                'strict': 0.80
            },
            'calculation_error': {
                'lenient': 0.70,
                'standard': 0.60,
                'strict': 0.40
            },
            'conceptual_error': {
                'lenient': 0.50,
                'standard': 0.40,
                'strict': 0.20
            },
            'method_correct_answer_wrong': {
                'lenient': 0.75,
                'standard': 0.65,
                'strict': 0.50
            },
            'incomplete_solution': {
                'lenient': 0.60,
                'standard': 0.50,
                'strict': 0.30
            },
            'minor_notation_error': {
                'lenient': 0.98,
                'standard': 0.95,
                'strict': 0.90
            }
        }

        # Step-based partial credit
        self.step_weights = {
            'problem_setup': 0.20,
            'method_selection': 0.25,
            'execution': 0.35,
            'final_answer': 0.20
        }

    def calculate_partial_credit(self, student_answer: Union[str, float],
                                 correct_answer: Union[str, float],
                                 max_points: float,
                                 work_shown: Dict = None) -> Dict:
        """
        Calculate partial credit for a student answer

        Args:
            student_answer: Student's answer
            correct_answer: Correct answer
            max_points: Maximum points for question
            work_shown: Optional dict with student's work/steps

        Returns:
            Partial credit result with justification
        """
        # Check if exactly correct
        if self._answers_match(student_answer, correct_answer):
            return {
                'points_earned': max_points,
                'percentage': 100,
                'mistake_type': None,
                'justification': 'Correct answer'
            }

        # Analyze the mistake
        mistake_analysis = self._analyze_mistake(student_answer, correct_answer)

        # Calculate partial credit
        credit_percentage = self._get_credit_percentage(mistake_analysis)
        points_earned = max_points * credit_percentage

        # If work is shown, adjust based on process
        if work_shown:
            process_credit = self._evaluate_process(work_shown)
            points_earned = max(points_earned, max_points * process_credit)

            if process_credit > credit_percentage:
                justification = f"{mistake_analysis['mistake_type']} in final answer, but correct method shown"
            else:
                justification = mistake_analysis['description']
        else:
            justification = mistake_analysis['description']

        return {
            'points_earned': points_earned,
            'percentage': (points_earned / max_points * 100),
            'mistake_type': mistake_analysis['mistake_type'],
            'justification': justification,
            'credit_percentage': credit_percentage
        }

    def evaluate_multi_step_problem(self, steps: List[Dict],
                                   max_points: float) -> Dict:
        """
        Evaluate multi-step problem with partial credit per step

        Args:
            steps: List of step dicts with 'name', 'student_answer', 'correct_answer'
            max_points: Maximum points for entire problem

        Returns:
            Step-by-step credit breakdown
        """
        step_results = []
        total_credit = 0

        # Assign weights if not provided
        if len(steps) <= len(self.step_weights):
            weights = list(self.step_weights.values())[:len(steps)]
        else:
            # Equal weights if more steps than defaults
            weights = [1.0 / len(steps)] * len(steps)

        # Evaluate each step
        for i, step in enumerate(steps):
            step_name = step.get('name', f'Step {i+1}')
            student_ans = step.get('student_answer')
            correct_ans = step.get('correct_answer')

            # Check correctness
            is_correct = self._answers_match(student_ans, correct_ans)

            if is_correct:
                step_credit = weights[i]
                mistake_type = None
                note = 'Correct'
            else:
                # Analyze mistake
                mistake = self._analyze_mistake(student_ans, correct_ans)
                partial = self._get_credit_percentage(mistake)
                step_credit = weights[i] * partial
                mistake_type = mistake['mistake_type']
                note = mistake['description']

            step_results.append({
                'step': step_name,
                'weight': weights[i],
                'credit_earned': step_credit,
                'is_correct': is_correct,
                'mistake_type': mistake_type,
                'note': note
            })

            total_credit += step_credit

        return {
            'total_credit': total_credit,
            'points_earned': max_points * total_credit,
            'max_points': max_points,
            'percentage': total_credit * 100,
            'steps': step_results,
            'summary': self._generate_step_summary(step_results)
        }

    def assign_method_credit(self, method_used: str,
                            correct_methods: List[str],
                            method_quality: str = 'good') -> float:
        """
        Assign credit for using correct method even if answer is wrong

        Args:
            method_used: Method student used
            correct_methods: List of acceptable methods
            method_quality: Quality of execution ('excellent', 'good', 'partial', 'poor')

        Returns:
            Credit percentage (0-1)
        """
        # Check if method is acceptable
        method_acceptable = any(
            method.lower() in method_used.lower() 
            for method in correct_methods
        )

        if not method_acceptable:
            return 0.0

        # Assign credit based on quality
        quality_credit = {
            'excellent': 0.90,
            'good': 0.75,
            'partial': 0.50,
            'poor': 0.25
        }

        return quality_credit.get(method_quality, 0.50)

    def detect_common_mistakes(self, student_answer: Union[str, float],
                              correct_answer: Union[str, float]) -> List[Dict]:
        """
        Detect common mistake patterns

        Args:
            student_answer: Student's answer
            correct_answer: Correct answer

        Returns:
            List of detected mistakes
        """
        mistakes = []

        # Convert to strings for analysis
        student_str = str(student_answer)
        correct_str = str(correct_answer)

        # Sign error detection
        if self._is_sign_error(student_str, correct_str):
            mistakes.append({
                'type': 'sign_error',
                'description': 'Incorrect sign (positive/negative)',
                'severity': 'moderate'
            })

        # Unit error detection
        if self._is_unit_error(student_str, correct_str):
            mistakes.append({
                'type': 'unit_error',
                'description': 'Incorrect or missing units',
                'severity': 'moderate'
            })

        # Rounding error detection
        if self._is_rounding_error(student_answer, correct_answer):
            mistakes.append({
                'type': 'rounding_error',
                'description': 'Rounding or precision difference',
                'severity': 'minor'
            })

        # Order of magnitude error
        if self._is_magnitude_error(student_answer, correct_answer):
            mistakes.append({
                'type': 'magnitude_error',
                'description': 'Order of magnitude error (factor of 10)',
                'severity': 'major'
            })

        # Reciprocal error (1/x instead of x)
        if self._is_reciprocal_error(student_answer, correct_answer):
            mistakes.append({
                'type': 'reciprocal_error',
                'description': 'Used reciprocal of correct value',
                'severity': 'major'
            })

        return mistakes

    def generate_feedback(self, partial_credit_result: Dict) -> str:
        """
        Generate constructive feedback based on partial credit result

        Args:
            partial_credit_result: Result from calculate_partial_credit

        Returns:
            Feedback message for student
        """
        points = partial_credit_result['points_earned']
        percentage = partial_credit_result['percentage']
        mistake = partial_credit_result.get('mistake_type')

        if percentage >= 95:
            tone = "Excellent work!"
        elif percentage >= 70:
            tone = "Good effort."
        elif percentage >= 50:
            tone = "Partial credit awarded."
        else:
            tone = "Keep trying."

        feedback = [tone]

        if mistake:
            feedback.append(partial_credit_result['justification'])
            feedback.append(self._get_mistake_advice(mistake))

        feedback.append(f"Points earned: {points:.2f}")

        return " ".join(feedback)

    def compare_grading_strategies(self, student_answer: Union[str, float],
                                  correct_answer: Union[str, float],
                                  max_points: float) -> Dict:
        """
        Compare partial credit across different grading strategies

        Args:
            student_answer: Student's answer
            correct_answer: Correct answer
            max_points: Maximum points

        Returns:
            Comparison of strategies
        """
        strategies = ['lenient', 'standard', 'strict']
        results = {}

        for strategy in strategies:
            original_strategy = self.strategy
            self.strategy = strategy

            result = self.calculate_partial_credit(
                student_answer, correct_answer, max_points
            )

            results[strategy] = {
                'points': result['points_earned'],
                'percentage': result['percentage'],
                'justification': result['justification']
            }

            self.strategy = original_strategy

        return {
            'strategies': results,
            'difference': results['lenient']['points'] - results['strict']['points'],
            'recommendation': self._recommend_strategy(results)
        }

    # Helper methods

    def _answers_match(self, student: Union[str, float],
                      correct: Union[str, float],
                      tolerance: float = 0.01) -> bool:
        """Check if answers match (with tolerance for numbers)"""
        # Try numeric comparison first
        try:
            student_num = float(student)
            correct_num = float(correct)
            return abs(student_num - correct_num) <= tolerance
        except (ValueError, TypeError):
            # String comparison
            return str(student).strip().lower() == str(correct).strip().lower()

    def _analyze_mistake(self, student: Union[str, float],
                        correct: Union[str, float]) -> Dict:
        """Analyze the type of mistake"""
        student_str = str(student)
        correct_str = str(correct)

        # Check specific error types
        if self._is_sign_error(student_str, correct_str):
            return {
                'mistake_type': 'sign_error',
                'description': 'Incorrect sign (positive/negative)'
            }

        if self._is_unit_error(student_str, correct_str):
            return {
                'mistake_type': 'unit_error',
                'description': 'Incorrect or missing units'
            }

        if self._is_rounding_error(student, correct):
            return {
                'mistake_type': 'rounding_error',
                'description': 'Minor rounding or precision difference'
            }

        if self._is_magnitude_error(student, correct):
            return {
                'mistake_type': 'calculation_error',
                'description': 'Significant calculation error'
            }

        # Default to general error
        return {
            'mistake_type': 'calculation_error',
            'description': 'Incorrect answer'
        }

    def _get_credit_percentage(self, mistake_analysis: Dict) -> float:
        """Get partial credit percentage for mistake type"""
        mistake_type = mistake_analysis['mistake_type']

        if mistake_type in self.mistake_rules:
            return self.mistake_rules[mistake_type][self.strategy]

        return 0.0

    def _evaluate_process(self, work_shown: Dict) -> float:
        """Evaluate student's work process"""
        total_credit = 0

        # Check each component
        if work_shown.get('setup_correct', False):
            total_credit += self.step_weights['problem_setup']

        if work_shown.get('method_correct', False):
            total_credit += self.step_weights['method_selection']

        if work_shown.get('execution_quality', 0) > 0:
            total_credit += self.step_weights['execution'] * work_shown['execution_quality']

        return total_credit

    def _is_sign_error(self, student: str, correct: str) -> bool:
        """Check for sign error"""
        try:
            student_num = float(re.sub(r'[^0-9.-]', '', student))
            correct_num = float(re.sub(r'[^0-9.-]', '', correct))
            return abs(student_num) == abs(correct_num) and student_num != correct_num
        except (ValueError, AttributeError):
            return False

    def _is_unit_error(self, student: str, correct: str) -> bool:
        """Check for unit error"""
        # Extract numbers
        try:
            student_num = float(re.sub(r'[^0-9.-]', '', student))
            correct_num = float(re.sub(r'[^0-9.-]', '', correct))

            # Numbers match but strings don't (likely unit difference)
            if abs(student_num - correct_num) < 0.01:
                return student.strip() != correct.strip()
        except (ValueError, AttributeError):
            pass

        return False

    def _is_rounding_error(self, student: Union[str, float],
                          correct: Union[str, float]) -> bool:
        """Check for rounding error"""
        try:
            student_num = float(student)
            correct_num = float(correct)

            # Within 5% or 0.1, whichever is larger
            tolerance = max(abs(correct_num) * 0.05, 0.1)
            return abs(student_num - correct_num) <= tolerance
        except (ValueError, TypeError):
            return False

    def _is_magnitude_error(self, student: Union[str, float],
                           correct: Union[str, float]) -> bool:
        """Check for order of magnitude error"""
        try:
            student_num = float(student)
            correct_num = float(correct)

            if correct_num == 0:
                return False

            ratio = abs(student_num / correct_num)
            # Check if off by factor of 10, 100, etc.
            return (9 <= ratio <= 11) or (0.09 <= ratio <= 0.11)
        except (ValueError, TypeError, ZeroDivisionError):
            return False

    def _is_reciprocal_error(self, student: Union[str, float],
                            correct: Union[str, float]) -> bool:
        """Check if student used reciprocal"""
        try:
            student_num = float(student)
            correct_num = float(correct)

            if student_num == 0 or correct_num == 0:
                return False

            return abs(student_num * correct_num - 1) < 0.01
        except (ValueError, TypeError):
            return False

    def _generate_step_summary(self, step_results: List[Dict]) -> str:
        """Generate summary of step-by-step results"""
        correct_steps = sum(1 for s in step_results if s['is_correct'])
        total_steps = len(step_results)

        return f"{correct_steps}/{total_steps} steps correct"

    def _get_mistake_advice(self, mistake_type: str) -> str:
        """Get advice for specific mistake type"""
        advice = {
            'sign_error': 'Double-check your signs (positive/negative).',
            'unit_error': 'Remember to include proper units in your answer.',
            'rounding_error': 'Be careful with rounding - use more decimal places.',
            'calculation_error': 'Review your calculations step by step.',
            'conceptual_error': 'Review the underlying concept for this problem.',
            'magnitude_error': 'Check your order of magnitude (powers of 10).'
        }

        return advice.get(mistake_type, 'Review your work carefully.')

    def _recommend_strategy(self, results: Dict) -> str:
        """Recommend grading strategy"""
        difference = results['lenient']['points'] - results['strict']['points']

        if difference < 1:
            return 'Mistake is minor - strategy choice has minimal impact'
        elif difference < 3:
            return 'Standard strategy recommended for fair grading'
        else:
            return 'Significant mistake - consider context when choosing strategy'


# Example usage
if __name__ == "__main__":
    engine = PartialCreditEngine(strategy='standard')

    print("\n🎯 Partial Credit Engine - Fair Grading for Educators")
    print("="*60)

    # Example 1: Sign error
    print("\n📋 Example 1: Sign Error")
    print("-"*60)

    result1 = engine.calculate_partial_credit(
        student_answer=-9.8,
        correct_answer=9.8,
        max_points=10
    )

    print(f"Student answer: -9.8")
    print(f"Correct answer: 9.8")
    print(f"Points earned: {result1['points_earned']:.1f}/10 ({result1['percentage']:.0f}%)")
    print(f"Mistake type: {result1['mistake_type']}")
    print(f"Justification: {result1['justification']}")
    print(f"\nFeedback: {engine.generate_feedback(result1)}")

    # Example 2: Unit error
    print("\n\n📋 Example 2: Unit Error")
    print("-"*60)

    result2 = engine.calculate_partial_credit(
        student_answer="9.8 m/s",
        correct_answer="9.8 m/s²",
        max_points=10
    )

    print(f"Student answer: 9.8 m/s")
    print(f"Correct answer: 9.8 m/s²")
    print(f"Points earned: {result2['points_earned']:.1f}/10 ({result2['percentage']:.0f}%)")
    print(f"Mistake type: {result2['mistake_type']}")
    print(f"\nFeedback: {engine.generate_feedback(result2)}")

    # Example 3: Multi-step problem
    print("\n\n📋 Example 3: Multi-Step Problem")
    print("-"*60)

    steps = [
        {'name': 'Identify given values', 'student_answer': 'correct', 'correct_answer': 'correct'},
        {'name': 'Select formula', 'student_answer': 'correct', 'correct_answer': 'correct'},
        {'name': 'Substitute values', 'student_answer': 'correct', 'correct_answer': 'correct'},
        {'name': 'Calculate result', 'student_answer': 98, 'correct_answer': 49}
    ]

    multi_result = engine.evaluate_multi_step_problem(steps, max_points=10)

    print(f"Total points: {multi_result['points_earned']:.1f}/10 ({multi_result['percentage']:.0f}%)")
    print(f"Summary: {multi_result['summary']}")
    print("\nStep breakdown:")
    for step in multi_result['steps']:
        status = "✅" if step['is_correct'] else "❌"
        print(f"  {status} {step['step']} (weight: {step['weight']:.0%}): {step['credit_earned']:.2f} credit")
        if not step['is_correct']:
            print(f"     Note: {step['note']}")

    # Example 4: Strategy comparison
    print("\n\n📋 Example 4: Grading Strategy Comparison")
    print("-"*60)

    comparison = engine.compare_grading_strategies(
        student_answer=-9.8,
        correct_answer=9.8,
        max_points=10
    )

    print("Sign error with different strategies:")
    for strategy, result in comparison['strategies'].items():
        print(f"  {strategy.capitalize()}: {result['points']:.1f}/10 ({result['percentage']:.0f}%)")

    print(f"\nDifference (lenient - strict): {comparison['difference']:.1f} points")
    print(f"Recommendation: {comparison['recommendation']}")

    print("\n="*60)
    print("✅ Partial credit examples complete!")
