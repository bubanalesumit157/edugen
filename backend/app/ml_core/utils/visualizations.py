"""
Visualization Helpers Module
Prepares data for charts, graphs, and dashboards
Formats metrics for frontend visualization
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


class VisualizationHelpers:
    """
    Prepares data for visualization
    Formats metrics for charts and dashboards
    """

    def __init__(self):
        """Initialize visualization helpers"""
        self.color_schemes = {
            'performance': {
                'excellent': '#4CAF50',  # Green
                'good': '#8BC34A',       # Light green
                'satisfactory': '#FFC107',  # Yellow
                'needs_improvement': '#FF9800',  # Orange
                'struggling': '#F44336'  # Red
            },
            'difficulty': {
                'Easy': '#4CAF50',
                'Medium': '#FFC107',
                'Hard': '#FF5722',
                'Advanced': '#9C27B0'
            }
        }

    def prepare_line_chart(self, performance_history: pd.DataFrame,
                          x_column: str = 'timestamp',
                          y_column: str = 'accuracy',
                          label: str = 'Performance') -> Dict:
        """
        Prepare data for line chart (performance over time)

        Args:
            performance_history: DataFrame with time series data
            x_column: Column for x-axis
            y_column: Column for y-axis
            label: Chart label

        Returns:
            Chart-ready data structure
        """
        if performance_history.empty:
            return {'labels': [], 'datasets': []}

        # Sort by time
        df = performance_history.sort_values(x_column).copy()

        # Format dates for display
        if pd.api.types.is_datetime64_any_dtype(df[x_column]):
            labels = df[x_column].dt.strftime('%Y-%m-%d').tolist()
        else:
            labels = df[x_column].astype(str).tolist()

        # Get values
        values = df[y_column].tolist()

        return {
            'labels': labels,
            'datasets': [{
                'label': label,
                'data': values,
                'borderColor': '#2196F3',
                'backgroundColor': 'rgba(33, 150, 243, 0.1)',
                'tension': 0.4
            }]
        }

    def prepare_bar_chart(self, topic_metrics: Dict,
                         metric_key: str = 'accuracy') -> Dict:
        """
        Prepare data for bar chart (topics or categories)

        Args:
            topic_metrics: Dict of metrics by topic
            metric_key: Which metric to visualize

        Returns:
            Chart-ready data structure
        """
        labels = list(topic_metrics.keys())
        values = [topic_metrics[topic].get(metric_key, 0) for topic in labels]

        # Color by performance level
        colors = []
        for topic in labels:
            performance = topic_metrics[topic].get('performance_level', 'satisfactory')
            color = self._get_performance_color(performance)
            colors.append(color)

        return {
            'labels': labels,
            'datasets': [{
                'label': metric_key.capitalize(),
                'data': values,
                'backgroundColor': colors,
                'borderWidth': 1
            }]
        }

    def prepare_pie_chart(self, distribution: Dict) -> Dict:
        """
        Prepare data for pie chart (distribution)

        Args:
            distribution: Dict with category counts

        Returns:
            Chart-ready data structure
        """
        labels = list(distribution.keys())
        values = list(distribution.values())

        colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']

        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': colors[:len(labels)],
                'borderWidth': 1
            }]
        }

    def prepare_radar_chart(self, topic_metrics: Dict) -> Dict:
        """
        Prepare data for radar chart (multi-dimensional)

        Args:
            topic_metrics: Metrics across multiple topics

        Returns:
            Chart-ready data structure
        """
        labels = list(topic_metrics.keys())
        values = [topic_metrics[topic].get('accuracy', 0) * 100 for topic in labels]

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Performance',
                'data': values,
                'backgroundColor': 'rgba(33, 150, 243, 0.2)',
                'borderColor': '#2196F3',
                'pointBackgroundColor': '#2196F3',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': '#2196F3'
            }]
        }

    def prepare_scatter_plot(self, data_points: List[Dict],
                           x_key: str = 'time_spent',
                           y_key: str = 'accuracy') -> Dict:
        """
        Prepare data for scatter plot

        Args:
            data_points: List of data points with x and y values
            x_key: Key for x-axis value
            y_key: Key for y-axis value

        Returns:
            Chart-ready data structure
        """
        points = [
            {'x': point.get(x_key, 0), 'y': point.get(y_key, 0)}
            for point in data_points
        ]

        return {
            'datasets': [{
                'label': f'{y_key} vs {x_key}',
                'data': points,
                'backgroundColor': '#2196F3',
                'borderColor': '#1976D2'
            }]
        }

    def prepare_heatmap_data(self, data_matrix: List[List[float]],
                           row_labels: List[str],
                           col_labels: List[str]) -> Dict:
        """
        Prepare data for heatmap

        Args:
            data_matrix: 2D array of values
            row_labels: Labels for rows
            col_labels: Labels for columns

        Returns:
            Heatmap-ready data structure
        """
        return {
            'data': data_matrix,
            'row_labels': row_labels,
            'col_labels': col_labels,
            'colorScale': {
                'low': '#F44336',
                'medium': '#FFC107',
                'high': '#4CAF50'
            }
        }

    def prepare_progress_gauge(self, current_value: float,
                              max_value: float = 100,
                              target_value: Optional[float] = None) -> Dict:
        """
        Prepare data for progress gauge/meter

        Args:
            current_value: Current progress value
            max_value: Maximum possible value
            target_value: Optional target value

        Returns:
            Gauge-ready data structure
        """
        percentage = (current_value / max_value * 100) if max_value > 0 else 0

        # Determine color based on percentage
        if percentage >= 90:
            color = '#4CAF50'  # Green
        elif percentage >= 75:
            color = '#8BC34A'  # Light green
        elif percentage >= 60:
            color = '#FFC107'  # Yellow
        else:
            color = '#FF5722'  # Red

        gauge_data = {
            'value': current_value,
            'max': max_value,
            'percentage': percentage,
            'color': color
        }

        if target_value is not None:
            gauge_data['target'] = target_value
            gauge_data['on_track'] = current_value >= target_value

        return gauge_data

    def prepare_trend_indicator(self, current: float,
                               previous: float) -> Dict:
        """
        Prepare trend indicator data

        Args:
            current: Current value
            previous: Previous value

        Returns:
            Trend indicator data
        """
        change = current - previous
        percent_change = (change / previous * 100) if previous > 0 else 0

        return {
            'current': current,
            'previous': previous,
            'change': change,
            'percent_change': percent_change,
            'trend': 'up' if change > 0 else 'down' if change < 0 else 'stable',
            'color': '#4CAF50' if change > 0 else '#F44336' if change < 0 else '#9E9E9E'
        }

    def prepare_comparison_chart(self, student_metrics: Dict,
                                class_average: Dict) -> Dict:
        """
        Prepare student vs class comparison

        Args:
            student_metrics: Individual student metrics
            class_average: Class average metrics

        Returns:
            Comparison chart data
        """
        metrics = ['accuracy', 'consistency', 'learning_velocity']
        labels = ['Accuracy', 'Consistency', 'Learning Velocity']

        student_values = []
        class_values = []

        for metric in metrics:
            student_val = student_metrics.get(metric, 0)
            class_val = class_average.get(metric, 0)

            # Normalize to 0-100 scale
            if metric == 'learning_velocity':
                student_val = min(max(student_val * 100, 0), 100)
                class_val = min(max(class_val * 100, 0), 100)
            else:
                student_val *= 100
                class_val *= 100

            student_values.append(student_val)
            class_values.append(class_val)

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Student',
                    'data': student_values,
                    'backgroundColor': 'rgba(33, 150, 243, 0.6)',
                    'borderColor': '#2196F3'
                },
                {
                    'label': 'Class Average',
                    'data': class_values,
                    'backgroundColor': 'rgba(158, 158, 158, 0.6)',
                    'borderColor': '#9E9E9E'
                }
            ]
        }

    def prepare_timeline_data(self, events: List[Dict]) -> List[Dict]:
        """
        Prepare timeline visualization data

        Args:
            events: List of events with timestamps

        Returns:
            Timeline-ready data
        """
        timeline = []

        for event in sorted(events, key=lambda x: x.get('timestamp', '')):
            timeline.append({
                'timestamp': event.get('timestamp'),
                'title': event.get('title', 'Event'),
                'description': event.get('description', ''),
                'type': event.get('type', 'milestone'),
                'icon': self._get_event_icon(event.get('type', 'milestone'))
            })

        return timeline

    def prepare_leaderboard_data(self, students: List[Dict],
                                metric_key: str = 'overall_accuracy',
                                top_n: int = 10) -> List[Dict]:
        """
        Prepare leaderboard visualization

        Args:
            students: List of student data
            metric_key: Metric to rank by
            top_n: Number of top students to show

        Returns:
            Leaderboard data
        """
        # Sort by metric
        sorted_students = sorted(
            students,
            key=lambda x: x.get(metric_key, 0),
            reverse=True
        )[:top_n]

        leaderboard = []
        for rank, student in enumerate(sorted_students, 1):
            leaderboard.append({
                'rank': rank,
                'student_id': student.get('student_id', 'Unknown'),
                'name': student.get('name', f"Student {student.get('student_id', '')}"),
                'score': student.get(metric_key, 0),
                'badge': self._get_rank_badge(rank)
            })

        return leaderboard

    def prepare_dashboard_summary(self, metrics: Dict) -> Dict:
        """
        Prepare summary cards for dashboard

        Args:
            metrics: Comprehensive metrics

        Returns:
            Dashboard card data
        """
        cards = []

        # Overall accuracy card
        cards.append({
            'title': 'Overall Accuracy',
            'value': f"{metrics.get('overall_accuracy', 0):.1%}",
            'trend': self.prepare_trend_indicator(
                metrics.get('overall_accuracy', 0),
                metrics.get('previous_accuracy', 0)
            ) if 'previous_accuracy' in metrics else None,
            'icon': '📊',
            'color': self._get_performance_color_from_value(metrics.get('overall_accuracy', 0))
        })

        # Learning velocity card
        if 'learning_velocity' in metrics:
            cards.append({
                'title': 'Learning Velocity',
                'value': f"{metrics['learning_velocity']:+.3f}/day",
                'icon': '📈',
                'color': '#4CAF50' if metrics['learning_velocity'] > 0 else '#F44336'
            })

        # Consistency card
        if 'consistency' in metrics:
            consistency_score = metrics['consistency'].get('consistency_score', 0)
            cards.append({
                'title': 'Consistency',
                'value': f"{consistency_score:.2f}",
                'icon': '🎯',
                'color': self._get_performance_color_from_value(consistency_score)
            })

        # Total questions card
        cards.append({
            'title': 'Questions Attempted',
            'value': str(metrics.get('total_questions_attempted', 0)),
            'icon': '📝',
            'color': '#2196F3'
        })

        return {'cards': cards}

    # Helper methods

    def _get_performance_color(self, performance_level: str) -> str:
        """Get color for performance level"""
        level_lower = performance_level.lower().replace(' ', '_')
        return self.color_schemes['performance'].get(level_lower, '#9E9E9E')

    def _get_performance_color_from_value(self, value: float) -> str:
        """Get color based on numeric value"""
        if value >= 0.90:
            return '#4CAF50'
        elif value >= 0.75:
            return '#8BC34A'
        elif value >= 0.60:
            return '#FFC107'
        elif value >= 0.50:
            return '#FF9800'
        else:
            return '#F44336'

    def _get_event_icon(self, event_type: str) -> str:
        """Get icon for event type"""
        icons = {
            'milestone': '🎯',
            'achievement': '🏆',
            'assessment': '📝',
            'improvement': '📈',
            'challenge': '⚡'
        }
        return icons.get(event_type, '📌')

    def _get_rank_badge(self, rank: int) -> str:
        """Get badge emoji for rank"""
        if rank == 1:
            return '🥇'
        elif rank == 2:
            return '🥈'
        elif rank == 3:
            return '🥉'
        else:
            return f'#{rank}'


# Example usage
if __name__ == "__main__":
    viz = VisualizationHelpers()

    print("\n📊 Visualization Helpers - Chart Data Preparation")
    print("="*60)

    # Example 1: Line chart (performance over time)
    print("\n📈 Example 1: Line Chart Data")
    print("-"*60)

    performance_df = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=7, freq='D'),
        'accuracy': [0.65, 0.68, 0.72, 0.75, 0.78, 0.80, 0.82]
    })

    line_data = viz.prepare_line_chart(performance_df)
    print(f"Labels: {line_data['labels'][:3]}... (showing first 3)")
    print(f"Values: {line_data['datasets'][0]['data'][:3]}... (showing first 3)")
    print(f"Color: {line_data['datasets'][0]['borderColor']}")

    # Example 2: Bar chart (topic performance)
    print("\n\n📊 Example 2: Bar Chart Data")
    print("-"*60)

    topic_metrics = {
        'Algebra': {'accuracy': 0.90, 'performance_level': 'Excellent'},
        'Geometry': {'accuracy': 0.75, 'performance_level': 'Good'},
        'Trigonometry': {'accuracy': 0.60, 'performance_level': 'Satisfactory'}
    }

    bar_data = viz.prepare_bar_chart(topic_metrics)
    print(f"Topics: {bar_data['labels']}")
    print(f"Accuracies: {bar_data['datasets'][0]['data']}")
    print(f"Colors: {bar_data['datasets'][0]['backgroundColor']}")

    # Example 3: Progress gauge
    print("\n\n⚙️ Example 3: Progress Gauge")
    print("-"*60)

    gauge = viz.prepare_progress_gauge(85, 100, target_value=80)
    print(f"Current: {gauge['value']}")
    print(f"Percentage: {gauge['percentage']:.1f}%")
    print(f"Color: {gauge['color']}")
    print(f"On Track: {gauge['on_track']}")

    # Example 4: Trend indicator
    print("\n\n📈 Example 4: Trend Indicator")
    print("-"*60)

    trend = viz.prepare_trend_indicator(current=0.85, previous=0.78)
    print(f"Current: {trend['current']:.2f}")
    print(f"Previous: {trend['previous']:.2f}")
    print(f"Change: {trend['change']:+.2f}")
    print(f"Percent Change: {trend['percent_change']:+.1f}%")
    print(f"Trend: {trend['trend']} {trend['color']}")

    # Example 5: Dashboard summary
    print("\n\n📋 Example 5: Dashboard Summary Cards")
    print("-"*60)

    metrics = {
        'overall_accuracy': 0.85,
        'previous_accuracy': 0.78,
        'learning_velocity': 0.025,
        'consistency': {'consistency_score': 0.92},
        'total_questions_attempted': 145
    }

    dashboard = viz.prepare_dashboard_summary(metrics)
    for card in dashboard['cards']:
        print(f"\n{card['icon']} {card['title']}: {card['value']}")
        if card.get('trend'):
            print(f"   Trend: {card['trend']['trend']} ({card['trend']['percent_change']:+.1f}%)")

    # Example 6: Leaderboard
    print("\n\n🏆 Example 6: Leaderboard")
    print("-"*60)

    students = [
        {'student_id': 'S001', 'name': 'Alice', 'overall_accuracy': 0.95},
        {'student_id': 'S002', 'name': 'Bob', 'overall_accuracy': 0.88},
        {'student_id': 'S003', 'name': 'Charlie', 'overall_accuracy': 0.92},
        {'student_id': 'S004', 'name': 'Diana', 'overall_accuracy': 0.85}
    ]

    leaderboard = viz.prepare_leaderboard_data(students, top_n=3)
    for entry in leaderboard:
        print(f"{entry['badge']} {entry['name']}: {entry['score']:.1%}")

    print("\n="*60)
    print("✅ Visualization helpers examples complete!")
