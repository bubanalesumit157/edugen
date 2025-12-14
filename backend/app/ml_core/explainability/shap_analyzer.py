"""
SHAP Analyzer Module - FIXED VERSION
Provides explainability for ML model predictions using SHAP values
Helps educators understand "why" the system made specific recommendations
"""

import sys
import os

# Fix imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


class SHAPAnalyzer:
    """
    SHAP (SHapley Additive exPlanations) analyzer for model interpretability
    Provides human-readable explanations for ML predictions

    FIXED: Better confidence calculation, complete factor reporting, aligned messaging
    """

    def __init__(self):
        # Feature categories for organization
        self.feature_categories = {
            'performance': [
                'overall_accuracy', 'recent_accuracy', 'trend',
                'consistency', 'learning_velocity'
            ],
            'engagement': [
                'total_attempts', 'avg_time_spent', 'session_length',
                'days_active', 'completion_rate'
            ],
            'difficulty': [
                'difficulty_level', 'difficulty_match', 'challenge_level',
                'zpd_alignment'
            ],
            'topic': [
                'topic_accuracy', 'topic_attempts', 'days_since_practice',
                'mastery_level', 'prerequisite_coverage'
            ]
        }

        # Human-readable feature names
        self.feature_names = {
            'overall_accuracy': 'Overall Performance',
            'recent_accuracy': 'Recent Performance',
            'learning_velocity': 'Learning Progress Rate',
            'total_attempts': 'Practice Frequency',
            'difficulty_match': 'Difficulty Appropriateness',
            'zpd_alignment': 'Challenge Level Fit',
            'topic_accuracy': 'Topic Mastery',
            'days_since_practice': 'Time Since Last Practice',
            'mastery_level': 'Skill Level',
            'consistency': 'Performance Consistency',
            'trend': 'Performance Trend',
            'avg_time_spent': 'Average Study Time',
            'session_length': 'Session Duration',
            'days_active': 'Days Active',
            'completion_rate': 'Assignment Completion',
            'difficulty_level': 'Question Difficulty',
            'challenge_level': 'Challenge Appropriateness',
            'topic_attempts': 'Topic Practice Count',
            'prerequisite_coverage': 'Foundation Strength'
        }

    def explain_recommendation(self, recommendation: Dict,
                              student_data: Dict,
                              model_type: str = 'difficulty') -> Dict:
        """
        Explain why a specific recommendation was made

        Args:
            recommendation: The recommendation made by the system
            student_data: Student features used for recommendation
            model_type: Type of recommendation ('difficulty', 'topic', 'path')

        Returns:
            Explanation with SHAP-like values and reasoning
        """
        # Calculate feature importance (simplified SHAP approximation)
        feature_importance = self._calculate_feature_importance(
            student_data, model_type
        )

        # Generate human-readable explanation
        explanation = self._generate_explanation(
            recommendation, feature_importance, student_data, model_type
        )

        return {
            'recommendation': recommendation,
            'model_type': model_type,
            'feature_importance': feature_importance,
            'explanation': explanation,
            'top_factors': self._get_top_factors(feature_importance, n=3),
            'confidence': self._calculate_confidence(feature_importance, student_data)
        }

    def explain_difficulty_recommendation(self, recommended_difficulty: str,
                                        current_difficulty: str,
                                        student_metrics: Dict) -> Dict:
        """
        Explain why a specific difficulty level was recommended
        FIXED: Shows all factors, better confidence, aligned messaging

        Args:
            recommended_difficulty: Recommended difficulty level
            current_difficulty: Current difficulty level
            student_metrics: Student performance metrics

        Returns:
            Detailed explanation for educators
        """
        # FIXED: Collect ALL factors, not just extreme ones
        factors = []

        # Recent accuracy (ALWAYS included)
        recent_acc = student_metrics.get('recent_accuracy', 0.7)
        if recent_acc >= 0.85:
            factors.append({
                'feature': 'Recent Performance',
                'value': f'{recent_acc:.1%}',
                'impact': 'positive',
                'importance': 0.35,
                'reasoning': 'High accuracy indicates readiness for increased challenge'
            })
        elif recent_acc <= 0.50:
            factors.append({
                'feature': 'Recent Performance',
                'value': f'{recent_acc:.1%}',
                'impact': 'negative',
                'importance': 0.40,
                'reasoning': 'Low accuracy suggests need for easier content'
            })
        else:
            factors.append({
                'feature': 'Recent Performance',
                'value': f'{recent_acc:.1%}',
                'impact': 'neutral',
                'importance': 0.25,
                'reasoning': 'Moderate accuracy - optimal learning zone'
            })

        # Learning velocity (ALWAYS included)
        velocity = student_metrics.get('learning_velocity', 0.0)
        if abs(velocity) > 0.15:
            factors.append({
                'feature': 'Learning Progress',
                'value': f'{velocity:+.1%}',
                'impact': 'positive' if velocity > 0 else 'negative',
                'importance': 0.25,
                'reasoning': f'{"Rapid improvement" if velocity > 0 else "Performance declining"} - adjust accordingly'
            })
        elif abs(velocity) > 0.05:
            factors.append({
                'feature': 'Learning Progress',
                'value': f'{velocity:+.1%}',
                'impact': 'neutral',
                'importance': 0.15,
                'reasoning': 'Steady progress maintained'
            })
        else:
            factors.append({
                'feature': 'Learning Progress',
                'value': f'{velocity:+.1%}',
                'impact': 'neutral',
                'importance': 0.10,
                'reasoning': 'Stable performance - no significant trend'
            })

        # Consistency (ALWAYS included)
        consistency = student_metrics.get('consistency', 0.7)
        if consistency >= 0.75:
            factors.append({
                'feature': 'Performance Consistency',
                'value': f'{consistency:.1%}',
                'impact': 'positive',
                'importance': 0.15,
                'reasoning': 'Consistent performance - reliable assessment'
            })
        elif consistency < 0.5:
            factors.append({
                'feature': 'Performance Consistency',
                'value': f'{consistency:.1%}',
                'impact': 'negative',
                'importance': 0.15,
                'reasoning': 'Inconsistent performance - needs stabilization'
            })
        else:
            factors.append({
                'feature': 'Performance Consistency',
                'value': f'{consistency:.1%}',
                'impact': 'neutral',
                'importance': 0.10,
                'reasoning': 'Moderate consistency'
            })

        # Practice frequency (ALWAYS included)
        attempts = student_metrics.get('total_attempts', 10)
        if attempts >= 20:
            factors.append({
                'feature': 'Practice Frequency',
                'value': f'{attempts} attempts',
                'impact': 'positive',
                'importance': 0.10,
                'reasoning': 'Sufficient practice data for confident recommendation'
            })
        elif attempts < 5:
            factors.append({
                'feature': 'Practice Frequency',
                'value': f'{attempts} attempts',
                'impact': 'negative',
                'importance': 0.15,
                'reasoning': 'Limited practice data - conservative recommendation advised'
            })
        else:
            factors.append({
                'feature': 'Practice Frequency',
                'value': f'{attempts} attempts',
                'impact': 'neutral',
                'importance': 0.05,
                'reasoning': 'Adequate practice data available'
            })

        # FIXED: Calculate confidence based on data quality and factor alignment
        confidence = self._calculate_recommendation_confidence(factors, student_metrics)

        # FIXED: Generate summary that matches confidence level
        summary = self._generate_difficulty_summary(
            recommended_difficulty, current_difficulty, factors, confidence
        )

        return {
            'recommended_difficulty': recommended_difficulty,
            'current_difficulty': current_difficulty,
            'factors': sorted(factors, key=lambda x: x['importance'], reverse=True),
            'summary': summary,
            'confidence': confidence,
            'data_quality': self._assess_data_quality(student_metrics)
        }

    def explain_topic_selection(self, selected_topics: List[Dict],
                               student_performance: Dict) -> Dict:
        """
        Explain why specific topics were selected

        Args:
            selected_topics: List of selected topics with metadata
            student_performance: Student's performance history

        Returns:
            Explanation for each topic selection
        """
        explanations = []

        for topic in selected_topics:
            # Determine primary reason
            category = topic.get('category', 'unknown')
            accuracy = topic.get('accuracy', None)
            priority = topic.get('priority', 50)

            # Build explanation
            explanation = {
                'topic': topic['topic'],
                'subject': topic['subject'],
                'category': category,
                'priority': priority,
                'reasoning': []
            }

            # Add category-specific reasoning
            if category == 'weak':
                explanation['reasoning'].append({
                    'factor': 'Low Performance',
                    'detail': f'Current accuracy: {accuracy:.1%}',
                    'importance': 'high',
                    'educator_action': 'Consider reviewing fundamentals before advancing'
                })
                if priority >= 70:
                    explanation['reasoning'].append({
                        'factor': 'High Priority',
                        'detail': 'Critical for progression',
                        'importance': 'high',
                        'educator_action': 'Focus attention on this topic'
                    })
            elif category == 'review':
                days_since = topic.get('days_since_practice', 0)
                explanation['reasoning'].append({
                    'factor': 'Spaced Repetition',
                    'detail': f'Last practiced {days_since} days ago',
                    'importance': 'medium',
                    'educator_action': 'Regular review prevents knowledge decay'
                })
            elif category == 'unlocked':
                explanation['reasoning'].append({
                    'factor': 'Prerequisites Met',
                    'detail': 'Student ready for new content',
                    'importance': 'medium',
                    'educator_action': 'Monitor initial understanding of new topic'
                })

            explanations.append(explanation)

        return {
            'selected_topics': len(selected_topics),
            'explanations': explanations,
            'summary': self._generate_topic_summary(explanations)
        }

    def get_feature_impact_breakdown(self, student_id: str,
                                    all_features: Dict) -> Dict:
        """
        Break down how each feature category impacts recommendations

        Args:
            student_id: Student identifier
            all_features: All student features

        Returns:
            Category-wise impact analysis
        """
        category_impacts = {}

        for category, features in self.feature_categories.items():
            available_features = {k: v for k, v in all_features.items() 
                                if k in features}

            if not available_features:
                continue

            # Calculate category impact
            impact = self._calculate_category_impact(available_features, category)

            category_impacts[category] = {
                'overall_impact': impact['score'],
                'direction': impact['direction'],
                'features': impact['features'],
                'interpretation': impact['interpretation']
            }

        return {
            'student_id': student_id,
            'category_impacts': category_impacts,
            'overall_assessment': self._generate_overall_assessment(category_impacts)
        }

    def generate_educator_insights(self, explanations: Dict) -> List[str]:
        """
        Generate actionable insights for educators
        FIXED: Aligned with confidence level

        Args:
            explanations: Explanation data from other methods

        Returns:
            List of educator-facing insights
        """
        insights = []
        confidence = explanations.get('confidence', 0.5)

        # FIXED: Add confidence context first
        if confidence >= 0.75:
            insights.append("✅ High confidence in recommendation - strong data support")
        elif confidence < 0.5:
            insights.append("⚠️ Low confidence - limited data available, monitor closely")

        # Check for critical factors
        if 'factors' in explanations:
            for factor in explanations['factors']:
                if factor['importance'] > 0.25:
                    if factor['impact'] == 'negative':
                        insights.append(
                            f"⚠️ {factor['feature']}: {factor['reasoning']}"
                        )
                    elif factor['impact'] == 'positive':
                        insights.append(
                            f"✅ {factor['feature']}: {factor['reasoning']}"
                        )

        # Add context
        if len(insights) == 0:
            insights.append("ℹ️ Student performing within expected parameters")

        return insights

    # Helper methods

    def _calculate_feature_importance(self, features: Dict, 
                                      model_type: str) -> Dict:
        """Calculate simplified SHAP-like feature importance"""
        importance = {}

        if model_type == 'difficulty':
            weights = {
                'recent_accuracy': 0.35,
                'learning_velocity': 0.25,
                'consistency': 0.15,
                'zpd_alignment': 0.15,
                'total_attempts': 0.10
            }
        elif model_type == 'topic':
            weights = {
                'topic_accuracy': 0.30,
                'days_since_practice': 0.25,
                'priority': 0.20,
                'prerequisite_coverage': 0.15,
                'mastery_level': 0.10
            }
        else:
            weights = {k: 1.0/len(features) for k in features.keys()}

        for feature, value in features.items():
            base_weight = weights.get(feature, 0.05)

            if isinstance(value, (int, float)):
                if value > 0.85:
                    importance[feature] = base_weight * 1.2
                elif value < 0.50:
                    importance[feature] = base_weight * 1.3
                else:
                    importance[feature] = base_weight
            else:
                importance[feature] = base_weight

        # Normalize
        total = sum(importance.values())
        if total > 0:
            importance = {k: v/total for k, v in importance.items()}

        return importance

    def _calculate_recommendation_confidence(self, factors: List[Dict], 
                                           metrics: Dict) -> float:
        """
        FIXED: Calculate confidence based on data quality and factor alignment
        """
        # Factor 1: Data quantity (attempts)
        attempts = metrics.get('total_attempts', 10)
        data_quality = min(attempts / 20, 1.0)  # 20+ attempts = full confidence

        # Factor 2: Factor alignment (do factors agree?)
        positive_factors = sum(1 for f in factors if f['impact'] == 'positive')
        negative_factors = sum(1 for f in factors if f['impact'] == 'negative')
        total_factors = len(factors)

        if total_factors > 0:
            alignment = max(positive_factors, negative_factors) / total_factors
        else:
            alignment = 0.5

        # Factor 3: Importance of agreeing factors
        total_importance = sum(f['importance'] for f in factors 
                              if f['impact'] != 'neutral')

        # Combined confidence
        confidence = (
            data_quality * 0.3 +      # 30% from data quantity
            alignment * 0.4 +          # 40% from factor alignment
            total_importance * 0.3     # 30% from importance weights
        )

        return min(confidence, 1.0)

    def _assess_data_quality(self, metrics: Dict) -> str:
        """Assess quality of available data"""
        attempts = metrics.get('total_attempts', 10)

        if attempts >= 20:
            return 'High - Sufficient data for confident recommendations'
        elif attempts >= 10:
            return 'Moderate - Adequate data available'
        else:
            return 'Low - Limited data, recommendations are provisional'

    def _generate_explanation(self, recommendation: Dict,
                            importance: Dict, data: Dict,
                            model_type: str) -> str:
        """Generate human-readable explanation"""
        top_features = sorted(importance.items(), 
                            key=lambda x: x[1], reverse=True)[:3]

        explanation_parts = []
        for feature, weight in top_features:
            feature_name = self.feature_names.get(feature, feature)
            value = data.get(feature, 'N/A')

            if isinstance(value, float):
                explanation_parts.append(
                    f"{feature_name}: {value:.1%} (impact: {weight:.0%})"
                )
            else:
                explanation_parts.append(
                    f"{feature_name}: {value} (impact: {weight:.0%})"
                )

        return "Primary factors: " + "; ".join(explanation_parts)

    def _get_top_factors(self, importance: Dict, n: int = 3) -> List[Dict]:
        """Get top N factors"""
        sorted_factors = sorted(importance.items(), 
                              key=lambda x: x[1], reverse=True)

        return [
            {
                'feature': self.feature_names.get(feat, feat),
                'importance': imp,
                'rank': i + 1
            }
            for i, (feat, imp) in enumerate(sorted_factors[:n])
        ]

    def _calculate_confidence(self, importance: Dict, data: Dict) -> float:
        """Calculate confidence based on feature importance distribution"""
        if not importance:
            return 0.5

        # Check data quality
        attempts = data.get('total_attempts', 10)
        data_quality = min(attempts / 20, 1.0)

        # Check feature distribution
        values = list(importance.values())
        top_3 = sorted(values, reverse=True)[:3]
        feature_confidence = sum(top_3)

        # Combined
        confidence = data_quality * 0.4 + feature_confidence * 0.6

        return min(confidence, 1.0)

    def _generate_difficulty_summary(self, recommended: str, 
                                   current: str, factors: List[Dict],
                                   confidence: float) -> str:
        """
        FIXED: Generate summary aligned with confidence level
        """
        # Determine direction
        if recommended == current:
            direction = "maintain"
        elif self._difficulty_level(recommended) > self._difficulty_level(current):
            direction = "increase"
        else:
            direction = "decrease"

        # FIXED: Adjust language based on confidence
        if confidence >= 0.75:
            # High confidence - strong language
            if direction == "increase":
                return f"Recommend increasing to {recommended} - student demonstrating readiness for greater challenge"
            elif direction == "decrease":
                return f"Recommend reducing to {recommended} - student needs additional support"
            else:
                return f"Recommend maintaining {current} - student in optimal learning zone"
        elif confidence >= 0.5:
            # Medium confidence - moderate language
            if direction == "increase":
                return f"Consider increasing to {recommended} - positive indicators present"
            elif direction == "decrease":
                return f"Consider reducing to {recommended} - some struggle detected"
            else:
                return f"Maintain {current} - performance appears stable"
        else:
            # Low confidence - conservative language
            return f"Provisional recommendation: {recommended} - limited data available, monitor student closely"

    def _difficulty_level(self, difficulty: str) -> int:
        """Convert difficulty to numeric"""
        levels = {'Easy': 1, 'Medium': 2, 'Hard': 3, 'Advanced': 4}
        return levels.get(difficulty, 2)

    def _generate_topic_summary(self, explanations: List[Dict]) -> str:
        """Generate summary for topic selections"""
        categories = {}
        for exp in explanations:
            cat = exp['category']
            categories[cat] = categories.get(cat, 0) + 1

        parts = []
        if categories.get('weak', 0) > 0:
            parts.append(f"{categories['weak']} remediation topic(s)")
        if categories.get('review', 0) > 0:
            parts.append(f"{categories['review']} review topic(s)")
        if categories.get('unlocked', 0) > 0:
            parts.append(f"{categories['unlocked']} new topic(s)")

        return "Selected: " + ", ".join(parts) if parts else "No topics selected"

    def _calculate_category_impact(self, features: Dict, 
                                  category: str) -> Dict:
        """Calculate impact of a feature category"""
        if not features:
            return {'score': 0, 'direction': 'neutral', 
                   'features': [], 'interpretation': 'No data'}

        scores = []
        for feature, value in features.items():
            if isinstance(value, (int, float)):
                scores.append(value)

        avg_score = np.mean(scores) if scores else 0.5

        direction = 'positive' if avg_score > 0.7 else                    'negative' if avg_score < 0.5 else 'neutral'

        interpretation = self._interpret_category(category, avg_score)

        return {
            'score': avg_score,
            'direction': direction,
            'features': list(features.keys()),
            'interpretation': interpretation
        }

    def _interpret_category(self, category: str, score: float) -> str:
        """Interpret category score"""
        interpretations = {
            'performance': {
                'high': 'Strong academic performance',
                'medium': 'Adequate performance with room for growth',
                'low': 'Performance needs attention'
            },
            'engagement': {
                'high': 'Highly engaged student',
                'medium': 'Moderate engagement',
                'low': 'Low engagement - requires intervention'
            },
            'difficulty': {
                'high': 'Difficulty level well-matched',
                'medium': 'Difficulty adjustment may help',
                'low': 'Difficulty mismatch detected'
            },
            'topic': {
                'high': 'Strong topic mastery',
                'medium': 'Developing topic proficiency',
                'low': 'Topic mastery needs work'
            }
        }

        level = 'high' if score > 0.7 else 'low' if score < 0.5 else 'medium'
        return interpretations.get(category, {}).get(level, 'Data available')

    def _generate_overall_assessment(self, impacts: Dict) -> str:
        """Generate overall assessment from category impacts"""
        positive = sum(1 for imp in impacts.values() 
                      if imp['direction'] == 'positive')
        negative = sum(1 for imp in impacts.values() 
                      if imp['direction'] == 'negative')

        if positive > negative:
            return "Overall: Student showing positive indicators"
        elif negative > positive:
            return "Overall: Student needs targeted support"
        else:
            return "Overall: Mixed performance - monitor closely"


