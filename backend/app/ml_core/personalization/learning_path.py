"""
Learning Path Module
Generates personalized learning paths based on student performance and knowledge gaps
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


class LearningPathGenerator:
    """
    Generate personalized learning paths for students
    Based on knowledge gaps, prerequisites, and difficulty progression
    """

    def __init__(self):
        # Define topic prerequisites (simplified)
        self.prerequisites = {
            'Mathematics': {
                'Calculus': ['Algebra', 'Trigonometry'],
                'Differential Equations': ['Calculus'],
                'Vectors': ['Algebra'],
                'Matrices': ['Algebra'],
                'Probability': ['Statistics'],
                'Linear Programming': ['Algebra', 'Matrices']
            },
            'Physics': {
                'Electrostatics': [],
                'Current Electricity': ['Electrostatics'],
                'Magnetic Effects of Current': ['Current Electricity'],
                'Electromagnetic Induction': ['Magnetic Effects of Current'],
                'Optics': [],
                'Modern Physics': ['Optics'],
                'Mechanics': [],
                'Thermodynamics': ['Mechanics'],
                'Waves': ['Mechanics'],
                'Atomic Structure': []
            },
            'Chemistry': {
                'Chemical Kinetics': [],
                'Electrochemistry': ['Chemical Kinetics'],
                'Solutions': [],
                'Surface Chemistry': ['Solutions'],
                'Organic Chemistry': [],
                'Coordination Compounds': [],
                'p-Block Elements': [],
                'd-f Block Elements': ['p-Block Elements'],
                'Haloalkanes': ['Organic Chemistry'],
                'Polymers': ['Organic Chemistry']
            }
        }

        # Topic difficulty levels (1-5)
        self.topic_difficulty = {
            'Algebra': 1, 'Trigonometry': 2, 'Calculus': 3,
            'Statistics': 2, 'Probability': 3, 'Vectors': 3,
            'Matrices': 2, 'Differential Equations': 4,
            'Linear Programming': 3, 'Relations and Functions': 2,
            'Electrostatics': 2, 'Current Electricity': 3,
            'Magnetic Effects of Current': 3, 'Electromagnetic Induction': 4,
            'Optics': 2, 'Modern Physics': 4, 'Mechanics': 3,
            'Thermodynamics': 3, 'Waves': 3, 'Atomic Structure': 3,
            'Chemical Kinetics': 2, 'Electrochemistry': 3,
            'Solutions': 2, 'Surface Chemistry': 3,
            'Organic Chemistry': 4, 'Coordination Compounds': 3,
            'p-Block Elements': 2, 'd-f Block Elements': 3,
            'Haloalkanes': 3, 'Polymers': 4
        }

    def generate_learning_path(self, student_id: str,
                              learning_sequences: pd.DataFrame,
                              performance_history: pd.DataFrame,
                              max_topics: int = 5) -> Dict:
        """
        Generate personalized learning path for a student

        Args:
            student_id: Student identifier
            learning_sequences: DataFrame with learning history
            performance_history: DataFrame with performance records
            max_topics: Maximum topics to recommend

        Returns:
            Dict with learning path recommendations
        """
        # Get student data
        student_sequences = learning_sequences[
            learning_sequences['student_id'] == student_id
        ]
        student_performance = performance_history[
            performance_history['student_id'] == student_id
        ]

        if len(student_sequences) == 0:
            return self._get_default_path()

        # Analyze knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps(student_performance)

        # Get topic recommendations
        recommendations = self._generate_recommendations(
            student_performance, knowledge_gaps, max_topics
        )

        # Create learning path
        learning_path = self._create_learning_path(
            recommendations, student_performance
        )

        # Get next best topics
        next_topics = self._get_next_topics(
            student_performance, knowledge_gaps, max_topics
        )

        return {
            'student_id': student_id,
            'knowledge_gaps': knowledge_gaps,
            'recommended_topics': recommendations,
            'learning_path': learning_path,
            'next_topics': next_topics,
            'study_plan': self._create_study_plan(learning_path)
        }

    def _identify_knowledge_gaps(self, performance: pd.DataFrame) -> List[Dict]:
        """Identify topics where student is struggling"""
        if len(performance) == 0:
            return []

        # Filter topics with low accuracy
        gaps = performance[performance['accuracy'] < 0.7].copy()

        # Sort by accuracy (lowest first)
        gaps = gaps.sort_values('accuracy')

        gap_list = []
        for _, row in gaps.iterrows():
            gap_list.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'current_accuracy': row['accuracy'],
                'attempts': row['total_attempts'],
                'gap_severity': self._calculate_gap_severity(row['accuracy']),
                'priority': self._calculate_priority(row)
            })

        return gap_list

    def _calculate_gap_severity(self, accuracy: float) -> str:
        """Calculate severity of knowledge gap"""
        if accuracy < 0.4:
            return 'Critical'
        elif accuracy < 0.55:
            return 'High'
        elif accuracy < 0.7:
            return 'Medium'
        else:
            return 'Low'

    def _calculate_priority(self, row: pd.Series) -> int:
        """Calculate priority score for a topic (higher = more urgent)"""
        priority = 0

        # Accuracy component (lower accuracy = higher priority)
        priority += (1 - row['accuracy']) * 50

        # Attempts component (more attempts but still low = higher priority)
        priority += min(row['total_attempts'] / 5, 1) * 20

        # Recent performance component
        if 'recent_accuracy' in row.index:
            if row['recent_accuracy'] < row['accuracy']:
                priority += 10  # Declining performance

        return int(priority)

    def _generate_recommendations(self, performance: pd.DataFrame,
                                 knowledge_gaps: List[Dict],
                                 max_topics: int) -> List[Dict]:
        """Generate topic recommendations"""
        recommendations = []

        # Get all attempted topics
        attempted_topics = set(zip(performance['subject'], performance['topic']))

        # Recommend weak topics first
        for gap in knowledge_gaps[:max_topics]:
            recommendations.append({
                'subject': gap['subject'],
                'topic': gap['topic'],
                'reason': 'Knowledge Gap',
                'current_accuracy': gap['current_accuracy'],
                'target_accuracy': 0.85,
                'priority': gap['priority'],
                'recommended_practice': self._get_recommended_practice(gap)
            })

        # If we still have room, suggest new topics
        if len(recommendations) < max_topics:
            new_topics = self._suggest_new_topics(performance, attempted_topics)
            recommendations.extend(new_topics[:max_topics - len(recommendations)])

        return recommendations

    def _get_recommended_practice(self, gap: Dict) -> Dict:
        """Get recommended practice for a knowledge gap"""
        severity = gap['gap_severity']

        if severity == 'Critical':
            return {
                'num_questions': 20,
                'difficulty_distribution': {'Easy': 0.6, 'Medium': 0.3, 'Hard': 0.1},
                'focus': 'Fundamentals and basic concepts',
                'estimated_time': '60-90 minutes'
            }
        elif severity == 'High':
            return {
                'num_questions': 15,
                'difficulty_distribution': {'Easy': 0.4, 'Medium': 0.4, 'Hard': 0.2},
                'focus': 'Core concepts and applications',
                'estimated_time': '45-60 minutes'
            }
        else:
            return {
                'num_questions': 10,
                'difficulty_distribution': {'Easy': 0.2, 'Medium': 0.5, 'Hard': 0.3},
                'focus': 'Advanced practice and problem-solving',
                'estimated_time': '30-45 minutes'
            }

    def _suggest_new_topics(self, performance: pd.DataFrame,
                           attempted_topics: set) -> List[Dict]:
        """Suggest new topics based on prerequisites"""
        suggestions = []

        # Get mastered topics
        mastered = performance[performance['accuracy'] >= 0.85]
        mastered_topics = set(zip(mastered['subject'], mastered['topic']))

        # Check what new topics are unlocked
        for subject, prereq_map in self.prerequisites.items():
            for topic, prereqs in prereq_map.items():
                # Skip if already attempted
                if (subject, topic) in attempted_topics:
                    continue

                # Check if prerequisites are met
                if self._prerequisites_met(subject, prereqs, mastered_topics):
                    difficulty = self.topic_difficulty.get(topic, 3)

                    suggestions.append({
                        'subject': subject,
                        'topic': topic,
                        'reason': 'Prerequisites Met',
                        'prerequisites': prereqs,
                        'difficulty_level': difficulty,
                        'priority': 50 - (difficulty * 5)  # Easier topics first
                    })

        # Sort by priority
        suggestions.sort(key=lambda x: x['priority'], reverse=True)

        return suggestions

    def _prerequisites_met(self, subject: str, prereqs: List[str],
                          mastered_topics: set) -> bool:
        """Check if prerequisites are met"""
        if not prereqs:
            return True

        for prereq in prereqs:
            if (subject, prereq) not in mastered_topics:
                return False

        return True

    def _create_learning_path(self, recommendations: List[Dict],
                             performance: pd.DataFrame) -> List[Dict]:
        """Create sequential learning path"""
        path = []

        # Sort recommendations by priority
        sorted_recs = sorted(recommendations, key=lambda x: x.get('priority', 0), reverse=True)

        for i, rec in enumerate(sorted_recs, 1):
            step = {
                'step': i,
                'subject': rec['subject'],
                'topic': rec['topic'],
                'reason': rec['reason'],
                'estimated_duration': rec.get('recommended_practice', {}).get('estimated_time', '30-45 minutes'),
                'learning_objectives': self._get_learning_objectives(rec['topic']),
                'success_criteria': 'Achieve 85% accuracy on practice questions'
            }

            path.append(step)

        return path

    def _get_learning_objectives(self, topic: str) -> List[str]:
        """Get learning objectives for a topic"""
        # Simplified objectives (in real system, would be topic-specific)
        objectives = [
            f'Understand fundamental concepts of {topic}',
            f'Apply {topic} principles to solve problems',
            f'Analyze complex scenarios involving {topic}'
        ]

        return objectives

    def _get_next_topics(self, performance: pd.DataFrame,
                        knowledge_gaps: List[Dict],
                        max_topics: int) -> List[Dict]:
        """Get immediate next topics to practice"""
        next_topics = []

        # Prioritize critical gaps
        critical_gaps = [g for g in knowledge_gaps if g['gap_severity'] in ['Critical', 'High']]

        if critical_gaps:
            # Focus on critical gaps
            for gap in critical_gaps[:max_topics]:
                next_topics.append({
                    'subject': gap['subject'],
                    'topic': gap['topic'],
                    'action': 'Review and Practice',
                    'urgency': 'High',
                    'current_level': self._get_mastery_level(gap['current_accuracy']),
                    'target_level': 'Proficient'
                })
        else:
            # Look for topics to advance
            proficient = performance[
                (performance['accuracy'] >= 0.7) & (performance['accuracy'] < 0.85)
            ].sort_values('accuracy')

            for _, row in proficient.head(max_topics).iterrows():
                next_topics.append({
                    'subject': row['subject'],
                    'topic': row['topic'],
                    'action': 'Advance to Mastery',
                    'urgency': 'Medium',
                    'current_level': 'Proficient',
                    'target_level': 'Mastered'
                })

        return next_topics

    def _create_study_plan(self, learning_path: List[Dict]) -> Dict:
        """Create a structured study plan"""
        if not learning_path:
            return {}

        # Calculate total estimated time
        total_time = 0
        for step in learning_path:
            time_str = step.get('estimated_duration', '30-45 minutes')
            # Extract average time (simplified)
            if '30-45' in time_str:
                total_time += 37.5
            elif '45-60' in time_str:
                total_time += 52.5
            elif '60-90' in time_str:
                total_time += 75

        # Create weekly plan
        sessions_per_week = 5  # Assume 5 study sessions per week
        topics_per_session = max(1, len(learning_path) // sessions_per_week)

        weekly_plan = []
        for i in range(0, len(learning_path), topics_per_session):
            session = learning_path[i:i+topics_per_session]
            weekly_plan.append({
                'session': len(weekly_plan) + 1,
                'topics': [s['topic'] for s in session],
                'subjects': list(set(s['subject'] for s in session)),
                'duration': f"{topics_per_session * 40} minutes"
            })

        return {
            'total_topics': len(learning_path),
            'total_estimated_time_minutes': total_time,
            'estimated_completion_weeks': len(weekly_plan) // sessions_per_week + 1,
            'sessions_per_week': sessions_per_week,
            'weekly_breakdown': weekly_plan[:4]  # Show first 4 weeks
        }

    def _get_mastery_level(self, accuracy: float) -> str:
        """Get mastery level from accuracy"""
        if accuracy >= 0.85:
            return 'Mastered'
        elif accuracy >= 0.70:
            return 'Proficient'
        elif accuracy >= 0.50:
            return 'Developing'
        else:
            return 'Novice'

    def _get_default_path(self) -> Dict:
        """Return default path for new students"""
        return {
            'message': 'No learning history available',
            'recommended_topics': [
                {'subject': 'Mathematics', 'topic': 'Algebra', 'reason': 'Foundational'},
                {'subject': 'Physics', 'topic': 'Mechanics', 'reason': 'Foundational'},
                {'subject': 'Chemistry', 'topic': 'Chemical Kinetics', 'reason': 'Foundational'}
            ]
        }


# Example usage
if __name__ == "__main__":
    from utils.data_loader import DataLoader

    loader = DataLoader()

    try:
        sequences = loader.load_learning_sequences()
        performance = loader.load_performance_history()

        generator = LearningPathGenerator()

        student_id = sequences['student_id'].iloc[0]

        print(f"\n📚 Generating Learning Path for {student_id}")
        print("="*60)

        path = generator.generate_learning_path(
            student_id, sequences, performance, max_topics=5
        )

        # Knowledge gaps
        print("\n🎯 Knowledge Gaps:")
        for i, gap in enumerate(path['knowledge_gaps'][:5], 1):
            print(f"   {i}. {gap['topic']} ({gap['subject']})")
            print(f"      Accuracy: {gap['current_accuracy']:.1%}, Severity: {gap['gap_severity']}")

        # Recommended topics
        print("\n💡 Recommended Topics:")
        for i, rec in enumerate(path['recommended_topics'], 1):
            print(f"   {i}. {rec['topic']} ({rec['subject']})")
            print(f"      Reason: {rec['reason']}")
            if 'current_accuracy' in rec:
                print(f"      Current: {rec['current_accuracy']:.1%} → Target: {rec['target_accuracy']:.1%}")

        # Learning path
        print("\n🗺️ Learning Path:")
        for step in path['learning_path'][:5]:
            print(f"   Step {step['step']}: {step['topic']} ({step['subject']})")
            print(f"      Duration: {step['estimated_duration']}")

        # Next topics
        print("\n⏭️ Next Topics to Practice:")
        for i, topic in enumerate(path['next_topics'], 1):
            print(f"   {i}. {topic['topic']} ({topic['subject']})")
            print(f"      Action: {topic['action']}, Urgency: {topic['urgency']}")

        # Study plan
        if 'study_plan' in path and path['study_plan']:
            print("\n📅 Study Plan:")
            plan = path['study_plan']
            print(f"   Total Topics: {plan['total_topics']}")
            print(f"   Estimated Time: {plan['total_estimated_time_minutes']:.0f} minutes")
            print(f"   Completion: ~{plan['estimated_completion_weeks']} weeks")
            print(f"   Sessions per Week: {plan['sessions_per_week']}")

        print("\n="*60)
        print("✅ Learning path generated!")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
