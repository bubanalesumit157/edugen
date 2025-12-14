"""
Feedback Generator Module
AI-assisted feedback generation for student responses
Provides personalized, constructive, and encouraging feedback
"""

import sys
import os

# Fix imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class FeedbackGenerator:
    """
    Generates personalized, constructive feedback for student responses
    Helps educators provide consistent, helpful feedback at scale
    """

    def __init__(self, tone: str = 'encouraging'):
        """
        Initialize feedback generator

        Args:
            tone: Feedback tone ('encouraging', 'neutral', 'direct')
        """
        self.tone = tone

        # Feedback templates by performance level
        self.templates = {
            'excellent': {
                'opening': [
                    "Excellent work!",
                    "Outstanding job!",
                    "Fantastic performance!",
                    "Superb work!"
                ],
                'strength': "You demonstrated strong understanding of {concept}.",
                'encouragement': "Keep up the excellent work!"
            },
            'good': {
                'opening': [
                    "Good work!",
                    "Nice job!",
                    "Well done!",
                    "Great effort!"
                ],
                'strength': "You showed good understanding of {concept}.",
                'encouragement': "You're on the right track!"
            },
            'satisfactory': {
                'opening': [
                    "Good effort!",
                    "You're making progress!",
                    "Keep working!",
                    "You're improving!"
                ],
                'strength': "You grasped the basic concept of {concept}.",
                'encouragement': "Keep practicing to strengthen your understanding!"
            },
            'needs_improvement': {
                'opening': [
                    "Keep trying!",
                    "Don't give up!",
                    "You can do this!",
                    "Let's work on this together!"
                ],
                'strength': "I can see you're working on {concept}.",
                'encouragement': "With more practice, you'll get there!"
            }
        }

        # Mistake-specific feedback
        self.mistake_feedback = {
            'sign_error': {
                'identification': "You made a sign error (positive/negative).",
                'explanation': "The value is correct, but the sign should be {correct_sign}.",
                'suggestion': "Tip: Draw a diagram to visualize direction, or check your signs at each step.",
                'resources': ["Review: Signed numbers and direction conventions"]
            },
            'unit_error': {
                'identification': "Your units are incorrect or missing.",
                'explanation': "The numerical value is right, but units should be {correct_units}.",
                'suggestion': "Tip: Always write units alongside numbers throughout your work.",
                'resources': ["Review: Unit conversion and dimensional analysis"]
            },
            'rounding_error': {
                'identification': "Your answer is very close but has a rounding difference.",
                'explanation': "Consider using more decimal places in intermediate steps.",
                'suggestion': "Tip: Keep extra precision during calculations, round only at the end.",
                'resources': ["Review: Significant figures and rounding"]
            },
            'calculation_error': {
                'identification': "There's an error in your calculations.",
                'explanation': "Your approach is correct, but check your arithmetic.",
                'suggestion': "Tip: Work through each calculation step carefully and double-check.",
                'resources': ["Practice: Similar calculation problems"]
            },
            'conceptual_error': {
                'identification': "There's a conceptual misunderstanding here.",
                'explanation': "Review the underlying concept before reattempting.",
                'suggestion': "Tip: Go back to the definition and work through examples.",
                'resources': ["Review: Core concept explanation", "Watch: Concept tutorial video"]
            },
            'method_error': {
                'identification': "The method you used isn't quite right for this problem.",
                'explanation': "This problem requires a different approach.",
                'suggestion': "Tip: Identify what type of problem this is, then select the appropriate method.",
                'resources': ["Review: Problem-solving strategies"]
            },
            'incomplete_solution': {
                'identification': "Your solution is incomplete.",
                'explanation': "You started well but didn't finish all required steps.",
                'suggestion': "Tip: Read the question carefully and make sure you've answered all parts.",
                'resources': ["Review: Complete problem-solving process"]
            }
        }

        # Strength identifiers
        self.strength_patterns = {
            'correct_method': "You selected the correct method to solve this problem.",
            'clear_work': "Your work is clearly organized and easy to follow.",
            'correct_setup': "You correctly set up the problem.",
            'good_reasoning': "Your reasoning is logical and well-explained.",
            'proper_notation': "You used proper mathematical notation.",
            'complete_answer': "You provided a complete answer with all required parts."
        }

    def generate_feedback(self, student_performance: Dict,
                         question_info: Dict = None) -> Dict:
        """
        Generate comprehensive feedback for student performance

        Args:
            student_performance: Dict with score, mistakes, strengths
            question_info: Optional question context

        Returns:
            Generated feedback with multiple components
        """
        score_percentage = student_performance.get('percentage', 0)

        # Determine performance level
        performance_level = self._determine_performance_level(score_percentage)

        # Generate feedback components
        opening = self._select_opening(performance_level)
        strengths = self._identify_strengths(student_performance)
        improvements = self._suggest_improvements(student_performance)
        resources = self._recommend_resources(student_performance, question_info)
        closing = self._generate_closing(performance_level, score_percentage)

        # Compile full feedback
        feedback_text = self._compile_feedback(
            opening, strengths, improvements, resources, closing
        )

        return {
            'feedback_text': feedback_text,
            'performance_level': performance_level,
            'strengths': strengths,
            'improvements': improvements,
            'resources': resources,
            'tone': self.tone,
            'score_percentage': score_percentage
        }

    def generate_rubric_feedback(self, rubric_results: Dict,
                                criterion_details: Dict = None) -> str:
        """
        Generate feedback based on rubric scoring

        Args:
            rubric_results: Results from rubric application
            criterion_details: Optional details about criteria

        Returns:
            Rubric-based feedback text
        """
        feedback_parts = []

        # Overall performance
        percentage = rubric_results.get('percentage', 0)
        feedback_parts.append(self._get_performance_opening(percentage))

        # Criterion-by-criterion feedback
        criterion_scores = rubric_results.get('criterion_scores', [])

        if criterion_scores:
            feedback_parts.append("\n\nPerformance by criterion:")

            for criterion in criterion_scores:
                name = criterion['criterion']
                earned = criterion['earned_points']
                max_pts = criterion['max_points']
                pct = criterion['percentage']

                if pct >= 90:
                    icon = "✅"
                    comment = "Excellent"
                elif pct >= 70:
                    icon = "✓"
                    comment = "Good"
                elif pct >= 50:
                    icon = "○"
                    comment = "Satisfactory"
                else:
                    icon = "⚠️"
                    comment = "Needs work"

                feedback_parts.append(
                    f"  {icon} {name}: {earned:.1f}/{max_pts} - {comment}"
                )

        # Closing encouragement
        feedback_parts.append("\n" + self._generate_closing(
            self._determine_performance_level(percentage),
            percentage
        ))

        return "\n".join(feedback_parts)

    def generate_comparative_feedback(self, student_score: float,
                                     class_average: float,
                                     class_std_dev: float) -> str:
        """
        Generate feedback comparing student to class performance

        Args:
            student_score: Student's score (0-100)
            class_average: Class average score
            class_std_dev: Class standard deviation

        Returns:
            Comparative feedback text
        """
        diff = student_score - class_average

        feedback_parts = []

        if diff > class_std_dev:
            feedback_parts.append("🌟 You performed above the class average!")
            feedback_parts.append(f"Your score: {student_score:.1f}% (Class avg: {class_average:.1f}%)")
            feedback_parts.append("You're demonstrating strong understanding of this material.")
        elif diff > 0:
            feedback_parts.append("✓ You performed above the class average.")
            feedback_parts.append(f"Your score: {student_score:.1f}% (Class avg: {class_average:.1f}%)")
            feedback_parts.append("Keep up the good work!")
        elif diff > -class_std_dev:
            feedback_parts.append("You're performing close to the class average.")
            feedback_parts.append(f"Your score: {student_score:.1f}% (Class avg: {class_average:.1f}%)")
            feedback_parts.append("With a bit more practice, you can excel!")
        else:
            feedback_parts.append("Let's work together to improve your understanding.")
            feedback_parts.append(f"Your score: {student_score:.1f}% (Class avg: {class_average:.1f}%)")
            feedback_parts.append("Don't hesitate to ask for help - that's what I'm here for!")

        return " ".join(feedback_parts)

    def generate_progress_feedback(self, current_score: float,
                                   previous_scores: List[float]) -> str:
        """
        Generate feedback based on student's progress over time

        Args:
            current_score: Current assessment score
            previous_scores: List of previous scores

        Returns:
            Progress-based feedback
        """
        if not previous_scores:
            return "This is your first assessment. Good luck!"

        avg_previous = np.mean(previous_scores)
        improvement = current_score - avg_previous

        feedback_parts = []

        if improvement > 10:
            feedback_parts.append("🎉 Excellent improvement!")
            feedback_parts.append(f"You've improved by {improvement:.1f} percentage points!")
            feedback_parts.append("Your hard work is paying off. Keep it up!")
        elif improvement > 5:
            feedback_parts.append("📈 Nice improvement!")
            feedback_parts.append(f"You've improved by {improvement:.1f} percentage points.")
            feedback_parts.append("You're moving in the right direction!")
        elif improvement > -5:
            feedback_parts.append("You're maintaining consistent performance.")
            feedback_parts.append("Consider reviewing areas where you struggled to improve further.")
        else:
            feedback_parts.append("Your score decreased from previous assessments.")
            feedback_parts.append("Let's identify what's challenging you and work on it together.")
            feedback_parts.append("Don't get discouraged - everyone has setbacks!")

        return " ".join(feedback_parts)

    def customize_feedback_template(self, template_name: str,
                                   custom_messages: Dict) -> None:
        """
        Customize feedback templates

        Args:
            template_name: Name of template to customize
            custom_messages: Dict of custom messages
        """
        if template_name in self.templates:
            self.templates[template_name].update(custom_messages)

    # Helper methods

    def _determine_performance_level(self, percentage: float) -> str:
        """Determine performance level from score"""
        if percentage >= 90:
            return 'excellent'
        elif percentage >= 75:
            return 'good'
        elif percentage >= 60:
            return 'satisfactory'
        else:
            return 'needs_improvement'

    def _select_opening(self, performance_level: str) -> str:
        """Select opening based on performance level"""
        import random
        openings = self.templates[performance_level]['opening']
        return random.choice(openings)

    def _get_performance_opening(self, percentage: float) -> str:
        """Get opening message based on percentage"""
        level = self._determine_performance_level(percentage)
        return self._select_opening(level)

    def _identify_strengths(self, performance: Dict) -> List[str]:
        """Identify student strengths from performance data"""
        strengths = []

        # Check for identified strengths in performance data
        if 'strengths' in performance:
            for strength in performance['strengths']:
                if strength in self.strength_patterns:
                    strengths.append(self.strength_patterns[strength])

        # Check for high-performing criteria
        if 'criterion_scores' in performance:
            for criterion in performance['criterion_scores']:
                if criterion.get('percentage', 0) >= 90:
                    strengths.append(f"Strong performance on {criterion['criterion']}")

        # Default strength if none identified
        if not strengths and performance.get('percentage', 0) >= 60:
            strengths.append("You demonstrated understanding of the core concepts.")

        return strengths

    def _suggest_improvements(self, performance: Dict) -> List[str]:
        """Suggest improvements based on mistakes"""
        suggestions = []

        # Check for specific mistakes
        mistakes = performance.get('mistakes', [])

        for mistake in mistakes:
            mistake_type = mistake if isinstance(mistake, str) else mistake.get('type')

            if mistake_type in self.mistake_feedback:
                feedback = self.mistake_feedback[mistake_type]
                suggestions.append(feedback['suggestion'])

        # Check for low-performing criteria
        if 'criterion_scores' in performance:
            for criterion in performance['criterion_scores']:
                if criterion.get('percentage', 100) < 60:
                    suggestions.append(
                        f"Focus on improving: {criterion['criterion']}"
                    )

        return suggestions

    def _recommend_resources(self, performance: Dict,
                           question_info: Dict = None) -> List[str]:
        """Recommend learning resources"""
        resources = []

        # Based on mistakes
        mistakes = performance.get('mistakes', [])
        for mistake in mistakes:
            mistake_type = mistake if isinstance(mistake, str) else mistake.get('type')

            if mistake_type in self.mistake_feedback:
                resources.extend(self.mistake_feedback[mistake_type]['resources'])

        # Based on question topic
        if question_info and 'topic' in question_info:
            topic = question_info['topic']
            resources.append(f"Review: {topic} fundamentals")

        # Remove duplicates
        return list(set(resources))

    def _generate_closing(self, performance_level: str,
                         percentage: float) -> str:
        """Generate closing message"""
        closing = self.templates[performance_level]['encouragement']

        if percentage >= 90:
            return closing + " You've mastered this material!"
        elif percentage >= 75:
            return closing + " You're doing great!"
        elif percentage >= 60:
            return closing + " You're on your way!"
        else:
            return closing + " I'm here to help you succeed!"

    def _compile_feedback(self, opening: str, strengths: List[str],
                         improvements: List[str], resources: List[str],
                         closing: str) -> str:
        """Compile all feedback components into formatted text"""
        parts = [opening]

        if strengths:
            parts.append("\n\nStrengths:")
            for strength in strengths:
                parts.append(f"  ✅ {strength}")

        if improvements:
            parts.append("\n\nAreas for Improvement:")
            for improvement in improvements:
                parts.append(f"  💡 {improvement}")

        if resources:
            parts.append("\n\nRecommended Resources:")
            for resource in resources:
                parts.append(f"  📚 {resource}")

        parts.append("\n\n" + closing)

        return "\n".join(parts)


