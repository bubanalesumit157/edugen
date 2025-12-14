"""
Student Analytics Module - TESTED VERSION
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import warnings
from utils.data_loader import DataLoader  # Expects to be at ml-analytics/ level
warnings.filterwarnings('ignore')


class StudentAnalytics:
    """Generate comprehensive analytics for students"""

    def __init__(self):
        self.performance_tiers = {
            'Excellent': 0.85,
            'Good': 0.70,
            'Average': 0.55,
            'Below Average': 0.40,
            'Struggling': 0.0
        }

    def analyze_student(self, student_id: str, 
                       learning_sequences: pd.DataFrame,
                       performance_history: pd.DataFrame) -> Dict:
        """Generate comprehensive analytics for a student"""
        # Filter student data
        student_sequences = learning_sequences[
            learning_sequences['student_id'] == student_id
        ].copy()

        student_performance = performance_history[
            performance_history['student_id'] == student_id
        ].copy()

        if len(student_sequences) == 0:
            return self._get_empty_analytics(student_id)

        # Sort by timestamp
        student_sequences = student_sequences.sort_values('timestamp')

        analytics = {
            'student_id': student_id,
            'overview': self._get_overview(student_sequences),
            'performance': self._analyze_performance(student_sequences),
            'subject_analysis': self._analyze_by_subject(student_sequences),
            'topic_strengths': self._identify_strengths(student_performance),
            'topic_weaknesses': self._identify_weaknesses(student_performance),
            'recommendations': self._generate_recommendations(student_sequences, student_performance),
            'risk_assessment': self._assess_risk(student_sequences, student_performance)
        }

        return analytics

    def _get_overview(self, sequences: pd.DataFrame) -> Dict:
        """Get high-level overview"""
        return {
            'total_attempts': len(sequences),
            'overall_accuracy': sequences['is_correct'].mean(),
            'average_score': sequences['score'].mean(),
            'subjects_studied': sequences['subject'].nunique(),
            'topics_covered': sequences['topic'].nunique(),
            'performance_tier': self._get_performance_tier(sequences['is_correct'].mean())
        }

    def _analyze_performance(self, sequences: pd.DataFrame) -> Dict:
        """Analyze performance metrics"""
        overall_accuracy = sequences['is_correct'].mean()

        # Recent performance (last 30%)
        cutoff = int(len(sequences) * 0.7)
        recent = sequences.iloc[cutoff:]
        recent_accuracy = recent['is_correct'].mean()

        return {
            'overall_accuracy': overall_accuracy,
            'average_score': sequences['score'].mean(),
            'recent_accuracy': recent_accuracy,
            'improvement': recent_accuracy - overall_accuracy,
            'consistency_score': 1 - sequences['is_correct'].std()
        }

    def _analyze_by_subject(self, sequences: pd.DataFrame) -> Dict:
        """Analyze by subject"""
        subject_stats = {}

        for subject in sequences['subject'].unique():
            subject_data = sequences[sequences['subject'] == subject]

            subject_stats[subject] = {
                'attempts': len(subject_data),
                'accuracy': subject_data['is_correct'].mean(),
                'average_score': subject_data['score'].mean(),
                'performance_tier': self._get_performance_tier(subject_data['is_correct'].mean())
            }

        return subject_stats

    def _identify_strengths(self, performance: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """Identify strongest topics"""
        if len(performance) == 0:
            return []

        sufficient_data = performance[performance['total_attempts'] >= 3].copy()
        if len(sufficient_data) == 0:
            return []

        strengths = sufficient_data.nlargest(top_n, 'accuracy')

        result = []
        for _, row in strengths.iterrows():
            result.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'accuracy': row['accuracy'],
                'attempts': row['total_attempts'],
                'avg_score': row['avg_score'],
                'mastery_level': self._get_mastery_level(row['accuracy'])
            })

        return result

    def _identify_weaknesses(self, performance: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """Identify weakest topics"""
        if len(performance) == 0:
            return []

        sufficient_data = performance[performance['total_attempts'] >= 3].copy()
        if len(sufficient_data) == 0:
            return []

        weaknesses = sufficient_data.nsmallest(top_n, 'accuracy')

        result = []
        for _, row in weaknesses.iterrows():
            priority = 'High' if row['accuracy'] < 0.4 else 'Medium' if row['accuracy'] < 0.6 else 'Low'
            result.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'accuracy': row['accuracy'],
                'attempts': row['total_attempts'],
                'priority': priority
            })

        return result

    def _generate_recommendations(self, sequences: pd.DataFrame, performance: pd.DataFrame) -> List[Dict]:
        """Generate recommendations"""
        recommendations = []

        overall_accuracy = sequences['is_correct'].mean()

        # Low performance
        if overall_accuracy < 0.5:
            recommendations.append({
                'type': 'intervention',
                'priority': 'High',
                'message': 'Consider reviewing fundamental concepts',
                'action': 'Review basics in weakest topics'
            })

        # Recent trend
        cutoff = int(len(sequences) * 0.7)
        recent_accuracy = sequences.iloc[cutoff:]['is_correct'].mean()

        if recent_accuracy > overall_accuracy + 0.1:
            recommendations.append({
                'type': 'positive',
                'priority': 'Low',
                'message': 'Great improvement! Keep it up',
                'action': 'Continue current study approach'
            })
        elif recent_accuracy < overall_accuracy - 0.1:
            recommendations.append({
                'type': 'alert',
                'priority': 'Medium',
                'message': 'Recent performance declined',
                'action': 'Take a break or review recent topics'
            })

        # Weak topics
        if len(performance) > 0:
            weak_topics = performance[performance['accuracy'] < 0.6]
            if len(weak_topics) > 0:
                topic_list = ', '.join(weak_topics['topic'].head(3).tolist())
                recommendations.append({
                    'type': 'focus',
                    'priority': 'Medium',
                    'message': f'Focus on topics below 60% accuracy',
                    'action': f'Practice: {topic_list}'
                })

        return recommendations

    def _assess_risk(self, sequences: pd.DataFrame, performance: pd.DataFrame) -> Dict:
        """Assess student risk level"""
        risk_factors = []
        risk_score = 0

        # Low accuracy
        overall_accuracy = sequences['is_correct'].mean()
        if overall_accuracy < 0.4:
            risk_factors.append('Very low accuracy (<40%)')
            risk_score += 3
        elif overall_accuracy < 0.6:
            risk_factors.append('Below average accuracy (<60%)')
            risk_score += 2

        # Declining trend
        if len(sequences) >= 10:
            first_half = sequences.iloc[:len(sequences)//2]['is_correct'].mean()
            second_half = sequences.iloc[len(sequences)//2:]['is_correct'].mean()
            if second_half < first_half - 0.15:
                risk_factors.append('Declining performance')
                risk_score += 2

        # Multiple weak topics
        if len(performance) > 0:
            weak_count = len(performance[performance['accuracy'] < 0.5])
            if weak_count > 3:
                risk_factors.append(f'{weak_count} topics with <50% accuracy')
                risk_score += 2

        # Determine level
        if risk_score >= 5:
            risk_level = 'High'
        elif risk_score >= 3:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'needs_intervention': risk_score >= 4
        }

    # Helper methods
    def _get_performance_tier(self, accuracy: float) -> str:
        """Get performance tier"""
        for tier, threshold in self.performance_tiers.items():
            if accuracy >= threshold:
                return tier
        return 'Struggling'

    def _get_mastery_level(self, accuracy: float) -> str:
        """Get mastery level"""
        if accuracy >= 0.85:
            return 'Mastered'
        elif accuracy >= 0.70:
            return 'Proficient'
        elif accuracy >= 0.50:
            return 'Developing'
        else:
            return 'Novice'

    def _get_empty_analytics(self, student_id: str) -> Dict:
        """Empty analytics"""
        return {
            'student_id': student_id,
            'overview': {'total_attempts': 0, 'message': 'No data available'},
            'error': 'No learning data found'
        }


# Example usage
if __name__ == "__main__":
    from utils.data_loader import DataLoader

    loader = DataLoader()

    try:
        sequences = loader.load_learning_sequences()
        performance = loader.load_performance_history()

        analytics = StudentAnalytics()
        student_id = sequences['student_id'].iloc[0]

        print(f"\n📊 Analyzing student: {student_id}")
        print("="*60)

        results = analytics.analyze_student(student_id, sequences, performance)

        # Display overview
        print("\n📈 Overview:")
        overview = results['overview']
        print(f"   Total Attempts: {overview['total_attempts']}")
        print(f"   Overall Accuracy: {overview['overall_accuracy']:.1%}")
        print(f"   Average Score: {overview['average_score']:.1f}")
        print(f"   Performance Tier: {overview['performance_tier']}")

        # Strengths
        print("\n💪 Top Strengths:")
        for i, s in enumerate(results['topic_strengths'][:3], 1):
            print(f"   {i}. {s['topic']} - {s['accuracy']:.1%} ({s['mastery_level']})")

        # Weaknesses
        print("\n🎯 Areas for Improvement:")
        for i, w in enumerate(results['topic_weaknesses'][:3], 1):
            print(f"   {i}. {w['topic']} - {w['accuracy']:.1%} (Priority: {w['priority']})")

        # Recommendations
        print("\n💡 Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. [{rec['priority']}] {rec['message']}")

        # Risk
        print("\n⚠️  Risk Assessment:")
        risk = results['risk_assessment']
        print(f"   Level: {risk['risk_level']}")
        print(f"   Score: {risk['risk_score']}/10")
        if risk['risk_factors']:
            print(f"   Factors: {', '.join(risk['risk_factors'])}")

        print("\n="*60)
        print("✅ Analytics complete!")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
