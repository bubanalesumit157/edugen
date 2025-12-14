"""
Feature Importance Module - FIXED VERSION
Analyzes and ranks feature contributions to model predictions
Provides comparative analysis and trend detection for educators
FIXED: Proper feature normalization for fair group comparison
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
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class FeatureImportance:
    """
    Feature importance analyzer for educational ML models
    Helps educators understand which factors most influence student outcomes
    FIXED: Normalized feature scaling for accurate group comparisons
    """

    def __init__(self):
        # Feature groupings for better organization
        self.feature_groups = {
            'Academic Performance': [
                'overall_accuracy', 'recent_accuracy', 'topic_accuracy',
                'difficulty_accuracy', 'subject_accuracy'
            ],
            'Learning Behavior': [
                'learning_velocity', 'improvement_rate', 'consistency',
                'retention_rate', 'mastery_speed'
            ],
            'Engagement Metrics': [
                'total_attempts', 'practice_frequency', 'session_length',
                'days_active', 'completion_rate', 'response_time'
            ],
            'Challenge Alignment': [
                'difficulty_match', 'zpd_alignment', 'challenge_level',
                'success_rate_at_difficulty'
            ],
            'Topic Coverage': [
                'topics_mastered', 'topics_attempted', 'prerequisite_coverage',
                'curriculum_progress', 'topic_diversity'
            ]
        }

        # Baseline importance weights
        self.baseline_weights = {
            'recent_accuracy': 0.20,
            'learning_velocity': 0.15,
            'consistency': 0.12,
            'total_attempts': 0.10,
            'zpd_alignment': 0.10,
            'topic_accuracy': 0.08,
            'practice_frequency': 0.07,
            'difficulty_match': 0.06,
            'retention_rate': 0.05,
            'completion_rate': 0.05,
            'mastery_speed': 0.02
        }

        # FIXED: Feature normalization ranges
        self.normalization_ranges = {
            # Percentages/rates (already 0-1)
            'overall_accuracy': {'min': 0, 'max': 1, 'type': 'percent'},
            'recent_accuracy': {'min': 0, 'max': 1, 'type': 'percent'},
            'topic_accuracy': {'min': 0, 'max': 1, 'type': 'percent'},
            'learning_velocity': {'min': -0.5, 'max': 0.5, 'type': 'delta'},
            'consistency': {'min': 0, 'max': 1, 'type': 'percent'},
            'zpd_alignment': {'min': 0, 'max': 1, 'type': 'percent'},
            'practice_frequency': {'min': 0, 'max': 1, 'type': 'percent'},
            'completion_rate': {'min': 0, 'max': 1, 'type': 'percent'},

            # Counts (need normalization)
            'total_attempts': {'min': 0, 'max': 100, 'type': 'count'},
            'session_length': {'min': 0, 'max': 120, 'type': 'minutes'},
            'days_active': {'min': 0, 'max': 365, 'type': 'days'},
            'topics_mastered': {'min': 0, 'max': 50, 'type': 'count'},
            'topics_attempted': {'min': 0, 'max': 50, 'type': 'count'},
            'response_time': {'min': 0, 'max': 600, 'type': 'seconds'}
        }

    def _normalize_feature(self, feature_name: str, value: float) -> float:
        """
        FIXED: Normalize feature value to 0-1 scale for fair comparison

        Args:
            feature_name: Name of the feature
            value: Raw feature value

        Returns:
            Normalized value (0-1)
        """
        if not isinstance(value, (int, float)):
            return 0.0

        # Get normalization parameters
        norm_params = self.normalization_ranges.get(feature_name)

        if not norm_params:
            # Unknown feature - assume already normalized if 0-1, else divide by 100
            if 0 <= value <= 1:
                return value
            else:
                return min(value / 100, 1.0)

        # Apply normalization
        if norm_params['type'] in ['percent', 'delta']:
            # Already in 0-1 range or delta range
            if norm_params['type'] == 'delta':
                # Convert delta (-0.5 to 0.5) to 0-1 scale
                return (value - norm_params['min']) / (norm_params['max'] - norm_params['min'])
            return max(0, min(value, 1))
        else:
            # Count/time-based - normalize to 0-1
            normalized = (value - norm_params['min']) / (norm_params['max'] - norm_params['min'])
            return max(0, min(normalized, 1))

    def calculate_feature_importance(self, student_data: pd.DataFrame,
                                    target: str = 'success',
                                    method: str = 'correlation') -> Dict:
        """
        Calculate importance of each feature for predicting target

        Args:
            student_data: DataFrame with student features and target
            target: Target variable to predict
            method: 'correlation', 'variance', or 'model_based'

        Returns:
            Feature importance scores and rankings
        """
        if target not in student_data.columns:
            return {'error': f'Target {target} not found in data'}

        importance_scores = {}

        # Get numeric features
        numeric_cols = student_data.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col != target]

        if method == 'correlation':
            # Correlation-based importance
            for feature in feature_cols:
                if feature in student_data.columns:
                    corr = abs(student_data[feature].corr(student_data[target]))
                    importance_scores[feature] = corr if not np.isnan(corr) else 0

        elif method == 'variance':
            # Variance-based importance
            for feature in feature_cols:
                if feature in student_data.columns:
                    variance = student_data[feature].var()
                    importance_scores[feature] = variance if not np.isnan(variance) else 0

        else:
            # Use baseline weights
            importance_scores = {k: v for k, v in self.baseline_weights.items()
                               if k in feature_cols}

        # Normalize scores
        total = sum(importance_scores.values())
        if total > 0:
            importance_scores = {k: v/total for k, v in importance_scores.items()}

        # Rank features
        ranked = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            'scores': importance_scores,
            'ranked': [
                {'feature': feat, 'importance': score, 'rank': i+1}
                for i, (feat, score) in enumerate(ranked)
            ],
            'method': method,
            'top_features': ranked[:5]
        }

    def analyze_feature_contributions(self, student_id: str,
                                     student_data: Dict,
                                     prediction: float) -> Dict:
        """
        Analyze how each feature contributed to a prediction

        Args:
            student_id: Student identifier
            student_data: Student's feature values
            prediction: Model prediction value

        Returns:
            Feature contribution breakdown
        """
        contributions = []

        for feature, value in student_data.items():
            if feature in self.baseline_weights:
                # Calculate contribution
                weight = self.baseline_weights[feature]

                if isinstance(value, (int, float)):
                    # FIXED: Normalize value for fair comparison
                    normalized_value = self._normalize_feature(feature, value)
                    contribution = weight * normalized_value

                    # Determine impact direction
                    if normalized_value > 0.7:
                        impact = 'positive'
                    elif normalized_value < 0.5:
                        impact = 'negative'
                    else:
                        impact = 'neutral'

                    contributions.append({
                        'feature': feature,
                        'value': value,
                        'normalized_value': normalized_value,
                        'weight': weight,
                        'contribution': contribution,
                        'impact': impact,
                        'percentage': contribution / prediction * 100 if prediction > 0 else 0
                    })

        # Sort by contribution
        contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)

        return {
            'student_id': student_id,
            'prediction': prediction,
            'contributions': contributions,
            'top_contributors': contributions[:5],
            'summary': self._generate_contribution_summary(contributions)
        }

    def track_feature_trends(self, student_history: pd.DataFrame,
                           features: List[str],
                           time_column: str = 'timestamp') -> Dict:
        """
        Track how feature values change over time

        Args:
            student_history: DataFrame with student's historical data
            features: List of features to track
            time_column: Name of timestamp column

        Returns:
            Trend analysis for each feature
        """
        if time_column in student_history.columns:
            student_history = student_history.sort_values(time_column)

        trends = {}

        for feature in features:
            if feature not in student_history.columns:
                continue

            values = student_history[feature].dropna()

            if len(values) < 2:
                trends[feature] = {
                    'trend': 'insufficient_data',
                    'direction': 'unknown',
                    'change': 0,
                    'volatility': 0
                }
                continue

            # Calculate trend metrics
            first_half = values[:len(values)//2].mean()
            second_half = values[len(values)//2:].mean()
            change = second_half - first_half

            # Determine direction
            if change > 0.1:
                direction = 'improving'
            elif change < -0.1:
                direction = 'declining'
            else:
                direction = 'stable'

            # Calculate volatility (standard deviation)
            volatility = values.std()

            # Detect pattern
            pattern = self._detect_pattern(values.tolist())

            trends[feature] = {
                'trend': direction,
                'direction': direction,
                'change': change,
                'change_percentage': (change / first_half * 100) if first_half > 0 else 0,
                'volatility': volatility,
                'pattern': pattern,
                'current_value': values.iloc[-1],
                'average_value': values.mean(),
                'data_points': len(values)
            }

        return {
            'trends': trends,
            'summary': self._generate_trend_summary(trends),
            'alerts': self._generate_trend_alerts(trends)
        }

    def compare_feature_importance(self, student_groups: Dict[str, pd.DataFrame],
                                  target: str = 'success') -> Dict:
        """
        Compare feature importance across different student groups

        Args:
            student_groups: Dict of {group_name: DataFrame}
            target: Target variable

        Returns:
            Comparative importance analysis
        """
        group_importance = {}

        for group_name, group_data in student_groups.items():
            importance = self.calculate_feature_importance(
                group_data, target, method='correlation'
            )
            group_importance[group_name] = importance['scores']

        # Find features with largest differences
        differences = self._calculate_importance_differences(group_importance)

        return {
            'group_importance': group_importance,
            'differences': differences,
            'interpretation': self._interpret_differences(differences)
        }

    def get_feature_impact_summary(self, feature_name: str,
                                  student_data: pd.DataFrame,
                                  bins: int = 3) -> Dict:
        """
        Analyze impact of a specific feature on outcomes

        Args:
            feature_name: Name of feature to analyze
            student_data: DataFrame with student data
            bins: Number of bins for grouping (low/medium/high)

        Returns:
            Impact analysis summary
        """
        if feature_name not in student_data.columns:
            return {'error': f'Feature {feature_name} not found'}

        # Create bins
        student_data['feature_bin'] = pd.qcut(
            student_data[feature_name], 
            q=bins, 
            labels=['Low', 'Medium', 'High'],
            duplicates='drop'
        )

        # Analyze outcomes by bin
        if 'success' in student_data.columns:
            outcomes = student_data.groupby('feature_bin')['success'].mean()
        elif 'accuracy' in student_data.columns:
            outcomes = student_data.groupby('feature_bin')['accuracy'].mean()
        else:
            outcomes = student_data.groupby('feature_bin').size()

        impact_data = []
        for level in ['Low', 'Medium', 'High']:
            if level in outcomes.index:
                impact_data.append({
                    'level': level,
                    'outcome': outcomes[level],
                    'count': len(student_data[student_data['feature_bin'] == level])
                })

        return {
            'feature': feature_name,
            'impact_by_level': impact_data,
            'interpretation': self._interpret_feature_impact(feature_name, impact_data),
            'recommendation': self._recommend_based_on_impact(feature_name, impact_data)
        }

    def rank_features_by_group(self, features: List[str],
                              student_data: Dict) -> Dict:
        """
        Rank features by their group and individual importance
        FIXED: Properly normalized for fair comparison

        Args:
            features: List of feature names
            student_data: Student feature values

        Returns:
            Grouped and ranked features
        """
        grouped_features = {}

        # Group features
        for group_name, group_features in self.feature_groups.items():
            group_items = []
            for feature in features:
                if feature in group_features:
                    raw_value = student_data.get(feature, 0)
                    weight = self.baseline_weights.get(feature, 0.01)

                    # FIXED: Normalize value before scoring
                    normalized_value = self._normalize_feature(feature, raw_value)

                    group_items.append({
                        'feature': feature,
                        'raw_value': raw_value,
                        'normalized_value': normalized_value,
                        'weight': weight,
                        'score': normalized_value * weight
                    })

            if group_items:
                # Sort by score
                group_items.sort(key=lambda x: x['score'], reverse=True)
                grouped_features[group_name] = {
                    'features': group_items,
                    'group_score': sum(item['score'] for item in group_items),
                    'feature_count': len(group_items)
                }

        # Rank groups
        ranked_groups = sorted(
            grouped_features.items(),
            key=lambda x: x[1]['group_score'],
            reverse=True
        )

        return {
            'grouped_features': grouped_features,
            'ranked_groups': [
                {'group': name, **data, 'rank': i+1}
                for i, (name, data) in enumerate(ranked_groups)
            ],
            'top_group': ranked_groups[0][0] if ranked_groups else None
        }

    # Helper methods

    def _generate_contribution_summary(self, contributions: List[Dict]) -> str:
        """Generate summary of feature contributions"""
        if not contributions:
            return "No contributions calculated"

        top_3 = contributions[:3]
        summary_parts = []

        for contrib in top_3:
            summary_parts.append(
                f"{contrib['feature']} ({contrib['percentage']:.1f}%)"
            )

        return "Top contributors: " + ", ".join(summary_parts)

    def _detect_pattern(self, values: List[float]) -> str:
        """Detect pattern in value sequence"""
        if len(values) < 3:
            return 'insufficient_data'

        # Check for monotonic increase/decrease
        increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
        decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))

        if increasing:
            return 'consistent_improvement'
        elif decreasing:
            return 'consistent_decline'

        # Check for oscillation
        changes = [values[i+1] - values[i] for i in range(len(values)-1)]
        sign_changes = sum(1 for i in range(len(changes)-1) 
                          if changes[i] * changes[i+1] < 0)

        if sign_changes >= len(changes) * 0.5:
            return 'oscillating'

        return 'irregular'

    def _generate_trend_summary(self, trends: Dict) -> str:
        """Generate summary of trends"""
        improving = sum(1 for t in trends.values() if t['direction'] == 'improving')
        declining = sum(1 for t in trends.values() if t['direction'] == 'declining')
        stable = sum(1 for t in trends.values() if t['direction'] == 'stable')

        return f"{improving} improving, {declining} declining, {stable} stable"

    def _generate_trend_alerts(self, trends: Dict) -> List[str]:
        """Generate alerts for concerning trends"""
        alerts = []

        for feature, trend_data in trends.items():
            # Alert for declining important features
            if trend_data['direction'] == 'declining':
                if feature in ['recent_accuracy', 'learning_velocity', 'consistency']:
                    alerts.append(
                        f"⚠️ {feature} declining ({trend_data['change_percentage']:.1f}%)"
                    )

            # Alert for high volatility
            if trend_data.get('volatility', 0) > 0.3:
                alerts.append(
                    f"⚠️ {feature} showing high volatility (unstable performance)"
                )

        return alerts

    def _calculate_importance_differences(self, group_importance: Dict) -> List[Dict]:
        """Calculate differences in feature importance between groups"""
        differences = []

        # Get all features
        all_features = set()
        for scores in group_importance.values():
            all_features.update(scores.keys())

        # Calculate differences for each feature
        for feature in all_features:
            scores = [group.get(feature, 0) for group in group_importance.values()]

            if len(scores) >= 2:
                max_diff = max(scores) - min(scores)
                differences.append({
                    'feature': feature,
                    'max_difference': max_diff,
                    'scores_by_group': {
                        group: group_importance[group].get(feature, 0)
                        for group in group_importance.keys()
                    }
                })

        # Sort by difference
        differences.sort(key=lambda x: x['max_difference'], reverse=True)

        return differences

    def _interpret_differences(self, differences: List[Dict]) -> str:
        """Interpret importance differences"""
        if not differences:
            return "No significant differences found"

        top_diff = differences[0]

        if top_diff['max_difference'] > 0.2:
            return f"Large variation in {top_diff['feature']} importance across groups"
        elif top_diff['max_difference'] > 0.1:
            return f"Moderate variation in {top_diff['feature']} importance across groups"
        else:
            return "Similar feature importance across groups"

    def _interpret_feature_impact(self, feature_name: str,
                                  impact_data: List[Dict]) -> str:
        """Interpret impact of a feature"""
        if len(impact_data) < 2:
            return "Insufficient data for interpretation"

        low = next((d for d in impact_data if d['level'] == 'Low'), None)
        high = next((d for d in impact_data if d['level'] == 'High'), None)

        if low and high:
            diff = high['outcome'] - low['outcome']

            if diff > 0.2:
                return f"Strong positive impact: Higher {feature_name} → better outcomes"
            elif diff < -0.2:
                return f"Strong negative impact: Higher {feature_name} → worse outcomes"
            else:
                return f"Moderate impact of {feature_name} on outcomes"

        return "Impact unclear from available data"

    def _recommend_based_on_impact(self, feature_name: str,
                                   impact_data: List[Dict]) -> str:
        """Generate recommendation based on feature impact"""
        if len(impact_data) < 2:
            return "Gather more data to make recommendations"

        low = next((d for d in impact_data if d['level'] == 'Low'), None)
        high = next((d for d in impact_data if d['level'] == 'High'), None)

        if low and high:
            diff = high['outcome'] - low['outcome']

            if diff > 0.2:
                return f"Encourage increasing {feature_name} for better outcomes"
            elif diff < -0.2:
                return f"Consider interventions to reduce {feature_name}"
            else:
                return f"Monitor {feature_name} but no immediate action needed"

        return "Continue monitoring this feature"


# Example usage
if __name__ == "__main__":
    analyzer = FeatureImportance()

    print("\n📊 Feature Importance Analyzer (FIXED - Normalized Scaling)")
    print("="*60)

    # Example 1: Feature ranking with proper normalization
    print("\n📈 Example 1: Feature Ranking by Group (FIXED)")
    print("-"*60)

    student_data = {
        'recent_accuracy': 0.85,
        'learning_velocity': 0.12,
        'consistency': 0.78,
        'total_attempts': 45,
        'practice_frequency': 0.8,
        'zpd_alignment': 0.75
    }

    ranking = analyzer.rank_features_by_group(
        list(student_data.keys()),
        student_data
    )

    print("Feature Groups Ranked by Impact (Normalized):")
    for group in ranking['ranked_groups']:
        print(f"\n{group['rank']}. {group['group']} (Score: {group['group_score']:.3f})")
        for feature in group['features'][:2]:
            print(f"   • {feature['feature']}: {feature['raw_value']} → normalized: {feature['normalized_value']:.2f}")
            print(f"     Weight: {feature['weight']:.0%}, Contribution: {feature['score']:.3f}")

    # Example 2: Contribution analysis
    print("\n\n🔍 Example 2: Feature Contribution Analysis")
    print("-"*60)

    contribution = analyzer.analyze_feature_contributions(
        'STU_001',
        student_data,
        prediction=0.82
    )

    print(f"Prediction: {contribution['prediction']:.1%}")
    print(f"Summary: {contribution['summary']}")
    print("\nTop Contributing Features:")
    for contrib in contribution['top_contributors'][:3]:
        impact_icon = "✅" if contrib['impact'] == 'positive' else "⚠️"
        print(f"  {impact_icon} {contrib['feature']}: {contrib['percentage']:.1f}% of prediction")
        print(f"     Raw: {contrib['value']}, Normalized: {contrib['normalized_value']:.2f}")
        print(f"     Impact: {contrib['impact']}")

    # Example 3: Trend analysis
    print("\n\n📉 Example 3: Feature Trend Analysis")
    print("-"*60)

    # Simulate historical data
    history = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', periods=10, freq='W'),
        'recent_accuracy': [0.65, 0.68, 0.72, 0.75, 0.78, 0.80, 0.83, 0.85, 0.87, 0.88],
        'consistency': [0.60, 0.62, 0.58, 0.65, 0.68, 0.70, 0.72, 0.75, 0.73, 0.78]
    })

    trends = analyzer.track_feature_trends(
        history,
        ['recent_accuracy', 'consistency'],
        'timestamp'
    )

    print(f"Trend Summary: {trends['summary']}")
    print("\nDetailed Trends:")
    for feature, trend_data in trends['trends'].items():
        direction_icon = "📈" if trend_data['direction'] == 'improving' else "📉" if trend_data['direction'] == 'declining' else "➡️"
        print(f"  {direction_icon} {feature}: {trend_data['direction']}")
        print(f"     Change: {trend_data['change']:+.2f} ({trend_data['change_percentage']:+.1f}%)")
        print(f"     Pattern: {trend_data['pattern']}")

    if trends['alerts']:
        print("\n⚠️ Alerts:")
        for alert in trends['alerts']:
            print(f"  {alert}")

    print("\n="*60)
    print("✅ Feature importance analysis (FIXED) complete!")
