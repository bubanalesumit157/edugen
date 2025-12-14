"""
Data Loading and Validation Utilities
Handles data loading, validation, and preprocessing for ML models
"""

import pandas as pd
import numpy as np
import os
from typing import Tuple, List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class DataLoader:
    """
    Centralized data loading and validation for ML analytics module
    """

    def __init__(self, data_dir: str = 'data/synthetic'):
        """
        Args:
            data_dir: Base directory for data files
        """
        self.data_dir = data_dir
        self.loaded_data = {}

    def load_student_records(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load student records dataset

        Args:
            file_path: Custom file path (if None, uses default)

        Returns:
            DataFrame with student records
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'student_records.csv')

        print(f"📚 Loading student records from {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Student records file not found: {file_path}")

        df = pd.read_csv(file_path)

        # Validate required columns (FIXED to match generated data)
        required_cols = ['student_id', 'name', 'grade']
        self._validate_columns(df, required_cols, 'student_records')

        print(f"   ✅ Loaded {len(df)} student records")

        self.loaded_data['student_records'] = df
        return df

    def load_learning_sequences(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load learning sequences dataset

        Args:
            file_path: Custom file path (if None, uses default)

        Returns:
            DataFrame with learning sequences
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'learning_sequences.csv')

        print(f"📚 Loading learning sequences from {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Learning sequences file not found: {file_path}")

        df = pd.read_csv(file_path)

        # Validate required columns
        required_cols = ['student_id', 'subject', 'topic', 'is_correct', 'score']
        self._validate_columns(df, required_cols, 'learning_sequences')

        # Parse timestamp if exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        print(f"   ✅ Loaded {len(df)} learning interactions")

        self.loaded_data['learning_sequences'] = df
        return df

    def load_performance_history(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load performance history dataset

        Args:
            file_path: Custom file path (if None, uses default)

        Returns:
            DataFrame with performance history
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'performance_history.csv')

        print(f"📚 Loading performance history from {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Performance history file not found: {file_path}")

        df = pd.read_csv(file_path)

        # Validate required columns
        required_cols = ['student_id', 'subject', 'topic', 'total_attempts', 'accuracy']
        self._validate_columns(df, required_cols, 'performance_history')

        print(f"   ✅ Loaded {len(df)} performance records")

        self.loaded_data['performance_history'] = df
        return df

    def load_knowledge_states(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load knowledge states dataset (for DKT)

        Args:
            file_path: Custom file path (if None, uses default)

        Returns:
            DataFrame with knowledge states
        """
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'knowledge_states.csv')

        print(f"📚 Loading knowledge states from {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Knowledge states file not found: {file_path}")

        df = pd.read_csv(file_path)

        # Validate required columns
        required_cols = ['student_id', 'skill_name']
        self._validate_columns(df, required_cols, 'knowledge_states')

        print(f"   ✅ Loaded {len(df)} knowledge state sequences")

        self.loaded_data['knowledge_states'] = df
        return df

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all datasets at once

        Returns:
            Dict mapping dataset names to DataFrames
        """
        print("📚 Loading all datasets...")
        print("="*60)

        try:
            self.load_student_records()
            self.load_learning_sequences()
            self.load_performance_history()
            self.load_knowledge_states()

            print("="*60)
            print("✅ All datasets loaded successfully!")

            return self.loaded_data

        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            raise

    def get_student_data(self, student_id: str) -> Dict[str, pd.DataFrame]:
        """
        Get all data for a specific student

        Args:
            student_id: Student identifier

        Returns:
            Dict with student's data from all datasets
        """
        student_data = {}

        if 'student_records' in self.loaded_data:
            student_data['records'] = self.loaded_data['student_records'][
                self.loaded_data['student_records']['student_id'] == student_id
            ]

        if 'learning_sequences' in self.loaded_data:
            student_data['sequences'] = self.loaded_data['learning_sequences'][
                self.loaded_data['learning_sequences']['student_id'] == student_id
            ]

        if 'performance_history' in self.loaded_data:
            student_data['performance'] = self.loaded_data['performance_history'][
                self.loaded_data['performance_history']['student_id'] == student_id
            ]

        return student_data

    def split_data(self, df: pd.DataFrame, 
                  test_size: float = 0.2, 
                  stratify_col: Optional[str] = None,
                  random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets

        Args:
            df: DataFrame to split
            test_size: Fraction for test set
            stratify_col: Column to stratify split (e.g., for balanced classes)
            random_state: Random seed

        Returns:
            Tuple of (train_df, test_df)
        """
        from sklearn.model_selection import train_test_split

        if stratify_col and stratify_col in df.columns:
            stratify = df[stratify_col]
        else:
            stratify = None

        train_df, test_df = train_test_split(
            df, 
            test_size=test_size, 
            random_state=random_state,
            stratify=stratify
        )

        return train_df, test_df

    def create_batches(self, df: pd.DataFrame, batch_size: int = 32) -> List[pd.DataFrame]:
        """
        Create batches from DataFrame for batch processing

        Args:
            df: DataFrame to batch
            batch_size: Number of rows per batch

        Returns:
            List of DataFrame batches
        """
        batches = []
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            batches.append(batch)

        return batches

    def filter_by_subject(self, df: pd.DataFrame, subject: str) -> pd.DataFrame:
        """Filter data by subject"""
        if 'subject' not in df.columns:
            raise ValueError("DataFrame does not have 'subject' column")

        return df[df['subject'] == subject].copy()

    def filter_by_topic(self, df: pd.DataFrame, topic: str) -> pd.DataFrame:
        """Filter data by topic"""
        if 'topic' not in df.columns:
            raise ValueError("DataFrame does not have 'topic' column")

        return df[df['topic'] == topic].copy()

    def filter_by_date_range(self, df: pd.DataFrame, 
                            start_date: str, 
                            end_date: str,
                            date_col: str = 'timestamp') -> pd.DataFrame:
        """
        Filter data by date range

        Args:
            df: DataFrame with date column
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            date_col: Name of date column

        Returns:
            Filtered DataFrame
        """
        if date_col not in df.columns:
            raise ValueError(f"DataFrame does not have '{date_col}' column")

        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
        return df[mask]

    def get_data_summary(self) -> Dict[str, Dict]:
        """
        Get summary statistics for all loaded datasets

        Returns:
            Dict with summary for each dataset
        """
        summary = {}

        for name, df in self.loaded_data.items():
            summary[name] = {
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'columns': list(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
            }

            if 'student_id' in df.columns:
                summary[name]['num_students'] = df['student_id'].nunique()

            if 'subject' in df.columns:
                summary[name]['num_subjects'] = df['subject'].nunique()

            if 'topic' in df.columns:
                summary[name]['num_topics'] = df['topic'].nunique()

        return summary

    def validate_data_quality(self, df: pd.DataFrame, dataset_name: str = 'dataset') -> Dict:
        """
        Validate data quality and return issues

        Args:
            df: DataFrame to validate
            dataset_name: Name for reporting

        Returns:
            Dict with validation results
        """
        issues = {
            'missing_values': {},
            'duplicate_rows': 0,
            'invalid_values': {},
            'warnings': []
        }

        # Check for missing values
        missing = df.isnull().sum()
        issues['missing_values'] = {col: int(count) for col, count in missing.items() if count > 0}

        # Check for duplicate rows
        issues['duplicate_rows'] = df.duplicated().sum()

        # Check for invalid numeric values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                continue

            if col in ['accuracy', 'completion_rate']:
                # Should be between 0 and 1
                invalid = ((df[col] < 0) | (df[col] > 1)).sum()
                if invalid > 0:
                    issues['invalid_values'][col] = f"{invalid} values outside [0, 1]"

            elif col == 'score':
                # Should be between 0 and 100
                invalid = ((df[col] < 0) | (df[col] > 100)).sum()
                if invalid > 0:
                    issues['invalid_values'][col] = f"{invalid} values outside [0, 100]"

        # Generate warnings
        if len(issues['missing_values']) > 0:
            issues['warnings'].append(f"Found missing values in {len(issues['missing_values'])} columns")

        if issues['duplicate_rows'] > 0:
            issues['warnings'].append(f"Found {issues['duplicate_rows']} duplicate rows")

        if len(issues['invalid_values']) > 0:
            issues['warnings'].append(f"Found invalid values in {len(issues['invalid_values'])} columns")

        return issues

    def _validate_columns(self, df: pd.DataFrame, required_cols: List[str], dataset_name: str):
        """Validate that required columns exist"""
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(
                f"{dataset_name} is missing required columns: {missing_cols}\n"
                f"Available columns: {list(df.columns)}"
            )


# Example usage
if __name__ == "__main__":
    # Initialize data loader
    loader = DataLoader(data_dir='data/synthetic')

    # Load all data
    try:
        all_data = loader.load_all_data()

        # Get data summary
        print("\n📊 Data Summary:")
        print("="*60)
        summary = loader.get_data_summary()

        for dataset_name, stats in summary.items():
            print(f"\n{dataset_name}:")
            print(f"   Rows: {stats['num_rows']:,}")
            print(f"   Columns: {stats['num_columns']}")
            if 'num_students' in stats:
                print(f"   Students: {stats['num_students']}")
            if 'num_topics' in stats:
                print(f"   Topics: {stats['num_topics']}")
            print(f"   Memory: {stats['memory_usage_mb']:.2f} MB")

        # Test student data retrieval
        print("\n🔍 Testing Student Data Retrieval:")
        print("="*60)
        student_id = all_data['learning_sequences']['student_id'].iloc[0]
        student_data = loader.get_student_data(student_id)

        print(f"\nData for {student_id}:")
        for key, df in student_data.items():
            print(f"   {key}: {len(df)} records")

        # Test data splitting
        print("\n✂️ Testing Data Split:")
        print("="*60)
        train_df, test_df = loader.split_data(all_data['performance_history'], test_size=0.2)
        print(f"   Train set: {len(train_df)} records")
        print(f"   Test set: {len(test_df)} records")

        # Validate data quality
        print("\n✅ Data Quality Check:")
        print("="*60)
        issues = loader.validate_data_quality(all_data['learning_sequences'], 'learning_sequences')

        if len(issues['warnings']) == 0:
            print("   ✅ No data quality issues found!")
        else:
            print("   ⚠️  Issues found:")
            for warning in issues['warnings']:
                print(f"      - {warning}")

        print("\n="*60)
        print("✅ Data loader test complete!")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("   Please run generate_data.py first!")
