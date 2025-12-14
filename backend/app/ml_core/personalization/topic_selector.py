"""
Topic Selector Module - FIXED VERSION
Smart topic selection using spaced repetition, prerequisites, and diversity balancing
Ensures optimal learning coverage and retention
"""

import sys
import os

# Fix imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class TopicSelector:
    """
    Intelligent topic selection engine
    Balances review, new content, weak areas, and diversity
    FIXED: Prevents duplicate topic selection
    """

    def __init__(self):
        # Selection strategies weights
        self.strategy_weights = {
            'remediation': 0.4,      # Focus on weak topics
            'advancement': 0.3,      # Progress to new topics
            'review': 0.2,           # Spaced repetition
            'diversity': 0.1         # Subject/topic variety
        }

        # Spaced repetition intervals (in days)
        self.review_intervals = {
            'new': 0,           # Just learned
            'learning': 1,      # Review next day
            'young': 3,         # Review after 3 days
            'mature': 7,        # Review after 1 week
            'mastered': 14      # Review after 2 weeks
        }

        # Prerequisites (simplified - matches learning_path.py)
        self.prerequisites = {
            'Mathematics': {
                'Calculus': ['Algebra'],
                'Differential Equations': ['Calculus'],
                'Vectors': ['Algebra'],
                'Probability': ['Statistics']
            },
            'Physics': {
                'Current Electricity': ['Electrostatics'],
                'Magnetic Effects of Current': ['Current Electricity'],
                'Electromagnetic Induction': ['Magnetic Effects of Current'],
                'Modern Physics': ['Optics']
            },
            'Chemistry': {
                'Electrochemistry': ['Chemical Kinetics'],
                'Surface Chemistry': ['Solutions'],
                'd-f Block Elements': ['p-Block Elements'],
                'Haloalkanes': ['Organic Chemistry'],
                'Polymers': ['Organic Chemistry']
            }
        }

    def select_topics(self, student_id: str,
                     performance_history: pd.DataFrame,
                     learning_sequences: pd.DataFrame,
                     num_topics: int = 5,
                     strategy: str = 'balanced') -> List[Dict]:
        """
        Select optimal topics for next assignment

        Args:
            student_id: Student identifier
            performance_history: Student's performance records
            learning_sequences: Student's learning history
            num_topics: Number of topics to select
            strategy: 'remediation', 'advancement', or 'balanced'

        Returns:
            List of selected topics with reasoning
        """
        # Filter student data
        student_perf = performance_history[
            performance_history['student_id'] == student_id
        ]
        student_seq = learning_sequences[
            learning_sequences['student_id'] == student_id
        ]

        if len(student_perf) == 0:
            return self._get_default_topics(num_topics)

        # Categorize topics
        weak_topics = self._identify_weak_topics(student_perf)
        review_topics = self._identify_review_topics(student_seq)
        unlocked_topics = self._identify_unlocked_topics(student_perf)

        # Apply strategy
        if strategy == 'remediation':
            weights = {'remediation': 0.7, 'review': 0.2, 'advancement': 0.1, 'diversity': 0.0}
        elif strategy == 'advancement':
            weights = {'advancement': 0.6, 'remediation': 0.2, 'review': 0.1, 'diversity': 0.1}
        else:  # balanced
            weights = self.strategy_weights

        # FIXED: Select topics with duplicate prevention
        selected = self._weighted_selection(
            weak_topics, review_topics, unlocked_topics,
            weights, num_topics
        )

        # Ensure diversity
        selected = self._ensure_diversity(selected, num_topics)

        return selected

    def get_next_topic(self, recent_topics: List[str],
                      available_topics: List[Dict],
                      current_performance: Dict) -> Dict:
        """
        Select next topic during active session

        Args:
            recent_topics: Topics covered in last few questions
            available_topics: Pool of topics to choose from
            current_performance: Current session performance metrics

        Returns:
            Next recommended topic
        """
        # Avoid immediate repetition
        if len(recent_topics) >= 2:
            # Don't repeat last 2 topics
            available = [t for t in available_topics 
                        if t['topic'] not in recent_topics[-2:]]
        else:
            available = available_topics

        if not available:
            available = available_topics

        # Prioritize based on current performance
        session_accuracy = current_performance.get('session_accuracy', 0.7)

        if session_accuracy < 0.5:
            # Struggling - pick easier topic
            sorted_topics = sorted(available, 
                                  key=lambda x: x.get('difficulty_score', 0.5))
        elif session_accuracy > 0.85:
            # Excelling - pick harder topic
            sorted_topics = sorted(available, 
                                  key=lambda x: x.get('difficulty_score', 0.5),
                                  reverse=True)
        else:
            # Balanced - use variety
            sorted_topics = available

        return sorted_topics[0] if sorted_topics else available_topics[0]

    def calculate_topic_priority(self, topic_data: Dict) -> float:
        """
        Calculate priority score for a topic (0-100)

        Args:
            topic_data: Dict with topic performance and metadata

        Returns:
            Priority score (higher = more urgent)
        """
        priority = 0.0

        # Factor 1: Accuracy (lower = higher priority)
        accuracy = topic_data.get('accuracy', 0.7)
        if accuracy < 0.5:
            priority += 40  # Critical
        elif accuracy < 0.7:
            priority += 25  # Important
        elif accuracy < 0.85:
            priority += 10  # Moderate

        # Factor 2: Days since last practice
        days_since = topic_data.get('days_since_practice', 0)
        if days_since > 14:
            priority += 20  # Needs review
        elif days_since > 7:
            priority += 10
        elif days_since > 3:
            priority += 5

        # Factor 3: Number of attempts (fewer = less familiar)
        attempts = topic_data.get('total_attempts', 0)
        if attempts < 3:
            priority += 15  # Need more practice
        elif attempts < 5:
            priority += 10

        # Factor 4: Prerequisites met
        if topic_data.get('prerequisites_met', True):
            priority += 0  # Ready to learn
        else:
            priority -= 30  # Not ready yet

        # Factor 5: Importance (if specified)
        priority += topic_data.get('importance', 0)

        return min(priority, 100)

    def balance_subject_distribution(self, topics: List[Dict],
                                    target_distribution: Dict = None) -> List[Dict]:
        """
        Ensure balanced distribution across subjects

        Args:
            topics: List of topic recommendations
            target_distribution: Desired subject distribution (optional)

        Returns:
            Balanced topic list
        """
        if not target_distribution:
            # Default: equal distribution
            target_distribution = {
                'Mathematics': 0.33,
                'Physics': 0.33,
                'Chemistry': 0.34
            }

        # Current distribution
        subject_counts = {}
        for topic in topics:
            subject = topic.get('subject', 'Unknown')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1

        total = len(topics)
        balanced = []
        remaining = topics.copy()

        # Fill to target distribution
        for subject, target_pct in target_distribution.items():
            target_count = int(total * target_pct)
            subject_topics = [t for t in remaining if t.get('subject') == subject]

            # Add up to target count
            for topic in subject_topics[:target_count]:
                balanced.append(topic)
                remaining.remove(topic)

        # Add any remaining topics
        balanced.extend(remaining)

        return balanced[:total]

    def implement_spaced_repetition(self, topic_history: pd.DataFrame,
                                   current_date: datetime = None) -> List[Dict]:
        """
        Identify topics due for review based on spaced repetition

        Args:
            topic_history: DataFrame with topic practice history
            current_date: Current date (defaults to now)

        Returns:
            List of topics due for review
        """
        if current_date is None:
            current_date = datetime.now()

        due_topics = []

        # Group by topic
        for topic_name in topic_history['topic'].unique():
            topic_data = topic_history[topic_history['topic'] == topic_name]

            # Get last practice date
            if 'timestamp' in topic_data.columns:
                last_practice = pd.to_datetime(topic_data['timestamp']).max()
                days_since = (current_date - last_practice).days
            else:
                days_since = 999  # Very old

            # Determine mastery level
            accuracy = topic_data['is_correct'].mean()
            mastery_level = self._determine_mastery_level(accuracy)

            # Check if review is due
            review_interval = self.review_intervals.get(mastery_level, 7)

            if days_since >= review_interval:
                due_topics.append({
                    'subject': topic_data['subject'].iloc[0],
                    'topic': topic_name,
                    'days_since_practice': days_since,
                    'accuracy': accuracy,
                    'mastery_level': mastery_level,
                    'reason': f'Due for review ({days_since} days since practice)',
                    'priority': self._calculate_review_priority(days_since, accuracy)
                })

        # Sort by priority
        due_topics.sort(key=lambda x: x['priority'], reverse=True)

        return due_topics

    # Helper methods

    def _identify_weak_topics(self, performance: pd.DataFrame,
                             threshold: float = 0.7) -> List[Dict]:
        """Identify topics where student is struggling"""
        weak = performance[performance['accuracy'] < threshold].copy()

        weak_topics = []
        for _, row in weak.iterrows():
            weak_topics.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'accuracy': row['accuracy'],
                'attempts': row['total_attempts'],
                'reason': 'Remediation needed',
                'priority': self.calculate_topic_priority({
                    'accuracy': row['accuracy'],
                    'total_attempts': row['total_attempts']
                }),
                'category': 'weak'
            })

        # Sort by priority
        weak_topics.sort(key=lambda x: x['priority'], reverse=True)

        return weak_topics

    def _identify_review_topics(self, sequences: pd.DataFrame,
                               days_threshold: int = 7) -> List[Dict]:
        """Identify topics needing review based on time"""
        if 'timestamp' not in sequences.columns:
            return []

        current_date = datetime.now()
        review_topics = []

        # Group by topic
        for topic_name in sequences['topic'].unique():
            topic_data = sequences[sequences['topic'] == topic_name]

            last_practice = pd.to_datetime(topic_data['timestamp']).max()
            days_since = (current_date - last_practice).days

            if days_since >= days_threshold:
                accuracy = topic_data['is_correct'].mean()

                review_topics.append({
                    'subject': topic_data['subject'].iloc[0],
                    'topic': topic_name,
                    'accuracy': accuracy,
                    'days_since_practice': days_since,
                    'reason': 'Spaced repetition review',
                    'priority': self._calculate_review_priority(days_since, accuracy),
                    'category': 'review'
                })

        review_topics.sort(key=lambda x: x['priority'], reverse=True)

        return review_topics

    def _identify_unlocked_topics(self, performance: pd.DataFrame) -> List[Dict]:
        """Identify new topics with prerequisites met"""
        # Get mastered topics
        mastered = performance[performance['accuracy'] >= 0.85]
        mastered_set = set(zip(mastered['subject'], mastered['topic']))

        # Get attempted topics
        attempted_set = set(zip(performance['subject'], performance['topic']))

        unlocked = []

        # Check each subject
        for subject, prereq_map in self.prerequisites.items():
            for topic, prereqs in prereq_map.items():
                # Skip if already attempted
                if (subject, topic) in attempted_set:
                    continue

                # Check prerequisites
                prereqs_met = all(
                    (subject, prereq) in mastered_set
                    for prereq in prereqs
                )

                if prereqs_met or not prereqs:  # No prereqs or all met
                    unlocked.append({
                        'subject': subject,
                        'topic': topic,
                        'reason': 'Prerequisites met - ready for new content',
                        'prerequisites': prereqs,
                        'priority': 50,  # Moderate priority
                        'category': 'unlocked'
                    })

        return unlocked

    def _weighted_selection(self, weak: List[Dict], review: List[Dict],
                          unlocked: List[Dict], weights: Dict,
                          num_topics: int) -> List[Dict]:
        """
        Select topics based on weighted strategy
        FIXED: Prevents duplicate topic selection
        """
        selected = []
        seen_topics = set()  # Track (subject, topic) pairs to prevent duplicates

        # Calculate number of topics from each category
        num_weak = int(num_topics * weights['remediation'])
        num_review = int(num_topics * weights['review'])
        num_unlocked = int(num_topics * weights['advancement'])

        # Helper function to add unique topics
        def add_unique_topics(source_list: List[Dict], max_count: int):
            added = 0
            for topic in source_list:
                if added >= max_count:
                    break

                topic_key = (topic['subject'], topic['topic'])
                if topic_key not in seen_topics:
                    selected.append(topic)
                    seen_topics.add(topic_key)
                    added += 1

        # Select from each category (checking for duplicates)
        add_unique_topics(weak, num_weak)
        add_unique_topics(review, num_review)
        add_unique_topics(unlocked, num_unlocked)

        # Fill remaining slots with highest priority topics (no duplicates)
        remaining_needed = num_topics - len(selected)
        if remaining_needed > 0:
            # Combine all topics and sort by priority
            all_topics = weak + review + unlocked
            all_topics.sort(key=lambda x: x['priority'], reverse=True)

            add_unique_topics(all_topics, remaining_needed)

        return selected[:num_topics]

    def _ensure_diversity(self, topics: List[Dict], num_topics: int) -> List[Dict]:
        """Ensure variety across subjects"""
        if len(topics) <= 1:
            return topics

        # Count subjects
        subject_counts = {}
        for topic in topics:
            subject = topic.get('subject', 'Unknown')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1

        # If one subject dominates (>60%), rebalance
        max_count = max(subject_counts.values())
        if max_count > num_topics * 0.6:
            topics = self.balance_subject_distribution(topics)

        return topics

    def _determine_mastery_level(self, accuracy: float) -> str:
        """Determine mastery level from accuracy"""
        if accuracy >= 0.90:
            return 'mastered'
        elif accuracy >= 0.75:
            return 'mature'
        elif accuracy >= 0.60:
            return 'young'
        elif accuracy >= 0.40:
            return 'learning'
        else:
            return 'new'

    def _calculate_review_priority(self, days_since: int, accuracy: float) -> float:
        """Calculate priority for review topics"""
        # Base priority on days overdue
        priority = min(days_since / 7 * 30, 40)

        # Adjust based on accuracy (lower accuracy = higher priority)
        if accuracy < 0.6:
            priority += 20
        elif accuracy < 0.8:
            priority += 10

        return priority

    def _get_default_topics(self, num_topics: int) -> List[Dict]:
        """Get default topics for new students"""
        default = [
            {'subject': 'Mathematics', 'topic': 'Algebra', 'reason': 'Foundational', 'priority': 80},
            {'subject': 'Physics', 'topic': 'Mechanics', 'reason': 'Foundational', 'priority': 80},
            {'subject': 'Chemistry', 'topic': 'Chemical Kinetics', 'reason': 'Foundational', 'priority': 80},
            {'subject': 'Mathematics', 'topic': 'Statistics', 'reason': 'Core concept', 'priority': 70},
            {'subject': 'Physics', 'topic': 'Electrostatics', 'reason': 'Core concept', 'priority': 70}
        ]

        return default[:num_topics]


