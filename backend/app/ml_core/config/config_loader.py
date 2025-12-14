"""
Configuration Loader Utility
Loads and validates YAML configuration files
"""

import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """Load and access configuration from YAML files"""

    def __init__(self, config_path: str = 'config/model_config.yaml'):
        """
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key_path: Dot-separated path (e.g., 'dkt.model.hidden_dim')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            config = ConfigLoader()
            hidden_dim = config.get('dkt.model.hidden_dim')  # Returns 128
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_dkt_config(self) -> Dict[str, Any]:
        """Get DKT model configuration"""
        return self.config.get('dkt', {})

    def get_predictor_config(self) -> Dict[str, Any]:
        """Get performance predictor configuration"""
        return self.config.get('performance_predictor', {})

    def get_feature_config(self) -> Dict[str, Any]:
        """Get feature engineering configuration"""
        return self.config.get('feature_engineering', {})

    def get_analytics_config(self) -> Dict[str, Any]:
        """Get analytics configuration"""
        return self.config.get('analytics', {})

    def get_data_paths(self) -> Dict[str, str]:
        """Get all data file paths"""
        return self.config.get('data_paths', {})


# Example usage
if __name__ == "__main__":
    # Load configuration
    config = ConfigLoader('config/model_config.yaml')

    print("📋 Configuration Loaded!")
    print("="*60)

    # Access DKT settings
    print("\n🧠 DKT Model Settings:")
    print(f"   Hidden Dim: {config.get('dkt.model.hidden_dim')}")
    print(f"   Num Layers: {config.get('dkt.model.num_layers')}")
    print(f"   Learning Rate: {config.get('dkt.training.learning_rate')}")
    print(f"   Early Stopping: {config.get('dkt.training.early_stopping_patience')}")

    # Access Performance Predictor settings
    print("\n🌲 Performance Predictor Settings:")
    print(f"   N Estimators: {config.get('performance_predictor.model.n_estimators')}")
    print(f"   Max Depth: {config.get('performance_predictor.model.max_depth')}")
    print(f"   Pass Threshold: {config.get('performance_predictor.features.pass_threshold')}")

    # Access Feature Engineering settings
    print("\n🔧 Feature Engineering Settings:")
    print(f"   Recent Window: {config.get('feature_engineering.student_features.recent_window_ratio')}")
    print(f"   Rolling Window: {config.get('feature_engineering.student_features.rolling_window_size')}")

    # Access Data Paths
    print("\n📁 Data Paths:")
    paths = config.get_data_paths()
    for key, path in list(paths.items())[:5]:
        print(f"   {key}: {path}")

    # Access Curriculum
    print("\n📚 Curriculum:")
    subjects = config.get('curriculum.subjects', {})
    for subject in subjects:
        num_topics = len(subjects[subject])
        print(f"   {subject}: {num_topics} topics")

    print("\n✅ Configuration access successful!")
