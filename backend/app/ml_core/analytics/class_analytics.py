"""
Topic Analytics Module
Analyzes topics across all students to identify difficulty, engagement, and patterns
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


class TopicAnalytics:
    """
    Analyze topics across all students
    Provides insights into topic difficulty, engagement, and success patterns
    """

    def __init__(self):
        self.difficulty_levels = {
            'Very Easy': (0.85, 1.0),
            'Easy': (0.75, 0.85),
            'Moderate': (0.60, 0.75),
            'Difficult': (0.45, 0.60),
            'Very Difficult': (0.0, 0.45)
        }

    def analyze_all_topics(self, learning_sequences: pd.DataFrame,
                          performance_history: pd.DataFrame) -> Dict:
        """
        Analyze all topics across all students

        Args:
            learning_sequences: DataFrame with learning interactions
            performance_history: DataFrame with performance records

        Returns:
            Dict with comprehensive topic analytics
        """
        analytics = {
            'overview': self._get_overview(learning_sequences, performance_history),
            'topic_rankings': self._rank_topics(performance_history),
            'difficulty_analysis': self._analyze_difficulty(learning_sequences),
            'engagement_metrics': self._analyze_engagement(learning_sequences),
            'subject_comparison': self._compare_subjects(learning_sequences),
            'challenging_topics': self._identify_challenging_topics(performance_history),
            'popular_topics': self._identify_popular_topics(learning_sequences),
            'recommendations': self._generate_topic_recommendations(learning_sequences, performance_history)
        }

        return analytics

    def analyze_topic(self, topic: str, subject: str,
                     learning_sequences: pd.DataFrame,
                     performance_history: pd.DataFrame) -> Dict:
        """
        Analyze a specific topic in detail

        Args:
            topic: Topic name
            subject: Subject name
            learning_sequences: DataFrame with learning interactions
            performance_history: DataFrame with performance records

        Returns:
            Dict with detailed topic analytics
        """
        # Filter topic data
        topic_sequences = learning_sequences[
            (learning_sequences['topic'] == topic) &
            (learning_sequences['subject'] == subject)
        ].copy()

        topic_performance = performance_history[
            (performance_history['topic'] == topic) &
            (performance_history['subject'] == subject)
        ].copy()

        if len(topic_sequences) == 0:
            return self._get_empty_topic_analytics(topic, subject)

        analytics = {
            'topic': topic,
            'subject': subject,
            'statistics': self._get_topic_statistics(topic_sequences, topic_performance),
            'student_performance': self._analyze_student_performance(topic_performance),
            'difficulty_breakdown': self._analyze_topic_difficulty(topic_sequences),
            'bloom_distribution': self._analyze_bloom_distribution(topic_sequences),
            'time_analysis': self._analyze_time_patterns(topic_sequences),
            'mastery_distribution': self._analyze_mastery_distribution(topic_performance),
            'success_factors': self._identify_success_factors(topic_sequences)
        }

        return analytics

    def _get_overview(self, sequences: pd.DataFrame, performance: pd.DataFrame) -> Dict:
        """Get high-level overview of all topics"""
        return {
            'total_topics': sequences['topic'].nunique(),
            'total_subjects': sequences['subject'].nunique(),
            'total_interactions': len(sequences),
            'total_students': sequences['student_id'].nunique(),
            'overall_success_rate': sequences['is_correct'].mean(),
            'average_score': sequences['score'].mean(),
            'topics_per_subject': sequences.groupby('subject')['topic'].nunique().to_dict()
        }

    def _rank_topics(self, performance: pd.DataFrame, top_n: int = 10) -> Dict:
        """Rank topics by various metrics"""
        # Group by topic
        topic_stats = performance.groupby(['subject', 'topic']).agg({
            'accuracy': 'mean',
            'total_attempts': 'sum',
            'avg_score': 'mean',
            'student_id': 'count'  # Number of students
        }).reset_index()

        topic_stats.columns = ['subject', 'topic', 'avg_accuracy', 'total_attempts', 
                              'avg_score', 'num_students']

        # Rankings
        easiest = topic_stats.nlargest(top_n, 'avg_accuracy')[
            ['subject', 'topic', 'avg_accuracy', 'num_students']
        ].to_dict('records')

        hardest = topic_stats.nsmallest(top_n, 'avg_accuracy')[
            ['subject', 'topic', 'avg_accuracy', 'num_students']
        ].to_dict('records')

        most_attempted = topic_stats.nlargest(top_n, 'total_attempts')[
            ['subject', 'topic', 'total_attempts', 'num_students']
        ].to_dict('records')

        highest_scoring = topic_stats.nlargest(top_n, 'avg_score')[
            ['subject', 'topic', 'avg_score', 'num_students']
        ].to_dict('records')

        return {
            'easiest_topics': easiest,
            'hardest_topics': hardest,
            'most_attempted': most_attempted,
            'highest_scoring': highest_scoring
        }

    def _analyze_difficulty(self, sequences: pd.DataFrame) -> Dict:
        """Analyze actual difficulty vs labeled difficulty"""
        # Success rate by labeled difficulty
        difficulty_stats = sequences.groupby('difficulty').agg({
            'is_correct': 'mean',
            'score': 'mean',
            'student_id': 'count'
        }).reset_index()

        difficulty_stats.columns = ['difficulty', 'success_rate', 'avg_score', 'count']

        # Calculate actual difficulty level for each topic
        topic_difficulty = sequences.groupby(['subject', 'topic']).agg({
            'is_correct': 'mean',
            'student_id': 'nunique'
        }).reset_index()

        topic_difficulty['perceived_difficulty'] = topic_difficulty['is_correct'].apply(
            self._classify_difficulty
        )

        return {
            'by_labeled_difficulty': difficulty_stats.to_dict('records'),
            'topic_difficulty_classification': topic_difficulty.to_dict('records')
        }

    def _analyze_engagement(self, sequences: pd.DataFrame) -> Dict:
        """Analyze topic engagement patterns"""
        topic_engagement = sequences.groupby(['subject', 'topic']).agg({
            'student_id': 'nunique',
            'is_correct': 'count',
            'time_spent_seconds': 'mean'
        }).reset_index()

        topic_engagement.columns = ['subject', 'topic', 'unique_students', 
                                    'total_attempts', 'avg_time']

        # Calculate engagement score
        max_students = topic_engagement['unique_students'].max()
        topic_engagement['engagement_score'] = (
            topic_engagement['unique_students'] / max_students * 0.6 +
            np.log1p(topic_engagement['total_attempts']) / np.log1p(topic_engagement['total_attempts'].max()) * 0.4
        )

        topic_engagement['engagement_level'] = topic_engagement['engagement_score'].apply(
            lambda x: 'High' if x > 0.7 else 'Medium' if x > 0.4 else 'Low'
        )

        return topic_engagement.to_dict('records')

    def _compare_subjects(self, sequences: pd.DataFrame) -> Dict:
        """Compare performance across subjects"""
        subject_stats = sequences.groupby('subject').agg({
            'is_correct': 'mean',
            'score': 'mean',
            'topic': 'nunique',
            'student_id': 'nunique',
            'time_spent_seconds': 'mean'
        }).reset_index()

        subject_stats.columns = ['subject', 'success_rate', 'avg_score', 
                                'num_topics', 'num_students', 'avg_time']

        return subject_stats.to_dict('records')

    def _identify_challenging_topics(self, performance: pd.DataFrame, 
                                    threshold: float = 0.5) -> List[Dict]:
        """Identify topics that students find challenging"""
        # Filter topics with low success rates
        challenging = performance[performance['accuracy'] < threshold].copy()

        # Group by topic
        topic_challenges = challenging.groupby(['subject', 'topic']).agg({
            'accuracy': 'mean',
            'student_id': 'count',
            'total_attempts': 'sum'
        }).reset_index()

        topic_challenges = topic_challenges.sort_values('accuracy')

        result = []
        for _, row in topic_challenges.iterrows():
            result.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'average_accuracy': row['accuracy'],
                'students_struggling': row['student_id'],
                'total_attempts': row['total_attempts'],
                'severity': 'High' if row['accuracy'] < 0.35 else 'Medium'
            })

        return result

    def _identify_popular_topics(self, sequences: pd.DataFrame, top_n: int = 10) -> List[Dict]:
        """Identify most popular topics by student engagement"""
        topic_popularity = sequences.groupby(['subject', 'topic']).agg({
            'student_id': 'nunique',
            'is_correct': ['count', 'mean']
        }).reset_index()

        topic_popularity.columns = ['subject', 'topic', 'num_students', 
                                    'total_attempts', 'success_rate']

        # Sort by number of unique students
        popular = topic_popularity.nlargest(top_n, 'num_students')

        return popular.to_dict('records')

    def _generate_topic_recommendations(self, sequences: pd.DataFrame,
                                       performance: pd.DataFrame) -> List[Dict]:
        """Generate recommendations for curriculum improvement"""
        recommendations = []

        # Check for topics with low success rates
        topic_success = performance.groupby(['subject', 'topic'])['accuracy'].mean()
        low_success = topic_success[topic_success < 0.5]

        if len(low_success) > 0:
            recommendations.append({
                'type': 'curriculum',
                'priority': 'High',
                'message': f'{len(low_success)} topics have <50% success rate',
                'action': 'Review teaching materials and add more examples',
                'affected_topics': low_success.head(5).index.tolist()
            })

        # Check for topics with low engagement
        topic_engagement = sequences.groupby(['subject', 'topic'])['student_id'].nunique()
        total_students = sequences['student_id'].nunique()
        low_engagement = topic_engagement[topic_engagement < total_students * 0.3]

        if len(low_engagement) > 0:
            recommendations.append({
                'type': 'engagement',
                'priority': 'Medium',
                'message': f'{len(low_engagement)} topics have low student engagement',
                'action': 'Make topics more interactive or relevant',
                'affected_topics': low_engagement.head(5).index.tolist()
            })

        # Check for difficulty balance
        difficulty_dist = sequences.groupby('difficulty').size()
        if 'Hard' in difficulty_dist.index and difficulty_dist['Hard'] > len(sequences) * 0.5:
            recommendations.append({
                'type': 'difficulty',
                'priority': 'Medium',
                'message': 'Too many hard questions - may discourage students',
                'action': 'Add more easy/medium difficulty questions for scaffolding'
            })

        return recommendations

    # Single topic analysis methods

    def _get_topic_statistics(self, sequences: pd.DataFrame, 
                             performance: pd.DataFrame) -> Dict:
        """Get basic statistics for a topic"""
        return {
            'total_attempts': len(sequences),
            'unique_students': sequences['student_id'].nunique(),
            'success_rate': sequences['is_correct'].mean(),
            'average_score': sequences['score'].mean(),
            'std_score': sequences['score'].std(),
            'avg_time_spent': sequences['time_spent_seconds'].mean(),
            'difficulty_rating': self._classify_difficulty(sequences['is_correct'].mean())
        }

    def _analyze_student_performance(self, performance: pd.DataFrame) -> Dict:
        """Analyze how students perform on this topic"""
        if len(performance) == 0:
            return {}

        # Performance distribution
        performance_dist = {
            'mastered': len(performance[performance['accuracy'] >= 0.85]),
            'proficient': len(performance[(performance['accuracy'] >= 0.7) & (performance['accuracy'] < 0.85)]),
            'developing': len(performance[(performance['accuracy'] >= 0.5) & (performance['accuracy'] < 0.7)]),
            'struggling': len(performance[performance['accuracy'] < 0.5])
        }

        return {
            'total_students': len(performance),
            'performance_distribution': performance_dist,
            'avg_attempts_per_student': performance['total_attempts'].mean(),
            'best_student_accuracy': performance['accuracy'].max(),
            'worst_student_accuracy': performance['accuracy'].min()
        }

    def _analyze_topic_difficulty(self, sequences: pd.DataFrame) -> Dict:
        """Analyze difficulty breakdown for topic"""
        difficulty_breakdown = sequences.groupby('difficulty').agg({
            'is_correct': 'mean',
            'student_id': 'count'
        }).reset_index()

        return difficulty_breakdown.to_dict('records')

    def _analyze_bloom_distribution(self, sequences: pd.DataFrame) -> Dict:
        """Analyze Bloom's taxonomy distribution"""
        bloom_stats = sequences.groupby('bloom_level').agg({
            'is_correct': 'mean',
            'student_id': 'count'
        }).reset_index()

        return bloom_stats.to_dict('records')

    def _analyze_time_patterns(self, sequences: pd.DataFrame) -> Dict:
        """Analyze time spent patterns"""
        return {
            'avg_time': sequences['time_spent_seconds'].mean(),
            'median_time': sequences['time_spent_seconds'].median(),
            'min_time': sequences['time_spent_seconds'].min(),
            'max_time': sequences['time_spent_seconds'].max(),
            'time_vs_accuracy_correlation': sequences['time_spent_seconds'].corr(sequences['is_correct'])
        }

    def _analyze_mastery_distribution(self, performance: pd.DataFrame) -> Dict:
        """Analyze mastery level distribution"""
        if len(performance) == 0:
            return {}

        mastery_counts = {
            'Mastered (≥85%)': len(performance[performance['accuracy'] >= 0.85]),
            'Proficient (70-85%)': len(performance[(performance['accuracy'] >= 0.7) & (performance['accuracy'] < 0.85)]),
            'Developing (50-70%)': len(performance[(performance['accuracy'] >= 0.5) & (performance['accuracy'] < 0.7)]),
            'Novice (<50%)': len(performance[performance['accuracy'] < 0.5])
        }

        total = sum(mastery_counts.values())
        mastery_percentages = {k: v/total*100 for k, v in mastery_counts.items()}

        return {
            'counts': mastery_counts,
            'percentages': mastery_percentages
        }

    def _identify_success_factors(self, sequences: pd.DataFrame) -> Dict:
        """Identify factors correlated with success"""
        # Time correlation
        time_corr = sequences['time_spent_seconds'].corr(sequences['is_correct'])

        # Difficulty correlation
        sequences['difficulty_numeric'] = sequences['difficulty'].map({
            'Easy': 1, 'Medium': 2, 'Hard': 3, 'Advanced': 4
        })
        difficulty_corr = sequences['difficulty_numeric'].corr(sequences['is_correct'])

        return {
            'time_correlation': time_corr,
            'difficulty_correlation': difficulty_corr,
            'optimal_time_range': self._find_optimal_time_range(sequences)
        }

    def _find_optimal_time_range(self, sequences: pd.DataFrame) -> Tuple[float, float]:
        """Find time range with highest success rate"""
        # Group by time buckets
        sequences['time_bucket'] = pd.cut(sequences['time_spent_seconds'], bins=5)
        bucket_success = sequences.groupby('time_bucket')['is_correct'].mean()

        if len(bucket_success) > 0:
            optimal_bucket = bucket_success.idxmax()
            return (optimal_bucket.left, optimal_bucket.right)
        return (0, 0)

    # Helper methods

    def _classify_difficulty(self, success_rate: float) -> str:
        """Classify difficulty based on success rate"""
        for level, (min_rate, max_rate) in self.difficulty_levels.items():
            if min_rate <= success_rate < max_rate:
                return level
        return 'Moderate'

    def _get_empty_topic_analytics(self, topic: str, subject: str) -> Dict:
        """Return empty analytics for topics with no data"""
        return {
            'topic': topic,
            'subject': subject,
            'error': 'No data available for this topic'
        }