# Example usage
if __name__ == "__main__":
    analyzer = SHAPAnalyzer()

    print("\n🔍 SHAP Analyzer - Model Explainability (FIXED)")
    print("="*60)

    # Example 1: High confidence scenario
    print("\n📊 Example 1: High Confidence Recommendation")
    print("-"*60)

    student_metrics = {
        'recent_accuracy': 0.88,
        'overall_accuracy': 0.75,
        'learning_velocity': 0.18,
        'consistency': 0.82,
        'total_attempts': 25
    }

    explanation = analyzer.explain_difficulty_recommendation(
        recommended_difficulty='Hard',
        current_difficulty='Medium',
        student_metrics=student_metrics
    )

    print(f"Recommendation: {explanation['current_difficulty']} → {explanation['recommended_difficulty']}")
    print(f"Confidence: {explanation['confidence']:.0%}")
    print(f"Data Quality: {explanation['data_quality']}")
    print(f"\nSummary: {explanation['summary']}")
    print("\nAll Factors:")
    for factor in explanation['factors']:
        impact_icon = "✅" if factor['impact'] == 'positive' else "⚠️" if factor['impact'] == 'negative' else "ℹ️"
        print(f"  {impact_icon} {factor['feature']}: {factor['value']} (importance: {factor['importance']:.0%})")
        print(f"     {factor['reasoning']}")

    print("\n💡 Educator Insights:")
    insights = analyzer.generate_educator_insights(explanation)
    for insight in insights:
        print(f"  {insight}")

    # Example 2: Low confidence scenario
    print("\n\n📊 Example 2: Low Confidence Recommendation")
    print("-"*60)

    student_metrics_low = {
        'recent_accuracy': 0.65,
        'overall_accuracy': 0.65,
        'learning_velocity': 0.02,
        'consistency': 0.60,
        'total_attempts': 4
    }

    explanation_low = analyzer.explain_difficulty_recommendation(
        recommended_difficulty='Medium',
        current_difficulty='Medium',
        student_metrics=student_metrics_low
    )

    print(f"Recommendation: {explanation_low['current_difficulty']} → {explanation_low['recommended_difficulty']}")
    print(f"Confidence: {explanation_low['confidence']:.0%}")
    print(f"Data Quality: {explanation_low['data_quality']}")
    print(f"\nSummary: {explanation_low['summary']}")
    print("\nAll Factors:")
    for factor in explanation_low['factors']:
        impact_icon = "✅" if factor['impact'] == 'positive' else "⚠️" if factor['impact'] == 'negative' else "ℹ️"
        print(f"  {impact_icon} {factor['feature']}: {factor['value']} (importance: {factor['importance']:.0%})")
        print(f"     {factor['reasoning']}")

    print("\n💡 Educator Insights:")
    insights_low = analyzer.generate_educator_insights(explanation_low)
    for insight in insights_low:
        print(f"  {insight}")

    print("\n="*60)
    print("✅ SHAP analyzer (FIXED) examples complete!")