# Example usage
if __name__ == "__main__":
    from utils.data_loader import DataLoader

    loader = DataLoader()

    try:
        sequences = loader.load_learning_sequences()
        performance = loader.load_performance_history()

        selector = TopicSelector()

        student_id = sequences['student_id'].iloc[0]

        print(f"\n🎯 Topic Selection for {student_id} (FIXED - No Duplicates)")
        print("="*60)

        # Select topics
        selected = selector.select_topics(
            student_id, performance, sequences,
            num_topics=5, strategy='balanced'
        )

        print("\n📚 Selected Topics (Balanced Strategy):")
        for i, topic in enumerate(selected, 1):
            print(f"\n{i}. {topic['topic']} ({topic['subject']})")
            print(f"   Reason: {topic['reason']}")
            print(f"   Priority: {topic['priority']:.0f}/100")
            if 'accuracy' in topic:
                print(f"   Current Accuracy: {topic['accuracy']:.1%}")
            if 'category' in topic:
                print(f"   Category: {topic['category']}")

        # Verify no duplicates
        print("\n\n✅ Duplicate Check:")
        print("-"*60)
        topics_set = set()
        duplicates_found = False
        for topic in selected:
            topic_key = (topic['subject'], topic['topic'])
            if topic_key in topics_set:
                print(f"   ❌ DUPLICATE: {topic['topic']} ({topic['subject']})")
                duplicates_found = True
            topics_set.add(topic_key)

        if not duplicates_found:
            print(f"   ✅ All {len(selected)} topics are unique!")

        # Topic priorities
        print("\n\n📊 Topic Priority Calculation Example:")
        print("-"*60)
        example_topic = {
            'accuracy': 0.45,
            'days_since_practice': 10,
            'total_attempts': 4,
            'prerequisites_met': True,
            'importance': 5
        }

        priority = selector.calculate_topic_priority(example_topic)
        print(f"Topic with 45% accuracy, 10 days since practice, 4 attempts:")
        print(f"   Priority Score: {priority:.0f}/100")

        # Spaced repetition
        print("\n\n📅 Spaced Repetition Analysis:")
        print("-"*60)
        student_sequences = sequences[sequences['student_id'] == student_id]
        due_topics = selector.implement_spaced_repetition(student_sequences)

        if due_topics:
            print(f"Found {len(due_topics)} topics due for review:")
            for topic in due_topics[:3]:
                print(f"\n   • {topic['topic']} ({topic['subject']})")
                print(f"     Last practiced: {topic['days_since_practice']} days ago")
                print(f"     Accuracy: {topic['accuracy']:.1%}")
                print(f"     Mastery: {topic['mastery_level']}")
        else:
            print("   No topics currently due for review")

        print("\n="*60)
        print("✅ Topic selection complete (with duplicate prevention)!")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
