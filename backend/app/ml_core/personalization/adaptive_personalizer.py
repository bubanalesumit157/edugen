"""
Adaptive Personalizer - Main Adaptive Engine
Integrates ML models to provide real-time personalized learning experiences
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


class AdaptivePersonalizer:
    """
    Main adaptive personalization engine
    Integrates DKT, performance prediction, and learning path generation
    to provide real-time personalized recommendations
    """

    def __init__(self):
        self.personalization_modes = {
            'aggressive': {'difficulty_factor': 1.2, 'challenge_threshold': 0.75},
            'balanced': {'difficulty_factor': 1.0, 'challenge_threshold': 0.70},
            'supportive': {'difficulty_factor': 0.8, 'challenge_threshold': 0.60}
        }

        self.difficulty_map = {
            'Easy': 1,
            'Medium': 2,
            'Hard': 3,
            'Advanced': 4
        }

        self.bloom_map = {
            'Remember': 1,
            'Understand': 2,
            'Apply': 3,
            'Analyze': 4,
            'Evaluate': 5,
            'Create': 6
        }

    def personalize_assignment(self, student_id: str,
                              learning_sequences: pd.DataFrame,
                              performance_history: pd.DataFrame,
                              available_topics: List[str] = None,
                              num_questions: int = 10,
                              mode: str = 'balanced') -> Dict:
        """
        Generate personalized assignment for a student

        Args:
            student_id: Student identifier
            learning_sequences: Student's learning history
            performance_history: Student's performance records
            available_topics: Topics to choose from (None = all topics)
            num_questions: Number of questions to recommend
            mode: 'aggressive', 'balanced', or 'supportive'

        Returns:
            Dict with personalized assignment recommendations
        """
        # Get student data
        student_sequences = learning_sequences[
            learning_sequences['student_id'] == student_id
        ]
        student_performance = performance_history[
            performance_history['student_id'] == student_id
        ]

        if len(student_sequences) == 0:
            return self._get_default_assignment(num_questions)

        # Analyze current state
        current_state = self._analyze_current_state(student_sequences, student_performance)

        # Get recommended difficulty
        difficulty_rec = self._recommend_difficulty(current_state, mode)

        # Select topics
        topic_recommendations = self._select_topics(
            student_performance, available_topics, num_questions
        )

        # Build question recommendations
        question_recommendations = self._build_question_recommendations(
            topic_recommendations, difficulty_rec, num_questions
        )

        # Generate metadata
        metadata = self._generate_metadata(current_state, mode)

        return {
            'student_id': student_id,
            'current_state': current_state,
            'difficulty_recommendation': difficulty_rec,
            'topic_recommendations': topic_recommendations,
            'question_recommendations': question_recommendations,
            'personalization_metadata': metadata
        }

    def get_next_question(self, student_id: str,
                         recent_performance: List[Dict],
                         available_questions: pd.DataFrame,
                         context: Dict = None) -> Dict:
        """
        Real-time next question recommendation during an active session

        Args:
            student_id: Student identifier
            recent_performance: Recent answers in current session
            available_questions: Pool of available questions
            context: Additional context (current topic, etc.)

        Returns:
            Recommended next question
        """
        if len(recent_performance) == 0:
            # First question - start moderate
            return self._get_initial_question(available_questions)

        # Analyze session performance
        session_accuracy = np.mean([q['is_correct'] for q in recent_performance])
        last_3_accuracy = np.mean([q['is_correct'] for q in recent_performance[-3:]])

        # Determine difficulty adjustment
        if last_3_accuracy >= 0.8:
            # Doing well - increase difficulty
            target_difficulty = self._increase_difficulty(recent_performance[-1]['difficulty'])
        elif last_3_accuracy <= 0.4:
            # Struggling - decrease difficulty
            target_difficulty = self._decrease_difficulty(recent_performance[-1]['difficulty'])
        else:
            # Maintain current level
            target_difficulty = recent_performance[-1]['difficulty']

        # Filter questions
        filtered = available_questions[
            available_questions['difficulty'] == target_difficulty
        ]

        # If topic context provided, prefer same topic
        if context and 'current_topic' in context:
            topic_filtered = filtered[filtered['topic'] == context['current_topic']]
            if len(topic_filtered) > 0:
                filtered = topic_filtered

        # Select question (random from filtered pool)
        if len(filtered) > 0:
            question = filtered.sample(1).iloc[0]
            return {
                'question_id': question.get('question_id', 'Q_' + str(np.random.randint(1000, 9999))),
                'topic': question['topic'],
                'difficulty': question['difficulty'],
                'bloom_level': question.get('bloom_level', 'Apply'),
                'reason': f'Adapted to {target_difficulty} based on recent performance'
            }
        else:
            # Fallback
            return self._get_initial_question(available_questions)

    def adapt_to_performance(self, student_id: str,
                           current_assignment: Dict,
                           completed_questions: List[Dict]) -> Dict:
        """
        Adapt remaining questions based on performance so far

        Args:
            student_id: Student identifier
            current_assignment: Original assignment
            completed_questions: Questions completed so far

        Returns:
            Updated recommendations for remaining questions
        """
        if len(completed_questions) == 0:
            return current_assignment

        # Calculate current performance
        current_accuracy = np.mean([q['is_correct'] for q in completed_questions])

        # Determine if adaptation is needed
        adaptation_needed = self._check_adaptation_needed(
            current_accuracy, 
            current_assignment['difficulty_recommendation']
        )

        if not adaptation_needed:
            return current_assignment

        # Adapt difficulty
        if current_accuracy >= 0.85:
            new_difficulty = self._increase_difficulty(
                current_assignment['difficulty_recommendation']['primary_difficulty']
            )
            reason = 'Student excelling - increasing challenge'
        elif current_accuracy <= 0.35:
            new_difficulty = self._decrease_difficulty(
                current_assignment['difficulty_recommendation']['primary_difficulty']
            )
            reason = 'Student struggling - providing support'
        else:
            new_difficulty = current_assignment['difficulty_recommendation']['primary_difficulty']
            reason = 'Maintaining current difficulty'

        # Update recommendations
        updated_assignment = current_assignment.copy()
        updated_assignment['difficulty_recommendation']['primary_difficulty'] = new_difficulty
        updated_assignment['difficulty_recommendation']['adaptation_reason'] = reason

        return updated_assignment

    def _analyze_current_state(self, sequences: pd.DataFrame, 
                              performance: pd.DataFrame) -> Dict:
        """Analyze student's current learning state"""
        # Overall metrics
        overall_accuracy = sequences['is_correct'].mean()
        overall_score = sequences['score'].mean()

        # Recent performance (last 20% of attempts)
        cutoff = int(len(sequences) * 0.8)
        recent = sequences.iloc[cutoff:]
        recent_accuracy = recent['is_correct'].mean()
        recent_score = recent['score'].mean()

        # Performance by difficulty
        difficulty_performance = sequences.groupby('difficulty')['is_correct'].mean().to_dict()

        # Knowledge state
        if len(performance) > 0:
            mastered_topics = len(performance[performance['accuracy'] >= 0.85])
            proficient_topics = len(performance[(performance['accuracy'] >= 0.7) & 
                                               (performance['accuracy'] < 0.85)])
            weak_topics = len(performance[performance['accuracy'] < 0.5])
        else:
            mastered_topics = proficient_topics = weak_topics = 0

        # Learning velocity
        if len(sequences) >= 10:
            first_half = sequences.iloc[:len(sequences)//2]['is_correct'].mean()
            second_half = sequences.iloc[len(sequences)//2:]['is_correct'].mean()
            learning_velocity = second_half - first_half
        else:
            learning_velocity = 0.0

        return {
            'overall_accuracy': overall_accuracy,
            'overall_score': overall_score,
            'recent_accuracy': recent_accuracy,
            'recent_score': recent_score,
            'learning_velocity': learning_velocity,
            'difficulty_performance': difficulty_performance,
            'mastered_topics': mastered_topics,
            'proficient_topics': proficient_topics,
            'weak_topics': weak_topics,
            'total_attempts': len(sequences),
            'performance_tier': self._get_performance_tier(overall_accuracy)
        }

    def _recommend_difficulty(self, current_state: Dict, mode: str) -> Dict:
        """Recommend difficulty distribution for assignment"""
        mode_config = self.personalization_modes.get(mode, self.personalization_modes['balanced'])

        overall_accuracy = current_state['overall_accuracy']
        recent_accuracy = current_state['recent_accuracy']
        learning_velocity = current_state['learning_velocity']

        # Base difficulty on recent performance
        if recent_accuracy >= 0.85:
            primary_difficulty = 'Hard'
            distribution = {'Easy': 0.1, 'Medium': 0.3, 'Hard': 0.5, 'Advanced': 0.1}
        elif recent_accuracy >= 0.70:
            primary_difficulty = 'Medium'
            distribution = {'Easy': 0.2, 'Medium': 0.5, 'Hard': 0.3, 'Advanced': 0.0}
        elif recent_accuracy >= 0.50:
            primary_difficulty = 'Medium'
            distribution = {'Easy': 0.3, 'Medium': 0.5, 'Hard': 0.2, 'Advanced': 0.0}
        else:
            primary_difficulty = 'Easy'
            distribution = {'Easy': 0.6, 'Medium': 0.3, 'Hard': 0.1, 'Advanced': 0.0}

        # Adjust based on learning velocity
        if learning_velocity > 0.15:
            # Rapid improvement - increase challenge
            distribution = self._shift_distribution_harder(distribution)
        elif learning_velocity < -0.15:
            # Declining - provide support
            distribution = self._shift_distribution_easier(distribution)

        # Apply mode factor
        if mode == 'aggressive':
            distribution = self._shift_distribution_harder(distribution)
        elif mode == 'supportive':
            distribution = self._shift_distribution_easier(distribution)

        return {
            'primary_difficulty': primary_difficulty,
            'distribution': distribution,
            'mode': mode,
            'reasoning': self._generate_difficulty_reasoning(
                recent_accuracy, learning_velocity, mode
            )
        }

    def _select_topics(self, performance: pd.DataFrame,
                      available_topics: Optional[List[str]],
                      num_questions: int) -> List[Dict]:
        """Select topics for assignment"""
        if len(performance) == 0:
            return []

        # Filter by available topics if specified
        if available_topics:
            performance = performance[performance['topic'].isin(available_topics)]

        if len(performance) == 0:
            return []

        # Categorize topics
        weak_topics = performance[performance['accuracy'] < 0.6].sort_values('accuracy')
        developing_topics = performance[
            (performance['accuracy'] >= 0.6) & (performance['accuracy'] < 0.85)
        ].sort_values('accuracy')

        # Recommend mix of topics
        recommendations = []

        # 60% weak topics (for improvement)
        weak_count = int(num_questions * 0.6)
        for _, row in weak_topics.head(weak_count).iterrows():
            recommendations.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'reason': 'Knowledge Gap',
                'current_accuracy': row['accuracy'],
                'priority': 'High'
            })

        # 40% developing topics (for advancement)
        dev_count = num_questions - len(recommendations)
        for _, row in developing_topics.head(dev_count).iterrows():
            recommendations.append({
                'subject': row['subject'],
                'topic': row['topic'],
                'reason': 'Skill Development',
                'current_accuracy': row['accuracy'],
                'priority': 'Medium'
            })

        return recommendations

    def _build_question_recommendations(self, topic_recs: List[Dict],
                                       difficulty_rec: Dict,
                                       num_questions: int) -> List[Dict]:
        """Build detailed question recommendations"""
        questions = []
        distribution = difficulty_rec['distribution']

        # Calculate questions per difficulty
        difficulty_counts = {
            diff: int(num_questions * prob) 
            for diff, prob in distribution.items()
        }

        # Ensure total equals num_questions
        total = sum(difficulty_counts.values())
        if total < num_questions:
            difficulty_counts[difficulty_rec['primary_difficulty']] += (num_questions - total)

        # Distribute topics across difficulties
        topic_idx = 0
        for difficulty, count in difficulty_counts.items():
            if count == 0:
                continue

            for _ in range(count):
                if topic_idx < len(topic_recs):
                    topic = topic_recs[topic_idx]
                    topic_idx = (topic_idx + 1) % len(topic_recs)
                else:
                    topic = topic_recs[0] if topic_recs else {
                        'subject': 'General', 'topic': 'Mixed'
                    }

                questions.append({
                    'subject': topic['subject'],
                    'topic': topic['topic'],
                    'difficulty': difficulty,
                    'bloom_level': self._get_bloom_for_difficulty(difficulty),
                    'reason': topic.get('reason', 'Practice')
                })

        return questions

    def _generate_metadata(self, current_state: Dict, mode: str) -> Dict:
        """Generate metadata about personalization"""
        return {
            'personalization_mode': mode,
            'student_tier': current_state['performance_tier'],
            'adaptation_factors': {
                'recent_performance': current_state['recent_accuracy'],
                'learning_velocity': current_state['learning_velocity'],
                'knowledge_coverage': {
                    'mastered': current_state['mastered_topics'],
                    'proficient': current_state['proficient_topics'],
                    'weak': current_state['weak_topics']
                }
            },
            'recommendations': self._generate_educator_insights(current_state)
        }

    def _generate_educator_insights(self, current_state: Dict) -> List[str]:
        """Generate insights for educators/system"""
        insights = []
        
        if current_state['learning_velocity'] < -0.1:
            insights.append('⚠️ Declining performance - recommend intervention or difficulty reduction')
        
        if current_state['weak_topics'] > 5:
            insights.append('📊 Multiple weak topics - suggest focused remediation before new content')
        
        if current_state['recent_accuracy'] < current_state['overall_accuracy'] - 0.15:
            insights.append('📉 Recent performance drop - recommend teacher review or reduced workload')
        
        if current_state['recent_accuracy'] >= 0.85:
            insights.append('✅ High performance - ready for advanced challenges')
        
        return insights


    # Helper methods

    def _get_performance_tier(self, accuracy: float) -> str:
        """Get performance tier"""
        if accuracy >= 0.85:
            return 'Excellent'
        elif accuracy >= 0.70:
            return 'Good'
        elif accuracy >= 0.55:
            return 'Average'
        elif accuracy >= 0.40:
            return 'Below Average'
        else:
            return 'Struggling'

    def _increase_difficulty(self, current: str) -> str:
        """Increase difficulty level"""
        levels = ['Easy', 'Medium', 'Hard', 'Advanced']
        current_idx = levels.index(current) if current in levels else 1
        return levels[min(current_idx + 1, len(levels) - 1)]

    def _decrease_difficulty(self, current: str) -> str:
        """Decrease difficulty level"""
        levels = ['Easy', 'Medium', 'Hard', 'Advanced']
        current_idx = levels.index(current) if current in levels else 1
        return levels[max(current_idx - 1, 0)]

    def _shift_distribution_harder(self, distribution: Dict) -> Dict:
        """Shift difficulty distribution to harder"""
        new_dist = distribution.copy()
        # Transfer 10% from Easy to Hard/Advanced
        transfer = min(new_dist.get('Easy', 0), 0.1)
        new_dist['Easy'] = new_dist.get('Easy', 0) - transfer
        new_dist['Hard'] = new_dist.get('Hard', 0) + transfer * 0.7
        new_dist['Advanced'] = new_dist.get('Advanced', 0) + transfer * 0.3
        return new_dist

    def _shift_distribution_easier(self, distribution: Dict) -> Dict:
        """Shift difficulty distribution to easier"""
        new_dist = distribution.copy()
        # Transfer 10% from Hard to Easy/Medium
        transfer = min(new_dist.get('Hard', 0), 0.1)
        new_dist['Hard'] = new_dist.get('Hard', 0) - transfer
        new_dist['Easy'] = new_dist.get('Easy', 0) + transfer * 0.5
        new_dist['Medium'] = new_dist.get('Medium', 0) + transfer * 0.5
        return new_dist

    def _get_bloom_for_difficulty(self, difficulty: str) -> str:
        """Get appropriate Bloom level for difficulty"""
        bloom_map = {
            'Easy': 'Remember',
            'Medium': 'Apply',
            'Hard': 'Analyze',
            'Advanced': 'Evaluate'
        }
        return bloom_map.get(difficulty, 'Apply')

    def _generate_difficulty_reasoning(self, accuracy: float, 
                                      velocity: float, mode: str) -> str:
        """Generate reasoning for difficulty choice"""
        reasons = []

        if accuracy >= 0.85:
            reasons.append('High recent accuracy')
        elif accuracy < 0.5:
            reasons.append('Low recent accuracy - providing support')

        if velocity > 0.15:
            reasons.append('Rapid improvement trajectory')
        elif velocity < -0.15:
            reasons.append('Declining performance - adjusting difficulty')

        reasons.append(f'{mode.capitalize()} personalization mode')

        return '; '.join(reasons)

    def _check_adaptation_needed(self, current_accuracy: float, 
                                difficulty_rec: Dict) -> bool:
        """Check if mid-assignment adaptation is needed"""
        primary = difficulty_rec['primary_difficulty']

        if primary == 'Hard' and current_accuracy < 0.4:
            return True  # Too hard
        elif primary == 'Easy' and current_accuracy > 0.9:
            return True  # Too easy

        return False

    def _get_initial_question(self, questions: pd.DataFrame) -> Dict:
        """Get initial question for new session"""
        # Start with medium difficulty
        medium = questions[questions['difficulty'] == 'Medium']
        if len(medium) > 0:
            q = medium.sample(1).iloc[0]
        else:
            q = questions.sample(1).iloc[0]

        return {
            'question_id': q.get('question_id', 'Q_INIT'),
            'topic': q.get('topic', 'General'),
            'difficulty': q.get('difficulty', 'Medium'),
            'bloom_level': q.get('bloom_level', 'Apply'),
            'reason': 'Initial assessment question'
        }

    def _get_default_assignment(self, num_questions: int) -> Dict:
        """Get default assignment for new students"""
        return {
            'message': 'No learning history - using default balanced assignment',
            'difficulty_recommendation': {
                'primary_difficulty': 'Medium',
                'distribution': {'Easy': 0.3, 'Medium': 0.5, 'Hard': 0.2, 'Advanced': 0.0}
            },
            'question_recommendations': [
                {'difficulty': 'Medium', 'reason': 'Initial assessment'}
                for _ in range(num_questions)
            ]
        }


