"""
Metrics Calculator Module
Calculates performance metrics for students and assessments
Provides accuracy, precision, recall, F1-score, and advanced analytics
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
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MetricsCalculator:
    """
    Calculates educational performance metrics
    Provides comprehensive analytics for students and assessments
    """

    def __init__(self):
        """Initialize metrics calculator"""
        self.metric_definitions = {
            'accuracy': 'Percentage of correct answers',
            'precision': 'True positives / (True positives + False positives)',
            'recall': 'True positives / (True positives + False negatives)',
            'f1_score': 'Harmonic mean of precision and recall',
            'learning_velocity': 'Rate of improvement over time',
            'consistency': 'Standard deviation of performance'
        }

    def calculate_accuracy(self, responses: List[Dict]) -> float:
        """
        Calculate overall accuracy

        Args:
            responses: List of student responses with 'is_correct' field

        Returns:
            Accuracy as float (0-1)
        """
        if not responses:
            return 0.0

        correct = sum(1 for r in responses if r.get('is_correct', False))
        total = len(responses)

        return correct / total if total > 0 else 0.0

    def calculate_precision_recall_f1(self, responses: List[Dict],
                                     positive_class: str = 'correct') -> Dict:
        """
        Calculate precision, recall, and F1-score

        Args:
            responses: List of responses with predictions and actuals
            positive_class: What constitutes a positive result

        Returns:
            Dict with precision, recall, f1_score
        """
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0

        for response in responses:
            actual = response.get('is_correct', False)
            predicted = response.get('predicted_correct', actual)

            if predicted and actual:
                true_positives += 1
            elif predicted and not actual:
                false_positives += 1
            elif not predicted and actual:
                false_negatives += 1
            else:
                true_negatives += 1

        # Calculate precision
        precision = (true_positives / (true_positives + false_positives)
                    if (true_positives + false_positives) > 0 else 0.0)

        # Calculate recall
        recall = (true_positives / (true_positives + false_negatives)
                 if (true_positives + false_negatives) > 0 else 0.0)

        # Calculate F1-score
        f1_score = (2 * precision * recall / (precision + recall)
                   if (precision + recall) > 0 else 0.0)

        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'true_negatives': true_negatives
        }

    def calculate_learning_velocity(self, performance_history: pd.DataFrame,
                                   time_column: str = 'timestamp',
                                   score_column: str = 'accuracy') -> float:
        """
        Calculate learning velocity (rate of improvement)

        Args:
            performance_history: DataFrame with timestamps and scores
            time_column: Name of timestamp column
            score_column: Name of score column

        Returns:
            Learning velocity (change per day)
        """
        if len(performance_history) < 2:
            return 0.0

        # Ensure sorted by time
        df = performance_history.sort_values(time_column).copy()

        # Calculate time differences in days
        if time_column in df.columns:
            df['days'] = (df[time_column] - df[time_column].iloc[0]).dt.total_seconds() / 86400
        else:
            # If no timestamp, assume sequential days
            df['days'] = range(len(df))

        # Simple linear regression slope
        if len(df) >= 2:
            x = df['days'].values
            y = df[score_column].values

            # Calculate slope
            n = len(x)
            slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)

            return slope

        return 0.0

    def calculate_consistency(self, scores: List[float]) -> Dict:
        """
        Calculate performance consistency

        Args:
            scores: List of performance scores

        Returns:
            Dict with consistency metrics
        """
        if not scores:
            return {
                'consistency_score': 0.0,
                'std_dev': 0.0,
                'variance': 0.0,
                'coefficient_variation': 0.0
            }

        mean_score = np.mean(scores)
        std_dev = np.std(scores)
        variance = np.var(scores)

        # Coefficient of variation (normalized std dev)
        cv = std_dev / mean_score if mean_score > 0 else 0

        # Consistency score (0-1, where 1 is most consistent)
        consistency_score = 1 - min(cv, 1.0)

        return {
            'consistency_score': consistency_score,
            'std_dev': std_dev,
            'variance': variance,
            'coefficient_variation': cv,
            'mean': mean_score,
            'min': min(scores),
            'max': max(scores)
        }

    def calculate_topic_metrics(self, responses: List[Dict],
                               topic_field: str = 'topic') -> Dict:
        """
        Calculate performance metrics by topic

        Args:
            responses: List of responses with topic information
            topic_field: Field name containing topic

        Returns:
            Dict of metrics per topic
        """
        topic_metrics = {}

        # Group by topic
        topics = {}
        for response in responses:
            topic = response.get(topic_field, 'Unknown')
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(response)

        # Calculate metrics for each topic
        for topic, topic_responses in topics.items():
            accuracy = self.calculate_accuracy(topic_responses)

            topic_metrics[topic] = {
                'accuracy': accuracy,
                'total_questions': len(topic_responses),
                'correct': sum(1 for r in topic_responses if r.get('is_correct', False)),
                'performance_level': self._categorize_performance(accuracy)
            }

        return topic_metrics

    def calculate_difficulty_metrics(self, responses: List[Dict],
                                    difficulty_field: str = 'difficulty') -> Dict:
        """
        Calculate performance metrics by difficulty level

        Args:
            responses: List of responses with difficulty information
            difficulty_field: Field name containing difficulty

        Returns:
            Dict of metrics per difficulty level
        """
        difficulty_metrics = {}

        # Group by difficulty
        difficulties = {}
        for response in responses:
            difficulty = response.get(difficulty_field, 'Unknown')
            if difficulty not in difficulties:
                difficulties[difficulty] = []
            difficulties[difficulty].append(response)

        # Calculate metrics for each difficulty
        for difficulty, diff_responses in difficulties.items():
            accuracy = self.calculate_accuracy(diff_responses)

            difficulty_metrics[difficulty] = {
                'accuracy': accuracy,
                'total_questions': len(diff_responses),
                'correct': sum(1 for r in diff_responses if r.get('is_correct', False)),
                'average_time': np.mean([r.get('time_spent', 0) for r in diff_responses])
            }

        return difficulty_metrics

    def calculate_time_metrics(self, responses: List[Dict]) -> Dict:
        """
        Calculate time-based performance metrics

        Args:
            responses: List of responses with time information

        Returns:
            Dict with time-based metrics
        """
        times = [r.get('time_spent', 0) for r in responses if 'time_spent' in r]

        if not times:
            return {
                'average_time': 0,
                'median_time': 0,
                'min_time': 0,
                'max_time': 0
            }

        return {
            'average_time': np.mean(times),
            'median_time': np.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev_time': np.std(times),
            'time_efficiency': self._calculate_time_efficiency(responses)
        }

    def calculate_comprehensive_metrics(self, student_data: Dict) -> Dict:
        """
        Calculate comprehensive metrics for a student

        Args:
            student_data: Dict containing student responses and history

        Returns:
            Comprehensive metrics report
        """
        responses = student_data.get('responses', [])
        performance_history = student_data.get('performance_history', pd.DataFrame())

        metrics = {
            'overall_accuracy': self.calculate_accuracy(responses),
            'topic_metrics': self.calculate_topic_metrics(responses),
            'difficulty_metrics': self.calculate_difficulty_metrics(responses),
            'time_metrics': self.calculate_time_metrics(responses),
            'total_questions_attempted': len(responses)
        }

        # Add learning velocity if history available
        if not performance_history.empty and 'accuracy' in performance_history.columns:
            metrics['learning_velocity'] = self.calculate_learning_velocity(performance_history)

        # Add consistency metrics
        if len(responses) > 0:
            scores = [1.0 if r.get('is_correct', False) else 0.0 for r in responses]
            metrics['consistency'] = self.calculate_consistency(scores)

        # Add performance classification
        metrics['performance_classification'] = self._classify_performance(metrics)

        return metrics

    def compare_metrics(self, metrics1: Dict, metrics2: Dict,
                       metric_name: str) -> Dict:
        """
        Compare two metric sets

        Args:
            metrics1: First metric set
            metrics2: Second metric set
            metric_name: Name of metric to compare

        Returns:
            Comparison results
        """
        value1 = metrics1.get(metric_name, 0)
        value2 = metrics2.get(metric_name, 0)

        difference = value2 - value1
        percent_change = (difference / value1 * 100) if value1 > 0 else 0

        return {
            'metric': metric_name,
            'value1': value1,
            'value2': value2,
            'difference': difference,
            'percent_change': percent_change,
            'improved': difference > 0
        }

    def calculate_percentile(self, student_score: float,
                           all_scores: List[float]) -> float:
        """
        Calculate student's percentile rank

        Args:
            student_score: Student's score
            all_scores: List of all scores

        Returns:
            Percentile (0-100)
        """
        if not all_scores:
            return 0.0

        below = sum(1 for score in all_scores if score < student_score)
        equal = sum(1 for score in all_scores if score == student_score)

        percentile = (below + 0.5 * equal) / len(all_scores) * 100

        return percentile

    def aggregate_class_metrics(self, student_metrics: List[Dict]) -> Dict:
        """
        Aggregate metrics across a class

        Args:
            student_metrics: List of individual student metrics

        Returns:
            Aggregated class metrics
        """
        if not student_metrics:
            return {}

        # Extract accuracies
        accuracies = [m.get('overall_accuracy', 0) for m in student_metrics]

        return {
            'class_average': np.mean(accuracies),
            'class_median': np.median(accuracies),
            'class_std_dev': np.std(accuracies),
            'class_min': min(accuracies),
            'class_max': max(accuracies),
            'total_students': len(student_metrics),
            'students_above_70': sum(1 for a in accuracies if a >= 0.70),
            'students_below_50': sum(1 for a in accuracies if a < 0.50),
            'distribution': self._calculate_distribution(accuracies)
        }

    # Helper methods

    def _categorize_performance(self, accuracy: float) -> str:
        """Categorize performance level"""
        if accuracy >= 0.90:
            return 'Excellent'
        elif accuracy >= 0.75:
            return 'Good'
        elif accuracy >= 0.60:
            return 'Satisfactory'
        elif accuracy >= 0.50:
            return 'Needs Improvement'
        else:
            return 'Struggling'

    def _calculate_time_efficiency(self, responses: List[Dict]) -> float:
        """Calculate time efficiency (correctness per unit time)"""
        if not responses:
            return 0.0

        efficiency_scores = []
        for response in responses:
            time = response.get('time_spent', 1)  # Avoid division by zero
            correct = 1.0 if response.get('is_correct', False) else 0.0
            efficiency = correct / max(time, 1)  # Score per second
            efficiency_scores.append(efficiency)

        return np.mean(efficiency_scores) if efficiency_scores else 0.0

    def _classify_performance(self, metrics: Dict) -> str:
        """Classify overall performance"""
        accuracy = metrics.get('overall_accuracy', 0)
        velocity = metrics.get('learning_velocity', 0)

        if accuracy >= 0.85 and velocity >= 0:
            return 'High Performer'
        elif accuracy >= 0.70 and velocity > 0.01:
            return 'Improving'
        elif accuracy >= 0.70 and velocity <= 0:
            return 'Stable'
        elif accuracy < 0.60 and velocity < 0:
            return 'Declining'
        else:
            return 'Developing'

    def _calculate_distribution(self, scores: List[float]) -> Dict:
        """Calculate score distribution"""
        return {
            '90-100%': sum(1 for s in scores if s >= 0.90),
            '75-89%': sum(1 for s in scores if 0.75 <= s < 0.90),
            '60-74%': sum(1 for s in scores if 0.60 <= s < 0.75),
            '50-59%': sum(1 for s in scores if 0.50 <= s < 0.60),
            'Below 50%': sum(1 for s in scores if s < 0.50)
        }


# Example usage
if __name__ == "__main__":
    calculator = MetricsCalculator()

    print("\n📊 Metrics Calculator - Performance Analytics")
    print("="*60)

    # Example 1: Calculate accuracy
    print("\n📈 Example 1: Calculate Accuracy")
    print("-"*60)

    responses = [
        {'is_correct': True, 'topic': 'algebra'},
        {'is_correct': True, 'topic': 'algebra'},
        {'is_correct': False, 'topic': 'geometry'},
        {'is_correct': True, 'topic': 'geometry'},
        {'is_correct': True, 'topic': 'algebra'}
    ]

    accuracy = calculator.calculate_accuracy(responses)
    print(f"Overall Accuracy: {accuracy:.1%}")

    # Example 2: Topic metrics
    print("\n\n📊 Example 2: Topic-Based Metrics")
    print("-"*60)

    topic_metrics = calculator.calculate_topic_metrics(responses)
    for topic, metrics in topic_metrics.items():
        print(f"\n{topic}:")
        print(f"  Accuracy: {metrics['accuracy']:.1%}")
        print(f"  Questions: {metrics['total_questions']}")
        print(f"  Performance: {metrics['performance_level']}")

    # Example 3: Learning velocity
    print("\n\n📈 Example 3: Learning Velocity")
    print("-"*60)

    performance_history = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=7, freq='D'),
        'accuracy': [0.60, 0.65, 0.68, 0.72, 0.75, 0.78, 0.80]
    })

    velocity = calculator.calculate_learning_velocity(performance_history)
    print(f"Learning Velocity: {velocity:+.3f} per day")
    print(f"Interpretation: {'Improving' if velocity > 0 else 'Declining'}")

    # Example 4: Consistency
    print("\n\n📊 Example 4: Performance Consistency")
    print("-"*60)

    scores = [0.85, 0.88, 0.82, 0.87, 0.86, 0.84, 0.88]
    consistency = calculator.calculate_consistency(scores)

    print(f"Consistency Score: {consistency['consistency_score']:.2f}")
    print(f"Mean: {consistency['mean']:.2f}")
    print(f"Std Dev: {consistency['std_dev']:.3f}")
    print(f"Range: {consistency['min']:.2f} - {consistency['max']:.2f}")

    # Example 5: Comprehensive metrics
    print("\n\n📊 Example 5: Comprehensive Student Metrics")
    print("-"*60)

    student_data = {
        'responses': [
            {'is_correct': True, 'topic': 'algebra', 'difficulty': 'Medium', 'time_spent': 120},
            {'is_correct': True, 'topic': 'algebra', 'difficulty': 'Hard', 'time_spent': 180},
            {'is_correct': False, 'topic': 'geometry', 'difficulty': 'Medium', 'time_spent': 150},
            {'is_correct': True, 'topic': 'geometry', 'difficulty': 'Easy', 'time_spent': 90}
        ],
        'performance_history': performance_history
    }

    comprehensive = calculator.calculate_comprehensive_metrics(student_data)

    print(f"Overall Accuracy: {comprehensive['overall_accuracy']:.1%}")
    print(f"Learning Velocity: {comprehensive['learning_velocity']:+.3f} per day")
    print(f"Consistency: {comprehensive['consistency']['consistency_score']:.2f}")
    print(f"Performance Classification: {comprehensive['performance_classification']}")
    print(f"Average Time: {comprehensive['time_metrics']['average_time']:.0f} seconds")

    print("\n="*60)
    print("✅ Metrics calculator examples complete!")
