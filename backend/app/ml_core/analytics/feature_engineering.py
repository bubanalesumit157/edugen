"""
Feature Engineering Pipeline
Extracts and transforms features from raw student data for ML models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """
    Feature engineering for student performance analytics
    Creates features from learning sequences and performance history
    """

    def __init__(self):
        self.feature_stats = {}
        self.is_fitted = False

    def extract_student_features(self, learning_sequences: pd.DataFrame, student_id: str) -> Dict:
        """
        Extract comprehensive features for a single student

        Args:
            learning_sequences: DataFrame with student learning history
            student_id: Student identifier

        Returns:
            Dict with extracted features
        """
        # Filter student data
        student_data = learning_sequences[learning_sequences['student_id'] == student_id].copy()

        if len(student_data) == 0:
            return self._get_default_features()

        # Sort by timestamp
        student_data = student_data.sort_values('timestamp')

        features = {}

        # 1. Basic performance metrics
        features['total_attempts'] = len(student_data)
        features['accuracy'] = student_data['is_correct'].mean()
        features['avg_score'] = student_data['score'].mean()
        features['std_score'] = student_data['score'].std() if len(student_data) > 1 else 0

        # 2. Recent performance (last 30% of attempts)
        recent_cutoff = int(len(student_data) * 0.7)
        recent_data = student_data.iloc[recent_cutoff:]

        features['recent_attempts'] = len(recent_data)
        features['recent_accuracy'] = recent_data['is_correct'].mean()
        features['recent_avg_score'] = recent_data['score'].mean()

        # 3. Learning progression
        if len(student_data) >= 2:
            first_half = student_data.iloc[:len(student_data)//2]
            second_half = student_data.iloc[len(student_data)//2:]

            features['learning_velocity'] = (
                second_half['is_correct'].mean() - first_half['is_correct'].mean()
            )
            features['score_improvement'] = (
                second_half['score'].mean() - first_half['score'].mean()
            )
        else:
            features['learning_velocity'] = 0.0
            features['score_improvement'] = 0.0

        # 4. Time-based features
        features['avg_time_spent'] = student_data['time_spent_seconds'].mean()
        features['total_time_spent'] = student_data['time_spent_seconds'].sum()
        features['std_time_spent'] = student_data['time_spent_seconds'].std() if len(student_data) > 1 else 0

        # 5. Difficulty progression
        features['avg_difficulty_level'] = self._difficulty_to_numeric(student_data['difficulty']).mean()
        features['max_difficulty_attempted'] = self._difficulty_to_numeric(student_data['difficulty']).max()

        # 6. Topic coverage
        features['unique_topics'] = student_data['topic'].nunique()
        features['unique_subjects'] = student_data['subject'].nunique()

        # 7. Bloom's taxonomy distribution
        bloom_dist = student_data['bloom_level'].value_counts(normalize=True).to_dict()
        for level in ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']:
            features[f'bloom_{level.lower()}_ratio'] = bloom_dist.get(level, 0.0)

        # 8. Consistency metrics
        features['consistency_score'] = 1 - student_data['is_correct'].std() if len(student_data) > 1 else 0.5

        # 9. Engagement patterns
        if 'timestamp' in student_data.columns:
            features['days_active'] = self._calculate_active_days(student_data['timestamp'])
            features['avg_attempts_per_day'] = features['total_attempts'] / max(features['days_active'], 1)
        else:
            features['days_active'] = 1
            features['avg_attempts_per_day'] = features['total_attempts']

        # 10. Completion rate (proxy for engagement)
        features['completion_rate'] = min(features['total_attempts'] / 20, 1.0)  # Normalized to expected 20 attempts

        return features

    def extract_topic_features(self, learning_sequences: pd.DataFrame, 
                              student_id: str, topic: str) -> Dict:
        """
        Extract features for a specific topic for a student

        Args:
            learning_sequences: DataFrame with learning history
            student_id: Student identifier
            topic: Topic name

        Returns:
            Dict with topic-specific features
        """
        # Filter for student and topic
        topic_data = learning_sequences[
            (learning_sequences['student_id'] == student_id) &
            (learning_sequences['topic'] == topic)
        ].copy()

        if len(topic_data) == 0:
            return self._get_default_topic_features()

        features = {}

        # Topic performance
        features['topic_attempts'] = len(topic_data)
        features['topic_accuracy'] = topic_data['is_correct'].mean()
        features['topic_avg_score'] = topic_data['score'].mean()

        # Recent topic performance
        if len(topic_data) >= 3:
            recent_topic = topic_data.tail(min(5, len(topic_data)))
            features['topic_recent_accuracy'] = recent_topic['is_correct'].mean()
            features['topic_trend'] = recent_topic['is_correct'].mean() - topic_data['is_correct'].mean()
        else:
            features['topic_recent_accuracy'] = features['topic_accuracy']
            features['topic_trend'] = 0.0

        # Topic difficulty
        features['topic_avg_difficulty'] = self._difficulty_to_numeric(topic_data['difficulty']).mean()

        # Topic mastery level
        features['topic_mastery_level'] = self._calculate_mastery_level(features['topic_accuracy'])

        return features

    def create_feature_matrix(self, learning_sequences: pd.DataFrame, 
                             student_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create feature matrix for multiple students

        Args:
            learning_sequences: DataFrame with all learning sequences
            student_ids: List of student IDs (if None, use all)

        Returns:
            DataFrame with feature matrix
        """
        if student_ids is None:
            student_ids = learning_sequences['student_id'].unique()

        print(f"🔧 Creating feature matrix for {len(student_ids)} students...")

        feature_list = []

        for student_id in student_ids:
            features = self.extract_student_features(learning_sequences, student_id)
            features['student_id'] = student_id
            feature_list.append(features)

        feature_df = pd.DataFrame(feature_list)

        print(f"   ✅ Created {len(feature_df)} × {len(feature_df.columns)} feature matrix")

        # Store feature statistics
        self.feature_stats = {
            'mean': feature_df.select_dtypes(include=[np.number]).mean().to_dict(),
            'std': feature_df.select_dtypes(include=[np.number]).std().to_dict(),
            'min': feature_df.select_dtypes(include=[np.number]).min().to_dict(),
            'max': feature_df.select_dtypes(include=[np.number]).max().to_dict()
        }

        self.is_fitted = True

        return feature_df

    def create_temporal_features(self, learning_sequences: pd.DataFrame, 
                                student_id: str, window_size: int = 5) -> pd.DataFrame:
        """
        Create temporal features for time-series models (e.g., DKT)

        Args:
            learning_sequences: DataFrame with learning history
            student_id: Student identifier
            window_size: Number of past interactions to consider

        Returns:
            DataFrame with temporal features
        """
        student_data = learning_sequences[
            learning_sequences['student_id'] == student_id
        ].sort_values('timestamp').copy()

        if len(student_data) == 0:
            return pd.DataFrame()

        # Rolling window features
        student_data['rolling_accuracy'] = (
            student_data['is_correct']
            .rolling(window=window_size, min_periods=1)
            .mean()
        )

        student_data['rolling_avg_score'] = (
            student_data['score']
            .rolling(window=window_size, min_periods=1)
            .mean()
        )

        student_data['rolling_avg_time'] = (
            student_data['time_spent_seconds']
            .rolling(window=window_size, min_periods=1)
            .mean()
        )

        # Momentum features (trend)
        student_data['accuracy_momentum'] = (
            student_data['rolling_accuracy'].diff().fillna(0)
        )

        # Cumulative features
        student_data['cumulative_attempts'] = range(1, len(student_data) + 1)
        student_data['cumulative_correct'] = student_data['is_correct'].cumsum()
        student_data['cumulative_accuracy'] = (
            student_data['cumulative_correct'] / student_data['cumulative_attempts']
        )

        return student_data

    def _difficulty_to_numeric(self, difficulty_series: pd.Series) -> pd.Series:
        """Convert difficulty labels to numeric values"""
        difficulty_map = {
            'Easy': 1,
            'Medium': 2,
            'Hard': 3,
            'Advanced': 4
        }
        return difficulty_series.map(difficulty_map).fillna(2)

    def _calculate_mastery_level(self, accuracy: float) -> str:
        """Convert accuracy to mastery level"""
        if accuracy >= 0.85:
            return 'Mastered'
        elif accuracy >= 0.70:
            return 'Proficient'
        elif accuracy >= 0.50:
            return 'Developing'
        else:
            return 'Novice'

    def _calculate_active_days(self, timestamps: pd.Series) -> int:
        """Calculate number of active days from timestamps"""
        try:
            timestamps = pd.to_datetime(timestamps)
            unique_dates = timestamps.dt.date.nunique()
            return max(unique_dates, 1)
        except:
            return 1

    def _get_default_features(self) -> Dict:
        """Return default features for students with no data"""
        return {
            'total_attempts': 0,
            'accuracy': 0.0,
            'avg_score': 0.0,
            'std_score': 0.0,
            'recent_attempts': 0,
            'recent_accuracy': 0.0,
            'recent_avg_score': 0.0,
            'learning_velocity': 0.0,
            'score_improvement': 0.0,
            'avg_time_spent': 0.0,
            'total_time_spent': 0.0,
            'std_time_spent': 0.0,
            'avg_difficulty_level': 0.0,
            'max_difficulty_attempted': 0.0,
            'unique_topics': 0,
            'unique_subjects': 0,
            'consistency_score': 0.5,
            'days_active': 1,
            'avg_attempts_per_day': 0.0,
            'completion_rate': 0.0
        }

    def _get_default_topic_features(self) -> Dict:
        """Return default features for topics with no data"""
        return {
            'topic_attempts': 0,
            'topic_accuracy': 0.0,
            'topic_avg_score': 0.0,
            'topic_recent_accuracy': 0.0,
            'topic_trend': 0.0,
            'topic_avg_difficulty': 0.0,
            'topic_mastery_level': 'Novice'
        }

    def get_feature_summary(self) -> pd.DataFrame:
        """Get summary statistics of features"""
        if not self.is_fitted:
            raise ValueError("FeatureEngineer not fitted. Call create_feature_matrix() first.")

        summary_df = pd.DataFrame(self.feature_stats).T
        return summary_df


