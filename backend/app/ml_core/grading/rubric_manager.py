"""
Rubric Manager Module - FIXED VERSION
Manages grading rubrics for assignments and provides consistent grading criteria
Helps educators create, apply, and analyze rubric-based assessments
FIXED: Proper handling of criteria list structure
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
import json
import warnings
warnings.filterwarnings('ignore')


class RubricManager:
    """
    Manages grading rubrics for educational assessments
    Provides consistent, transparent grading criteria for educators
    FIXED: Proper criteria list handling
    """

    def __init__(self):
        # Standard rubric templates (stored as lists for consistency)
        self.rubric_templates = {
            'bloom_taxonomy': [
                {'name': 'Remember', 'points': 1, 'description': 'Recall facts and basic concepts'},
                {'name': 'Understand', 'points': 2, 'description': 'Explain ideas or concepts'},
                {'name': 'Apply', 'points': 3, 'description': 'Use information in new situations'},
                {'name': 'Analyze', 'points': 4, 'description': 'Draw connections among ideas'},
                {'name': 'Evaluate', 'points': 5, 'description': 'Justify decisions or positions'},
                {'name': 'Create', 'points': 6, 'description': 'Produce new or original work'}
            ],
            'difficulty': [
                {'name': 'Easy', 'points': 1, 'description': 'Basic recall and simple application'},
                {'name': 'Medium', 'points': 2, 'description': 'Moderate complexity and reasoning'},
                {'name': 'Hard', 'points': 3, 'description': 'Complex problem-solving'},
                {'name': 'Advanced', 'points': 4, 'description': 'Advanced synthesis and creativity'}
            ],
            'short_answer': [
                {'name': 'Correct Concept', 'points': 0.4, 'description': 'Core concept identified'},
                {'name': 'Proper Application', 'points': 0.3, 'description': 'Applied correctly'},
                {'name': 'Clear Explanation', 'points': 0.2, 'description': 'Well explained'},
                {'name': 'Supporting Details', 'points': 0.1, 'description': 'Relevant details included'}
            ],
            'problem_solving': [
                {'name': 'Problem Understanding', 'points': 0.2, 'description': 'Understood the problem'},
                {'name': 'Approach/Method', 'points': 0.3, 'description': 'Used appropriate method'},
                {'name': 'Execution', 'points': 0.3, 'description': 'Correct calculations/steps'},
                {'name': 'Final Answer', 'points': 0.2, 'description': 'Correct final result'}
            ]
        }

        # Rubric library (custom rubrics)
        self.custom_rubrics = {}

    def create_rubric(self, rubric_name: str, 
                     criteria: List[Dict],
                     total_points: float = None) -> Dict:
        """
        Create a custom grading rubric

        Args:
            rubric_name: Name for the rubric
            criteria: List of criterion dicts with 'name', 'points', 'description'
            total_points: Optional total points (calculated if not provided)

        Returns:
            Created rubric structure
        """
        # Validate criteria
        if not criteria:
            return {'error': 'At least one criterion required'}

        # Calculate total points if not provided
        if total_points is None:
            total_points = sum(c.get('points', 0) for c in criteria)

        # Build rubric
        rubric = {
            'name': rubric_name,
            'total_points': total_points,
            'criteria': criteria,  # Store as list
            'created_date': pd.Timestamp.now().isoformat(),
            'type': 'custom'
        }

        # Store in library
        self.custom_rubrics[rubric_name] = rubric

        return rubric

    def get_rubric(self, rubric_name: str, 
                   template: str = None) -> Dict:
        """
        Get a rubric by name or template

        Args:
            rubric_name: Name of custom rubric
            template: Name of template to use

        Returns:
            Rubric structure
        """
        # Check custom rubrics first
        if rubric_name in self.custom_rubrics:
            return self.custom_rubrics[rubric_name]

        # Check templates
        if template and template in self.rubric_templates:
            criteria = self.rubric_templates[template]
            total_points = sum(c.get('points', 0) for c in criteria)
            return {
                'name': template,
                'type': 'template',
                'criteria': criteria,
                'total_points': total_points
            }

        return {'error': f'Rubric {rubric_name} not found'}

    def apply_rubric(self, rubric: Dict,
                    student_response: Dict,
                    criterion_scores: Dict = None) -> Dict:
        """
        Apply a rubric to score a student response
        FIXED: Properly handles criteria as list

        Args:
            rubric: Rubric to apply
            student_response: Student's answer/work
            criterion_scores: Manual scores for each criterion

        Returns:
            Scoring results with breakdown
        """
        if 'error' in rubric:
            return rubric

        results = {
            'rubric_name': rubric['name'],
            'total_points': rubric.get('total_points', 0),
            'earned_points': 0,
            'criterion_scores': [],
            'percentage': 0
        }

        criteria = rubric.get('criteria', [])

        # FIXED: Iterate over criteria list
        for criterion in criteria:
            criterion_name = criterion.get('name', 'Unknown')
            max_points = criterion.get('points', 0)
            description = criterion.get('description', '')

            # Get score for this criterion
            if criterion_scores and criterion_name in criterion_scores:
                earned = criterion_scores[criterion_name]
            else:
                # Auto-scoring logic (simplified)
                earned = self._auto_score_criterion(
                    criterion_name, criterion, student_response
                )

            # Cap at max points
            earned = min(earned, max_points)

            results['criterion_scores'].append({
                'criterion': criterion_name,
                'max_points': max_points,
                'earned_points': earned,
                'percentage': (earned / max_points * 100) if max_points > 0 else 0,
                'description': description
            })

            results['earned_points'] += earned

        # Calculate overall percentage
        if results['total_points'] > 0:
            results['percentage'] = results['earned_points'] / results['total_points'] * 100

        return results

    def analyze_rubric_performance(self, rubric_name: str,
                                  student_scores: List[Dict]) -> Dict:
        """
        Analyze how students performed across rubric criteria

        Args:
            rubric_name: Name of rubric
            student_scores: List of scoring results from apply_rubric

        Returns:
            Analysis of criterion performance
        """
        if not student_scores:
            return {'error': 'No scores to analyze'}

        # Aggregate by criterion
        criterion_data = {}

        for score in student_scores:
            for criterion in score.get('criterion_scores', []):
                crit_name = criterion['criterion']

                if crit_name not in criterion_data:
                    criterion_data[crit_name] = {
                        'scores': [],
                        'max_points': criterion['max_points'],
                        'description': criterion['description']
                    }

                criterion_data[crit_name]['scores'].append(criterion['earned_points'])

        # Calculate statistics
        analysis = {
            'rubric_name': rubric_name,
            'num_students': len(student_scores),
            'criteria_analysis': []
        }

        for crit_name, data in criterion_data.items():
            scores = data['scores']
            max_points = data['max_points']

            analysis['criteria_analysis'].append({
                'criterion': crit_name,
                'description': data['description'],
                'max_points': max_points,
                'avg_score': np.mean(scores),
                'avg_percentage': np.mean(scores) / max_points * 100 if max_points > 0 else 0,
                'std_dev': np.std(scores),
                'min_score': np.min(scores),
                'max_score': np.max(scores),
                'students_full_credit': sum(1 for s in scores if s >= max_points),
                'students_no_credit': sum(1 for s in scores if s == 0),
                'difficulty_indicator': self._calculate_difficulty_indicator(scores, max_points)
            })

        # Sort by difficulty
        analysis['criteria_analysis'].sort(
            key=lambda x: x['avg_percentage']
        )

        # Add insights
        analysis['insights'] = self._generate_rubric_insights(analysis['criteria_analysis'])

        return analysis

    def compare_rubrics(self, rubric1_scores: List[Dict],
                       rubric2_scores: List[Dict],
                       rubric1_name: str,
                       rubric2_name: str) -> Dict:
        """
        Compare student performance across different rubrics

        Args:
            rubric1_scores: Scores using first rubric
            rubric2_scores: Scores using second rubric
            rubric1_name: Name of first rubric
            rubric2_name: Name of second rubric

        Returns:
            Comparison analysis
        """
        # Calculate average scores
        avg1 = np.mean([s['percentage'] for s in rubric1_scores])
        avg2 = np.mean([s['percentage'] for s in rubric2_scores])

        std1 = np.std([s['percentage'] for s in rubric1_scores])
        std2 = np.std([s['percentage'] for s in rubric2_scores])

        return {
            'rubric1': {
                'name': rubric1_name,
                'avg_percentage': avg1,
                'std_dev': std1,
                'num_scores': len(rubric1_scores)
            },
            'rubric2': {
                'name': rubric2_name,
                'avg_percentage': avg2,
                'std_dev': std2,
                'num_scores': len(rubric2_scores)
            },
            'comparison': {
                'difference': avg1 - avg2,
                'interpretation': self._interpret_rubric_difference(avg1, avg2, std1, std2)
            }
        }

    def generate_rubric_report(self, rubric_name: str,
                             analysis: Dict) -> str:
        """
        Generate human-readable rubric analysis report

        Args:
            rubric_name: Name of rubric
            analysis: Analysis from analyze_rubric_performance

        Returns:
            Formatted report text
        """
        report = [
            f"Rubric Analysis Report: {rubric_name}",
            "=" * 60,
            f"Students Assessed: {analysis['num_students']}",
            "",
            "Criterion Performance:",
            "-" * 60
        ]

        for criterion in analysis['criteria_analysis']:
            report.append(f"  Criterion: {criterion['criterion']}")
            report.append(f"  Description: {criterion['description']}")
            report.append(f"  Average Score: {criterion['avg_score']:.2f}/{criterion['max_points']} ({criterion['avg_percentage']:.1f}%)")
            report.append(f"  Difficulty: {criterion['difficulty_indicator']}")
            report.append(f"  Full Credit: {criterion['students_full_credit']} students")
            report.append(f"  No Credit: {criterion['students_no_credit']} students")

        if analysis.get('insights'):
            report.append(" " + "-" * 60)
            report.append("Key Insights:")
            for insight in analysis['insights']:
                report.append(f"  • {insight}")

        return "\n".join(report)

    def export_rubric(self, rubric_name: str, 
                     format: str = 'json') -> str:
        """
        Export rubric for sharing or backup

        Args:
            rubric_name: Name of rubric to export
            format: Export format ('json', 'text')

        Returns:
            Exported rubric string
        """
        rubric = self.get_rubric(rubric_name)

        if 'error' in rubric:
            return json.dumps(rubric)

        if format == 'json':
            return json.dumps(rubric, indent=2)
        elif format == 'text':
            return self._format_rubric_text(rubric)
        else:
            return json.dumps({'error': f'Unknown format: {format}'})

    def import_rubric(self, rubric_json: str) -> Dict:
        """
        Import rubric from JSON

        Args:
            rubric_json: JSON string of rubric

        Returns:
            Import status
        """
        try:
            rubric = json.loads(rubric_json)
            rubric_name = rubric.get('name', 'imported_rubric')
            self.custom_rubrics[rubric_name] = rubric
            return {'status': 'success', 'rubric_name': rubric_name}
        except json.JSONDecodeError as e:
            return {'status': 'error', 'message': str(e)}

    # Helper methods

    def _auto_score_criterion(self, criterion_name: str,
                             criterion_data: Dict,
                             student_response: Dict) -> float:
        """Auto-score a criterion (simplified)"""
        # This is a placeholder - in production, use NLP/ML models
        max_points = criterion_data.get('points', 0)

        # Check if correct answer provided
        is_correct = student_response.get('is_correct', False)

        if is_correct:
            return max_points
        else:
            # Simplified partial credit logic
            return max_points * 0.5

    def _calculate_difficulty_indicator(self, scores: List[float],
                                       max_points: float) -> str:
        """Calculate difficulty indicator for criterion"""
        if not scores or max_points == 0:
            return 'Unknown'

        avg_percentage = np.mean(scores) / max_points * 100

        if avg_percentage >= 80:
            return 'Easy'
        elif avg_percentage >= 60:
            return 'Moderate'
        elif avg_percentage >= 40:
            return 'Challenging'
        else:
            return 'Difficult'

    def _generate_rubric_insights(self, criteria_analysis: List[Dict]) -> List[str]:
        """Generate insights from rubric analysis"""
        insights = []

        # Find easiest and hardest criteria
        if criteria_analysis:
            easiest = criteria_analysis[-1]  # Sorted ascending by avg_percentage
            hardest = criteria_analysis[0]

            insights.append(
                f"Easiest criterion: {easiest['criterion']} ({easiest['avg_percentage']:.1f}% avg)"
            )
            insights.append(
                f"Hardest criterion: {hardest['criterion']} ({hardest['avg_percentage']:.1f}% avg)"
            )

            # Find criteria with high variance
            high_variance = [c for c in criteria_analysis if c['std_dev'] > 1.0]
            if high_variance:
                insights.append(
                    f"{len(high_variance)} criteria show high score variance (inconsistent student performance)"
                )

            # Find criteria where many students got no credit
            no_credit = [c for c in criteria_analysis 
                        if c['students_no_credit'] > len(criteria_analysis) * 0.3]
            if no_credit:
                insights.append(
                    f"{len(no_credit)} criteria where >30% of students earned no credit"
                )

        return insights

    def _interpret_rubric_difference(self, avg1: float, avg2: float,
                                    std1: float, std2: float) -> str:
        """Interpret difference between two rubrics"""
        diff = abs(avg1 - avg2)

        if diff < 5:
            return "Rubrics produced similar results"
        elif diff < 15:
            return "Rubrics produced moderately different results"
        else:
            return "Rubrics produced significantly different results"

    def _format_rubric_text(self, rubric: Dict) -> str:
        """Format rubric as plain text"""
        lines = [
            f"Rubric: {rubric['name']}",
            f"Total Points: {rubric.get('total_points', 'N/A')}",
            "",
            "Criteria:"
        ]

        # FIXED: Handle criteria as list
        for criterion in rubric.get('criteria', []):
            name = criterion.get('name', 'Unknown')
            points = criterion.get('points', 0)
            desc = criterion.get('description', '')
            lines.append(f"  - {name}: {points} points")
            if desc:
                lines.append(f"    {desc}")

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    manager = RubricManager()

    print("\n📝 Rubric Manager - Grading Assistance (FIXED)")
    print("="*60)

    # Example 1: Create custom rubric
    print("\n📋 Example 1: Creating Custom Rubric")
    print("-"*60)

    problem_solving_criteria = [
        {'name': 'Problem Understanding', 'points': 2, 'description': 'Correctly identified problem'},
        {'name': 'Solution Method', 'points': 3, 'description': 'Used appropriate approach'},
        {'name': 'Calculations', 'points': 3, 'description': 'Accurate calculations'},
        {'name': 'Final Answer', 'points': 2, 'description': 'Correct final result'}
    ]

    rubric = manager.create_rubric(
        'Physics Problem Solving',
        problem_solving_criteria,
        total_points=10
    )

    print(f"Created rubric: {rubric['name']}")
    print(f"Total points: {rubric['total_points']}")
    print(f"Criteria: {len(rubric['criteria'])}")
    for criterion in rubric['criteria']:
        print(f"  • {criterion['name']}: {criterion['points']} pts - {criterion['description']}")

    # Example 2: Apply rubric
    print("\n\n📊 Example 2: Applying Rubric to Student Work")
    print("-"*60)

    student_response = {'is_correct': False, 'work_shown': True}
    criterion_scores = {
        'Problem Understanding': 2.0,
        'Solution Method': 2.5,
        'Calculations': 1.5,
        'Final Answer': 0.0
    }

    result = manager.apply_rubric(
        rubric,
        student_response,
        criterion_scores
    )

    print(f"Total Score: {result['earned_points']}/{result['total_points']} ({result['percentage']:.1f}%)")
    print("\nCriterion Breakdown:")
    for criterion in result['criterion_scores']:
        print(f"  • {criterion['criterion']}: {criterion['earned_points']}/{criterion['max_points']} ({criterion['percentage']:.0f}%)")

    # Example 3: Analyze rubric performance
    print("\n\n📈 Example 3: Rubric Performance Analysis")
    print("-"*60)

    # Simulate multiple student scores
    student_scores = [
        {'earned_points': 6, 'total_points': 10, 'percentage': 60,
         'criterion_scores': [
             {'criterion': 'Problem Understanding', 'earned_points': 2.0, 'max_points': 2, 'percentage': 100, 'description': 'Correctly identified problem'},
             {'criterion': 'Solution Method', 'earned_points': 2.5, 'max_points': 3, 'percentage': 83, 'description': 'Used appropriate approach'},
             {'criterion': 'Calculations', 'earned_points': 1.5, 'max_points': 3, 'percentage': 50, 'description': 'Accurate calculations'},
             {'criterion': 'Final Answer', 'earned_points': 0.0, 'max_points': 2, 'percentage': 0, 'description': 'Correct final result'}
         ]},
        {'earned_points': 8, 'total_points': 10, 'percentage': 80,
         'criterion_scores': [
             {'criterion': 'Problem Understanding', 'earned_points': 2.0, 'max_points': 2, 'percentage': 100, 'description': 'Correctly identified problem'},
             {'criterion': 'Solution Method', 'earned_points': 3.0, 'max_points': 3, 'percentage': 100, 'description': 'Used appropriate approach'},
             {'criterion': 'Calculations', 'earned_points': 2.0, 'max_points': 3, 'percentage': 67, 'description': 'Accurate calculations'},
             {'criterion': 'Final Answer', 'earned_points': 1.0, 'max_points': 2, 'percentage': 50, 'description': 'Correct final result'}
         ]},
        {'earned_points': 4, 'total_points': 10, 'percentage': 40,
         'criterion_scores': [
             {'criterion': 'Problem Understanding', 'earned_points': 1.5, 'max_points': 2, 'percentage': 75, 'description': 'Correctly identified problem'},
             {'criterion': 'Solution Method', 'earned_points': 1.0, 'max_points': 3, 'percentage': 33, 'description': 'Used appropriate approach'},
             {'criterion': 'Calculations', 'earned_points': 1.5, 'max_points': 3, 'percentage': 50, 'description': 'Accurate calculations'},
             {'criterion': 'Final Answer', 'earned_points': 0.0, 'max_points': 2, 'percentage': 0, 'description': 'Correct final result'}
         ]}
    ]

    analysis = manager.analyze_rubric_performance(
        'Physics Problem Solving',
        student_scores
    )

    print(f"Students Assessed: {analysis['num_students']}")
    print("\nCriterion Performance (sorted by difficulty):")
    for criterion in analysis['criteria_analysis']:
        print(f"\n  {criterion['criterion']}")
        print(f"    Average: {criterion['avg_score']:.2f}/{criterion['max_points']} ({criterion['avg_percentage']:.1f}%)")
        print(f"    Difficulty: {criterion['difficulty_indicator']}")
        print(f"    Full credit: {criterion['students_full_credit']} students")

    print("\nInsights:")
    for insight in analysis['insights']:
        print(f"  • {insight}")

    print("\n="*60)
    print("✅ Rubric manager (FIXED) examples complete!")