# Example usage
if __name__ == "__main__":
    generator = FeedbackGenerator(tone='encouraging')

    print("\n📝 Feedback Generator - Personalized Student Feedback")
    print("="*60)

    # Example 1: High-performing student
    print("\n🌟 Example 1: High-Performing Student")
    print("-"*60)

    high_performance = {
        'percentage': 92,
        'mistakes': [],
        'strengths': ['correct_method', 'clear_work', 'complete_answer']
    }

    feedback1 = generator.generate_feedback(high_performance)
    print(feedback1['feedback_text'])

    # Example 2: Student with sign error
    print("\n\n⚠️ Example 2: Student with Sign Error")
    print("-"*60)

    sign_error_performance = {
        'percentage': 70,
        'mistakes': ['sign_error'],
        'strengths': ['correct_method', 'correct_setup'],
        'criterion_scores': [
            {'criterion': 'Method', 'earned_points': 3, 'max_points': 3, 'percentage': 100},
            {'criterion': 'Calculation', 'earned_points': 2, 'max_points': 3, 'percentage': 67}
        ]
    }

    feedback2 = generator.generate_feedback(sign_error_performance)
    print(feedback2['feedback_text'])

    # Example 3: Rubric-based feedback
    print("\n\n📋 Example 3: Rubric-Based Feedback")
    print("-"*60)

    rubric_results = {
        'percentage': 75,
        'criterion_scores': [
            {'criterion': 'Problem Understanding', 'earned_points': 2, 'max_points': 2, 'percentage': 100},
            {'criterion': 'Method Selection', 'earned_points': 2.5, 'max_points': 3, 'percentage': 83},
            {'criterion': 'Calculations', 'earned_points': 2, 'max_points': 3, 'percentage': 67},
            {'criterion': 'Final Answer', 'earned_points': 1, 'max_points': 2, 'percentage': 50}
        ]
    }

    feedback3 = generator.generate_rubric_feedback(rubric_results)
    print(feedback3)

    # Example 4: Progress-based feedback
    print("\n\n📈 Example 4: Progress-Based Feedback")
    print("-"*60)

    progress_feedback = generator.generate_progress_feedback(
        current_score=85,
        previous_scores=[65, 70, 72, 75]
    )
    print(progress_feedback)

    # Example 5: Comparative feedback
    print("\n\n📊 Example 5: Comparative Feedback (vs Class)")
    print("-"*60)

    comparative_feedback = generator.generate_comparative_feedback(
        student_score=88,
        class_average=75,
        class_std_dev=10
    )
    print(comparative_feedback)

    print("\n="*60)
    print("✅ Feedback generator examples complete!")
