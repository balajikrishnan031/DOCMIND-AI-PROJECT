import math
import time
from typing import Dict, List, Any

class AcademicAnalyticsEngine:
    """
    Enterprise Academic Analytics & Cognitive Assessment Engine for DocMind AI.
    Provides Ebbinghaus memory retention decay modeling, Bloom's Taxonomy cognitive level
    classification, Topic Weakness Index scoring, and Exam Readiness Score prediction.
    """

    @staticmethod
    def calculate_ebbinghaus_retention(days_elapsed: float, stability_factor: float = 3.5) -> float:
        """
        Calculates memory retention percentage using the Ebbinghaus Forgetting Curve formula:
        R = e^(-t / S) * 100
        where:
          t = days elapsed since last active recall review
          S = stability factor of memory (higher with spaced repetition)
        """
        if days_elapsed <= 0:
            return 100.0
        retention = math.exp(-days_elapsed / max(0.5, stability_factor)) * 100.0
        return round(max(5.0, min(100.0, retention)), 1)

    @staticmethod
    def classify_blooms_taxonomy(question_text: str) -> Dict[str, Any]:
        """
        Classifies educational questions or topics into Bloom's Taxonomy 6 Cognitive Levels.
        """
        text_lower = question_text.lower()
        
        remember_keywords = ['define', 'list', 'name', 'state', 'identify', 'recall', 'what is', 'mention']
        understand_keywords = ['explain', 'describe', 'discuss', 'summarize', 'classify', 'interpret', 'why']
        apply_keywords = ['apply', 'calculate', 'solve', 'demonstrate', 'compute', 'implement', 'use']
        analyze_keywords = ['analyze', 'compare', 'contrast', 'differentiate', 'distinguish', 'examine']
        evaluate_keywords = ['evaluate', 'justify', 'critique', 'assess', 'validate', 'recommend']
        create_keywords = ['design', 'construct', 'formulate', 'synthesize', 'create', 'develop', 'build']

        score_map = {
            'Remember': sum(1 for k in remember_keywords if k in text_lower),
            'Understand': sum(1 for k in understand_keywords if k in text_lower),
            'Apply': sum(1 for k in apply_keywords if k in text_lower),
            'Analyze': sum(1 for k in analyze_keywords if k in text_lower),
            'Evaluate': sum(1 for k in evaluate_keywords if k in text_lower),
            'Create': sum(1 for k in create_keywords if k in text_lower)
        }

        best_level = max(score_map, key=score_map.get)
        if score_map[best_level] == 0:
            best_level = 'Understand'  # Default cognitive level for academic questions

        level_weights = {
            'Remember': 1,
            'Understand': 2,
            'Apply': 3,
            'Analyze': 4,
            'Evaluate': 5,
            'Create': 6
        }

        return {
            'level': best_level,
            'cognitive_weight': level_weights[best_level],
            'scores': score_map,
            'description': f"Bloom's Cognitive Level: {best_level} (Weight: {level_weights[best_level]}/6)"
        }

    @staticmethod
    def predict_exam_readiness(
        quiz_accuracy_pct: float,
        syllabus_coverage_pct: float,
        flashcard_mastery_pct: float,
        study_hours_logged: float,
        days_to_exam: int = 14
    ) -> Dict[str, Any]:
        """
        Predicts comprehensive Exam Readiness Score (0 to 100%) and provides actionable recommendations.
        """
        # Weighted formula
        # Quiz Accuracy: 35% weight
        # Syllabus Coverage: 30% weight
        # Flashcard Mastery: 25% weight
        # Consistency (Study Hours): 10% weight
        
        hours_score = min(100.0, (study_hours_logged / 20.0) * 100.0)
        
        readiness_score = (
            (quiz_accuracy_pct * 0.35) +
            (syllabus_coverage_pct * 0.30) +
            (flashcard_mastery_pct * 0.25) +
            (hours_score * 0.10)
        )
        
        readiness_score = round(max(0.0, min(100.0, readiness_score)), 1)
        
        if readiness_score >= 85.0:
            status = 'EXCELLENT'
            color = 'success'
            recommendation = 'You are well-prepared for your exams! Focus on high-level synthesis and revision.'
        elif readiness_score >= 70.0:
            status = 'GOOD'
            color = 'cyan'
            recommendation = 'Solid progress! Review weak syllabus units and take 2 more practice quizzes.'
        elif readiness_score >= 50.0:
            status = 'NEEDS_WORK'
            color = 'warning'
            recommendation = 'Moderate preparation. Increase daily active recall flashcards and complete unread topics.'
        else:
            status = 'CRITICAL'
            color = 'danger'
            recommendation = 'High risk! Immediate revision required. Focus on Unit I & Unit II fundamentals first.'

        return {
            'readiness_score': readiness_score,
            'status': status,
            'color': color,
            'recommendation': recommendation,
            'breakdown': {
                'quiz_contribution': round(quiz_accuracy_pct * 0.35, 1),
                'syllabus_contribution': round(syllabus_coverage_pct * 0.30, 1),
                'flashcard_contribution': round(flashcard_mastery_pct * 0.25, 1),
                'consistency_contribution': round(hours_score * 0.10, 1)
            }
        }

    @staticmethod
    def compute_topic_weakness_index(quiz_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes historical quiz results to calculate Topic Weakness Index (0 - 100%) for targeted remediation.
        """
        topic_stats = {}
        
        for q in quiz_results:
            topic = q.get('topic', 'General Concepts')
            is_correct = q.get('is_correct', False)
            
            if topic not in topic_stats:
                topic_stats[topic] = {'total': 0, 'correct': 0}
            
            topic_stats[topic]['total'] += 1
            if is_correct:
                topic_stats[topic]['correct'] += 1

        weakness_list = []
        for topic, data in topic_stats.items():
            acc = (data['correct'] / data['total']) * 100.0
            weakness_index = round(100.0 - acc, 1)
            
            weakness_list.append({
                'topic': topic,
                'total_attempts': data['total'],
                'accuracy_pct': round(acc, 1),
                'weakness_index': weakness_index,
                'priority': 'HIGH' if weakness_index >= 50.0 else ('MEDIUM' if weakness_index >= 25.0 else 'LOW')
            })

        weakness_list.sort(key=lambda x: x['weakness_index'], reverse=True)
        return weakness_list
