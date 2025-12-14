"""
Difficulty Adapter Module - FIXED VERSION
Manages difficulty progression based on Zone of Proximal Development (ZPD)
Provides optimal challenge levels for student engagement and learning
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


class DifficultyAdapter:
    """
    Manages difficulty progression using Zone of Proximal Development principles
    Ensures optimal challenge level for maximum learning efficiency
    """

    def __init__(self):
        # Zone of Proximal Development thresholds
        self.zpd_thresholds = {
            'too_easy': 0.90,      # >90% accuracy = too easy
            'optimal_high': 0.85,  # 70-85% = optimal challenge zone
            'optimal_low': 0.70,
            'too_hard': 0.50       # <50% accuracy = too hard
        }

        # Difficulty levels with numeric values
        self.difficulty_levels = {
            'Easy': 1,
            'Medium': 2,
            'Hard': 3,
            'Advanced': 4
        }

        self.reverse_difficulty = {v: k for k, v in self.difficulty_levels.items()}

        # Progression rules
        self.progression_rules = {
            'min_attempts_before_increase': 5,
            'min_attempts_before_decrease': 3,
            'consecutive_success_threshold': 3,
            'consecutive_failure_threshold': 3,
            'velocity_threshold': 0.15
        }

    def recommend_difficulty(self, performance_history: List[Dict],
                           current_difficulty: str = 'Medium') -> Dict:
        """
        Recommend difficulty level based on recent performance

        Args:
            performance_history: List of recent attempts with 'is_correct' and 'difficulty'
            current_difficulty: Current difficulty level

        Returns:
            Dict with difficulty recommendation and reasoning
        """
        if len(performance_history) < self.progression_rules['min_attempts_before_increase']:
            return {
                'recommended_difficulty': current_difficulty,
                'confidence': 'low',
                'reason': 'Insufficient data for adaptation',
                'zone': 'unknown'
            }

        # Calculate recent accuracy
        recent_accuracy = self._calculate_recent_accuracy(performance_history)

        # Determine ZPD zone
        zone = self._determine_zpd_zone(recent_accuracy)

        # Calculate learning velocity
        velocity = self._calculate_learning_velocity(performance_history)

        # Get zone-based recommendation
        zone_recommendation = self._get_zone_recommendation(zone, current_difficulty)

        # Apply velocity adjustment
        final_recommendation, reason = self._apply_velocity_adjustment(
            zone_recommendation, current_difficulty, zone, 
            recent_accuracy, velocity
        )

        return {
            'recommended_difficulty': final_recommendation,
            'current_difficulty': current_difficulty,
            'recent_accuracy': recent_accuracy,
            'learning_velocity': velocity,
            'zone': zone,
            'reason': reason,
            'confidence': self._calculate_confidence(performance_history)
        }

    def _get_zone_recommendation(self, zone: str, current: str) -> str:
        """Get recommendation based on ZPD zone"""
        if zone == 'too_easy':
            return self._increase_difficulty(current)
        elif zone == 'too_hard':
            return self._decrease_difficulty(current)
        else:
            return current

    def _apply_velocity_adjustment(self, zone_rec: str, current: str,
                                  zone: str, accuracy: float, 
                                  velocity: float) -> Tuple[str, str]:
        """Apply velocity-based adjustment and generate clear reasoning"""

        # Build reason components
        zone_reason = self._get_zone_reason(zone, accuracy)

        # Check velocity
        if abs(velocity) > self.progression_rules['velocity_threshold']:
            if velocity > 0:
                # Rapid improvement
                velocity_adjustment = self._increase_difficulty(zone_rec)
                velocity_reason = f"rapid improvement detected ({velocity:+.1%})"

                if zone == 'too_hard' and velocity_adjustment == current:
                    # Special case: struggling but improving
                    reason = f"{zone_reason}, but {velocity_reason} - maintaining current level to consolidate gains"
                elif velocity_adjustment != zone_rec:
                    reason = f"{zone_reason}; {velocity_reason} - advancing further"
                else:
                    reason = f"{zone_reason}; {velocity_reason}"

                return velocity_adjustment, reason

            else:
                # Rapid decline
                velocity_adjustment = self._decrease_difficulty(zone_rec)
                velocity_reason = f"performance declining ({velocity:+.1%})"

                if zone == 'too_easy' and velocity_adjustment == current:
                    # Special case: easy but declining
                    reason = f"{zone_reason}, but {velocity_reason} - maintaining current level for stability"
                elif velocity_adjustment != zone_rec:
                    reason = f"{zone_reason}; {velocity_reason} - providing additional support"
                else:
                    reason = f"{zone_reason}; {velocity_reason}"

                return velocity_adjustment, reason
        else:
            # No significant velocity change
            return zone_rec, zone_reason

    def _get_zone_reason(self, zone: str, accuracy: float) -> str:
        """Get human-readable reason for zone"""
        if zone == 'too_easy':
            return f"Accuracy {accuracy:.1%} indicates mastery - student ready for increased challenge"
        elif zone == 'too_hard':
            return f"Accuracy {accuracy:.1%} indicates struggle - student needs support"
        else:
            return f"Accuracy {accuracy:.1%} is in optimal learning zone (70-85%)"

    def get_difficulty_distribution(self, student_performance: Dict,
                                   target_difficulty: str = 'Medium') -> Dict:
        """
        Get optimal difficulty distribution for an assignment

        Args:
            student_performance: Dict with performance metrics
            target_difficulty: Primary difficulty level

        Returns:
            Dict with difficulty distribution percentages
        """
        recent_accuracy = student_performance.get('recent_accuracy', 0.7)
        learning_velocity = student_performance.get('learning_velocity', 0.0)

        # Base distribution on target difficulty
        if target_difficulty == 'Easy':
            distribution = {'Easy': 0.7, 'Medium': 0.3, 'Hard': 0.0, 'Advanced': 0.0}
        elif target_difficulty == 'Medium':
            distribution = {'Easy': 0.2, 'Medium': 0.6, 'Hard': 0.2, 'Advanced': 0.0}
        elif target_difficulty == 'Hard':
            distribution = {'Easy': 0.1, 'Medium': 0.3, 'Hard': 0.5, 'Advanced': 0.1}
        else:  # Advanced
            distribution = {'Easy': 0.0, 'Medium': 0.2, 'Hard': 0.4, 'Advanced': 0.4}

        # Adjust based on ZPD zone
        zone = self._determine_zpd_zone(recent_accuracy)

        if zone == 'too_easy':
            distribution = self._shift_harder(distribution)
        elif zone == 'too_hard':
            distribution = self._shift_easier(distribution)

        # Adjust based on learning velocity
        if learning_velocity > 0.15:
            distribution = self._shift_harder(distribution, factor=0.1)
        elif learning_velocity < -0.15:
            distribution = self._shift_easier(distribution, factor=0.1)

        # Ensure distribution sums to 1.0
        distribution = self._normalize_distribution(distribution)

        return distribution

    def calculate_zpd_score(self, student_data: pd.DataFrame) -> float:
        """
        Calculate ZPD alignment score (0-1, higher = better alignment)

        Args:
            student_data: DataFrame with student's learning history

        Returns:
            ZPD score between 0 and 1
        """
        if len(student_data) == 0:
            return 0.5  # Neutral

        # Get accuracy by difficulty level
        difficulty_accuracy = student_data.groupby('difficulty')['is_correct'].mean()

        zpd_scores = []

        for difficulty, accuracy in difficulty_accuracy.items():
            # Score based on how well accuracy aligns with optimal zone
            if self.zpd_thresholds['optimal_low'] <= accuracy <= self.zpd_thresholds['optimal_high']:
                score = 1.0
            elif accuracy > self.zpd_thresholds['too_easy']:
                score = 0.6
            elif accuracy < self.zpd_thresholds['too_hard']:
                score = 0.4
            else:
                score = 0.8

            zpd_scores.append(score)

        return np.mean(zpd_scores) if zpd_scores else 0.5

    def get_next_difficulty(self, recent_results: List[bool],
                          current_difficulty: str) -> str:
        """
        Real-time difficulty adjustment during active session

        Args:
            recent_results: List of recent correctness (True/False)
            current_difficulty: Current difficulty level

        Returns:
            Next recommended difficulty level
        """
        if len(recent_results) < 3:
            return current_difficulty

        # Check last 3 attempts
        last_3 = recent_results[-3:]
        accuracy = sum(last_3) / len(last_3)

        # Check for streaks
        consecutive_correct = self._count_consecutive(recent_results, True)
        consecutive_incorrect = self._count_consecutive(recent_results, False)

        # Progression rules
        if consecutive_correct >= self.progression_rules['consecutive_success_threshold']:
            return self._increase_difficulty(current_difficulty)
        elif consecutive_incorrect >= self.progression_rules['consecutive_failure_threshold']:
            return self._decrease_difficulty(current_difficulty)
        elif accuracy >= 0.8:
            return self._increase_difficulty(current_difficulty)
        elif accuracy <= 0.3:
            return self._decrease_difficulty(current_difficulty)
        else:
            return current_difficulty

    def generate_progression_plan(self, current_level: str,
                                 target_level: str,
                                 num_steps: int = 5) -> List[Dict]:
        """
        Generate gradual progression plan from current to target difficulty
        FIXED: Creates smoother progression with mixed distributions

        Args:
            current_level: Starting difficulty
            target_level: Goal difficulty
            num_steps: Number of steps in progression

        Returns:
            List of progression steps with difficulty distributions
        """
        current_val = self.difficulty_levels.get(current_level, 2)
        target_val = self.difficulty_levels.get(target_level, 3)

        if current_val >= target_val:
            return [{'step': 1, 'difficulty': current_level, 'note': 'Already at or above target'}]

        progression = []

        # Create smooth progression with blended distributions
        for i in range(num_steps):
            progress_ratio = (i + 1) / num_steps

            # Blend between current and target
            blend_val = current_val + (target_val - current_val) * progress_ratio

            # Create distribution that blends difficulties
            distribution = self._create_blended_distribution(
                current_val, target_val, progress_ratio
            )

            # Determine primary difficulty for this step
            primary_diff = self.reverse_difficulty.get(round(blend_val), 'Medium')

            progression.append({
                'step': i + 1,
                'primary_difficulty': primary_diff,
                'distribution': distribution,
                'progress': f"{progress_ratio:.0%} toward {target_level}",
                'milestone': f'Step {i+1}/{num_steps}'
            })

        return progression

    def _create_blended_distribution(self, current_val: float, 
                                    target_val: float, 
                                    progress_ratio: float) -> Dict:
        """Create smooth blended distribution between two difficulty levels"""

        # Current and target distributions
        current_dist = self._get_base_distribution(self.reverse_difficulty[int(current_val)])
        target_dist = self._get_base_distribution(self.reverse_difficulty[int(target_val)])

        # Blend distributions
        blended = {}
        for diff in ['Easy', 'Medium', 'Hard', 'Advanced']:
            current_weight = current_dist.get(diff, 0)
            target_weight = target_dist.get(diff, 0)
            blended[diff] = current_weight * (1 - progress_ratio) + target_weight * progress_ratio

        return self._normalize_distribution(blended)

    def _get_base_distribution(self, difficulty: str) -> Dict:
        """Get base distribution for a difficulty level"""
        distributions = {
            'Easy': {'Easy': 0.7, 'Medium': 0.3, 'Hard': 0.0, 'Advanced': 0.0},
            'Medium': {'Easy': 0.2, 'Medium': 0.6, 'Hard': 0.2, 'Advanced': 0.0},
            'Hard': {'Easy': 0.1, 'Medium': 0.3, 'Hard': 0.5, 'Advanced': 0.1},
            'Advanced': {'Easy': 0.0, 'Medium': 0.2, 'Hard': 0.4, 'Advanced': 0.4}
        }
        return distributions.get(difficulty, distributions['Medium'])

    # Helper methods

    def _calculate_recent_accuracy(self, history: List[Dict], window: int = 10) -> float:
        """Calculate accuracy over recent window"""
        recent = history[-window:] if len(history) > window else history
        if not recent:
            return 0.7

        correct = sum(1 for h in recent if h.get('is_correct', False))
        return correct / len(recent)

    def _calculate_learning_velocity(self, history: List[Dict]) -> float:
        """Calculate rate of learning (improvement/decline)"""
        if len(history) < 10:
            return 0.0

        mid = len(history) // 2
        first_half_acc = self._calculate_recent_accuracy(history[:mid], window=999)
        second_half_acc = self._calculate_recent_accuracy(history[mid:], window=999)

        return second_half_acc - first_half_acc

    def _determine_zpd_zone(self, accuracy: float) -> str:
        """Determine which ZPD zone the accuracy falls into"""
        if accuracy >= self.zpd_thresholds['too_easy']:
            return 'too_easy'
        elif accuracy <= self.zpd_thresholds['too_hard']:
            return 'too_hard'
        else:
            return 'optimal'

    def _increase_difficulty(self, current: str, steps: int = 1) -> str:
        """Increase difficulty by N steps"""
        current_val = self.difficulty_levels.get(current, 2)
        new_val = min(current_val + steps, 4)
        return self.reverse_difficulty[new_val]

    def _decrease_difficulty(self, current: str, steps: int = 1) -> str:
        """Decrease difficulty by N steps"""
        current_val = self.difficulty_levels.get(current, 2)
        new_val = max(current_val - steps, 1)
        return self.reverse_difficulty[new_val]

    def _shift_harder(self, distribution: Dict, factor: float = 0.15) -> Dict:
        """Shift difficulty distribution toward harder"""
        new_dist = distribution.copy()

        transfer = min(new_dist.get('Easy', 0), factor)
        new_dist['Easy'] = new_dist.get('Easy', 0) - transfer
        new_dist['Hard'] = new_dist.get('Hard', 0) + transfer * 0.7
        new_dist['Advanced'] = new_dist.get('Advanced', 0) + transfer * 0.3

        return new_dist

    def _shift_easier(self, distribution: Dict, factor: float = 0.15) -> Dict:
        """Shift difficulty distribution toward easier"""
        new_dist = distribution.copy()

        transfer = min(new_dist.get('Hard', 0), factor)
        new_dist['Hard'] = new_dist.get('Hard', 0) - transfer
        new_dist['Easy'] = new_dist.get('Easy', 0) + transfer * 0.5
        new_dist['Medium'] = new_dist.get('Medium', 0) + transfer * 0.5

        return new_dist

    def _normalize_distribution(self, distribution: Dict) -> Dict:
        """Ensure distribution sums to 1.0"""
        total = sum(distribution.values())
        if total == 0:
            return {'Easy': 0.3, 'Medium': 0.5, 'Hard': 0.2, 'Advanced': 0.0}

        return {k: v/total for k, v in distribution.items()}

    def _calculate_confidence(self, history: List[Dict]) -> str:
        """Calculate confidence level of recommendation"""
        if len(history) < 5:
            return 'low'
        elif len(history) < 15:
            return 'medium'
        else:
            return 'high'

    def _count_consecutive(self, results: List[bool], value: bool) -> int:
        """Count consecutive occurrences of value from end of list"""
        count = 0
        for result in reversed(results):
            if result == value:
                count += 1
            else:
                break
        return count


# Example usage
if __name__ == "__main__":
    adapter = DifficultyAdapter()

    print("\n🎚️ Difficulty Adapter - Zone of Proximal Development (FIXED)")
    print("="*60)

    # Simulate student performance history
    print("\n📊 Scenario 1: Student excelling (90% accuracy)")
    print("-"*60)
    performance_history = [
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': False, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
    ]

    rec = adapter.recommend_difficulty(performance_history, 'Medium')
    print(f"Current Difficulty: {rec['current_difficulty']}")
    print(f"Recent Accuracy: {rec['recent_accuracy']:.1%}")
    print(f"Learning Velocity: {rec['learning_velocity']:+.1%}")
    print(f"ZPD Zone: {rec['zone']}")
    print(f"Recommended: {rec['recommended_difficulty']}")
    print(f"Reason: {rec['reason']}")

    # Scenario 2: Student struggling BUT improving
    print("\n\n📊 Scenario 2: Student struggling but improving (30% → 50%)")
    print("-"*60)
    performance_history = [
        {'is_correct': False, 'difficulty': 'Hard'},
        {'is_correct': False, 'difficulty': 'Hard'},
        {'is_correct': True, 'difficulty': 'Hard'},
        {'is_correct': False, 'difficulty': 'Hard'},
        {'is_correct': False, 'difficulty': 'Hard'},
        {'is_correct': False, 'difficulty': 'Hard'},
        {'is_correct': True, 'difficulty': 'Hard'},
        {'is_correct': False, 'difficulty': 'Hard'},
        {'is_correct': True, 'difficulty': 'Hard'},
        {'is_correct': True, 'difficulty': 'Hard'},
    ]

    rec = adapter.recommend_difficulty(performance_history, 'Hard')
    print(f"Current Difficulty: {rec['current_difficulty']}")
    print(f"Recent Accuracy: {rec['recent_accuracy']:.1%}")
    print(f"Learning Velocity: {rec['learning_velocity']:+.1%}")
    print(f"ZPD Zone: {rec['zone']}")
    print(f"Recommended: {rec['recommended_difficulty']}")
    print(f"Reason: {rec['reason']}")

    # Scenario 3: Optimal zone
    print("\n\n📊 Scenario 3: Student in optimal zone (75% accuracy)")
    print("-"*60)
    performance_history = [
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': False, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': False, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
        {'is_correct': False, 'difficulty': 'Medium'},
        {'is_correct': True, 'difficulty': 'Medium'},
    ]

    rec = adapter.recommend_difficulty(performance_history, 'Medium')
    print(f"Current Difficulty: {rec['current_difficulty']}")
    print(f"Recent Accuracy: {rec['recent_accuracy']:.1%}")
    print(f"Learning Velocity: {rec['learning_velocity']:+.1%}")
    print(f"ZPD Zone: {rec['zone']}")
    print(f"Recommended: {rec['recommended_difficulty']}")
    print(f"Reason: {rec['reason']}")

    # Difficulty distribution
    print("\n\n📊 Difficulty Distribution Example")
    print("-"*60)
    student_perf = {
        'recent_accuracy': 0.78,
        'learning_velocity': 0.12
    }

    distribution = adapter.get_difficulty_distribution(student_perf, 'Medium')
    print("For student with 78% accuracy, +12% velocity:")
    for diff, prob in distribution.items():
        if prob > 0:
            print(f"   {diff}: {prob:.1%}")

    # FIXED Progression plan
    print("\n\n📈 Progression Plan: Easy → Hard (IMPROVED)")
    print("-"*60)
    plan = adapter.generate_progression_plan('Easy', 'Hard', num_steps=4)
    for step in plan:
        print(f"\nStep {step['step']}: {step['primary_difficulty']} ({step['progress']})")
        print(f"   Distribution: ", end='')
        for diff, prob in step['distribution'].items():
            if prob > 0.05:  # Only show >5%
                print(f"{diff}: {prob:.0%}  ", end='')
        print()

    print("\n="*60)
    print("✅ Difficulty adapter examples complete!")