# Example usage
if __name__ == "__main__":
    from utils.data_loader import DataLoader

    loader = DataLoader()

    try:
        sequences = loader.load_learning_sequences()
        performance = loader.load_performance_history()

        analytics = TopicAnalytics()

        print("\n📊 Analyzing All Topics")
        print("="*60)

        results = analytics.analyze_all_topics(sequences, performance)

        # Overview
        print("\n📈 Overview:")
        overview = results['overview']
        print(f"   Total Topics: {overview['total_topics']}")
        print(f"   Total Students: {overview['total_students']}")
        print(f"   Overall Success Rate: {overview['overall_success_rate']:.1%}")
        print(f"   Average Score: {overview['average_score']:.1f}")

        # Easiest topics
        print("\n✅ Easiest Topics (Top 5):")
        for i, topic in enumerate(results['topic_rankings']['easiest_topics'][:5], 1):
            print(f"   {i}. {topic['topic']} ({topic['subject']})")
            print(f"      Success Rate: {topic['avg_accuracy']:.1%}, Students: {topic['num_students']}")

        # Hardest topics
        print("\n🎯 Most Challenging Topics (Top 5):")
        for i, topic in enumerate(results['topic_rankings']['hardest_topics'][:5], 1):
            print(f"   {i}. {topic['topic']} ({topic['subject']})")
            print(f"      Success Rate: {topic['avg_accuracy']:.1%}, Students: {topic['num_students']}")

        # Subject comparison
        print("\n📚 Subject Comparison:")
        for subject in results['subject_comparison']:
            print(f"   {subject['subject']}:")
            print(f"      Success Rate: {subject['success_rate']:.1%}")
            print(f"      Avg Score: {subject['avg_score']:.1f}")
            print(f"      Topics: {subject['num_topics']}")

        # Recommendations
        print("\n💡 Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. [{rec['priority']}] {rec['message']}")
            print(f"      Action: {rec['action']}")

        # Analyze specific topic
        print("\n\n🔍 Analyzing Specific Topic: Calculus (Mathematics)")
        print("="*60)

        topic_result = analytics.analyze_topic('Calculus', 'Mathematics', sequences, performance)

        if 'error' not in topic_result:
            stats = topic_result['statistics']
            print(f"\n   Total Attempts: {stats['total_attempts']}")
            print(f"   Unique Students: {stats['unique_students']}")
            print(f"   Success Rate: {stats['success_rate']:.1%}")
            print(f"   Difficulty: {stats['difficulty_rating']}")

            if 'student_performance' in topic_result:
                perf = topic_result['student_performance']
                print(f"\n   Student Performance Distribution:")
                dist = perf['performance_distribution']
                print(f"      Mastered: {dist['mastered']}")
                print(f"      Proficient: {dist['proficient']}")
                print(f"      Developing: {dist['developing']}")
                print(f"      Struggling: {dist['struggling']}")

        print("\n="*60)
        print("✅ Topic analytics complete!")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