# Example usage
if __name__ == "__main__":
    import os

    # Load data
    data_path = 'data/synthetic/learning_sequences.csv'

    if os.path.exists(data_path):
        print("📚 Loading learning sequences...")
        sequences_df = pd.read_csv(data_path)
        print(f"   Loaded {len(sequences_df)} learning interactions")

        # Initialize feature engineer
        fe = FeatureEngineer()

        # Test single student features
        print("\n🔧 Extracting features for single student...")
        student_id = sequences_df['student_id'].iloc[0]
        student_features = fe.extract_student_features(sequences_df, student_id)

        print(f"\nFeatures for {student_id}:")
        for key, value in list(student_features.items())[:10]:
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        print(f"   ... and {len(student_features) - 10} more features")

        # Create feature matrix for all students
        print("\n🔧 Creating feature matrix for all students...")
        feature_matrix = fe.create_feature_matrix(sequences_df)

        print(f"\n📊 Feature Matrix Shape: {feature_matrix.shape}")
        print(f"\nFeature Columns:")
        for i, col in enumerate(feature_matrix.columns[:15], 1):
            print(f"   {i}. {col}")
        if len(feature_matrix.columns) > 15:
            print(f"   ... and {len(feature_matrix.columns) - 15} more columns")

        # Show sample statistics
        print(f"\n📈 Sample Statistics:")
        print(feature_matrix[['accuracy', 'recent_accuracy', 'learning_velocity', 
                             'total_attempts', 'avg_time_spent']].describe())

        # Test topic-specific features
        print("\n🔧 Extracting topic-specific features...")
        topic = sequences_df['topic'].iloc[0]
        topic_features = fe.extract_topic_features(sequences_df, student_id, topic)

        print(f"\nTopic features for '{topic}':")
        for key, value in topic_features.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")

        print("\n✅ Feature engineering complete!")

    else:
        print(f"❌ Data file not found: {data_path}")
        print("   Run generate_data.py first!")