# Example usage
if __name__ == "__main__":
    from utils.data_loader import DataLoader

    loader = DataLoader()

    try:
        sequences = loader.load_learning_sequences()
        performance = loader.load_performance_history()

        personalizer = AdaptivePersonalizer()

        student_id = sequences['student_id'].iloc[0]

        print(f"\n🎯 Personalizing Assignment for {student_id}")
        print("="*60)

        # Generate personalized assignment
        assignment = personalizer.personalize_assignment(
            student_id, sequences, performance, 
            num_questions=10, mode='balanced'
        )

        # Current state
        print("\n📊 Current State:")
        state = assignment['current_state']
        print(f"   Performance Tier: {state['performance_tier']}")
        print(f"   Overall Accuracy: {state['overall_accuracy']:.1%}")
        print(f"   Recent Accuracy: {state['recent_accuracy']:.1%}")
        print(f"   Learning Velocity: {state['learning_velocity']:+.1%}")
        print(f"   Mastered Topics: {state['mastered_topics']}")
        print(f"   Weak Topics: {state['weak_topics']}")

        # Difficulty recommendation
        print("\n🎚️ Difficulty Recommendation:")
        diff_rec = assignment['difficulty_recommendation']
        print(f"   Primary: {diff_rec['primary_difficulty']}")
        print(f"   Distribution:")
        for diff, prob in diff_rec['distribution'].items():
            if prob > 0:
                print(f"      {diff}: {prob:.0%}")
        print(f"   Reasoning: {diff_rec['reasoning']}")

        # Topic recommendations
        print("\n📚 Topic Recommendations:")
        for i, topic in enumerate(assignment['topic_recommendations'][:5], 1):
            print(f"   {i}. {topic['topic']} ({topic['subject']})")
            print(f"      Reason: {topic['reason']}, Accuracy: {topic['current_accuracy']:.1%}")

        # Question breakdown
        print("\n📝 Assignment Breakdown (10 questions):")
        questions = assignment['question_recommendations']
        for diff in ['Easy', 'Medium', 'Hard', 'Advanced']:
            count = len([q for q in questions if q['difficulty'] == diff])
            if count > 0:
                print(f"   {diff}: {count} questions")

        # Recommendations
        print("\n💡 Study Recommendations:")
        recs = assignment['personalization_metadata']['recommendations']
        if recs:
            for i, rec in enumerate(recs, 1):
                print(f"   {i}. {rec}")
        else:
            print("   Continue with current approach!")

        print("\n="*60)
        print("✅ Personalization complete!")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
