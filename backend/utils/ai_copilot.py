import json
import re
import os
from typing import Dict, List, Any
from utils.ai_engine import AIEngine
from config import Config

class AICopilotEngine:
    """
    Advanced Multi-Persona AI Educational Copilot Engine for DocMind AI.
    Generates role-tailored insights for Students, Teachers, Professors, HODs, and Deans.
    Produces automated flashcards, quiz question banks with Bloom's taxonomy tags,
    and Vis.js mind map JSON structures.
    """

    @staticmethod
    def _generate(prompt: str) -> str:
        api_key = Config.GROQ_API_KEY or os.environ.get('GROQ_API_KEY', '')
        if api_key:
            res = AIEngine.call_groq(prompt, api_key)
            if res:
                return res
        return "Insight generated based on educational document context."

    @staticmethod
    def generate_role_insight(role: str, grade: str, document_title: str, text_snippet: str) -> str:
        """
        Generates specialized multi-persona executive insights based on academic role and grade tier.
        """
        role_lower = role.lower()
        
        system_instructions = {
            'student': f"You are a supportive AI Academic Mentor for a {grade} student. Explain concepts simply, highlight key definitions, formulas, and pre-exam revision tips.",
            'teacher': f"You are a Senior Educator AI Assistant. Synthesize lesson plans, teaching strategies, classroom discussion prompts, and key student learning outcomes from this content.",
            'professor': f"You are a University Professor AI Academic Advisor. Evaluate syllabus compliance, reference book accuracy, advanced theoretical derivations, and research paper connections.",
            'hod': f"You are a Head of Department (HOD) Academic Compliance Auditor. Summarize departmental curriculum coverage, NAAC/NBA accreditation alignment, and unit learning objectives.",
            'dean': f"You are an Institutional Dean AI Executive Counselor. Provide high-level executive academic analytics, accreditation audit readiness, and inter-departmental curriculum synthesis."
        }

        prompt_context = system_instructions.get(role_lower, system_instructions['student'])
        
        query = (
            f"{prompt_context}\n\n"
            f"Document: {document_title}\n"
            f"Grade Tier: {grade}\n"
            f"Content Snippet: {text_snippet[:2000]}\n\n"
            f"Please generate a structured, executive 3-bullet insight with actionable academic recommendations for the {role}."
        )

        return AICopilotEngine._generate(query)

    @staticmethod
    def generate_flashcards(text_snippet: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Generates structured 3D study flashcards (Question/Front and Answer/Back) from text.
        """
        prompt = (
            f"Extract exactly {count} high-priority study flashcards from the following educational text snippet.\n"
            f"Return ONLY valid JSON array format like this:\n"
            f"[{{\"front\": \"What is X?\", \"back\": \"X is Y...\", \"unit\": \"Unit I\"}}]\n\n"
            f"Text Snippet:\n{text_snippet[:2500]}"
        )

        raw_response = AICopilotEngine._generate(prompt)
        
        try:
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            if json_match:
                cards = json.loads(json_match.group(0))
                return cards[:count]
        except Exception as e:
            print(f"Error parsing AI flashcard JSON: {e}")

        # Fallback flashcard generation if JSON parsing fails
        return [
            {
                "front": "What is the primary concept discussed in this chapter?",
                "back": text_snippet[:200] + "...",
                "unit": "Unit I"
            },
            {
                "front": "What are the key definitions and formulas?",
                "back": "Refer to textbook section for detailed derivations.",
                "unit": "Unit I"
            }
        ]

    @staticmethod
    def generate_quiz_questions(text_snippet: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Generates multiple-choice quiz questions (MCQs) with 4 options, correct answer, and Bloom's taxonomy level.
        """
        prompt = (
            f"Generate exactly {num_questions} multiple-choice quiz questions (MCQs) based on the text below.\n"
            f"Return ONLY valid JSON array format like this:\n"
            f"[\n"
            f"  {{\n"
            f"    \"question\": \"Which algorithm is used for CPU scheduling?\",\n"
            f"    \"options\": [\"Round Robin\", \"K-Means\", \"Dijkstra\", \"Bubble Sort\"],\n"
            f"    \"correct_index\": 0,\n"
            f"    \"explanation\": \"Round Robin is a preemptive CPU scheduling algorithm.\",\n"
            f"    \"blooms_level\": \"Remember\"\n"
            f"  }}\n"
            f"]\n\n"
            f"Text:\n{text_snippet[:2500]}"
        )

        raw_response = AICopilotEngine._generate(prompt)

        try:
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group(0))
                return questions[:num_questions]
        except Exception as e:
            print(f"Error parsing AI quiz JSON: {e}")

        # Fallback question bank
        return [
            {
                "question": "What is the main resource managed by an Operating System?",
                "options": ["CPU and Memory", "Printer paper", "Web browser", "Email server"],
                "correct_index": 0,
                "explanation": "Operating systems primarily manage hardware resources such as CPU, memory, and storage.",
                "blooms_level": "Remember"
            }
        ]

    @staticmethod
    def generate_mindmap_nodes(text_snippet: str) -> Dict[str, Any]:
        """
        Generates Vis.js compatible node network graph (nodes and edges) from course text.
        """
        prompt = (
            "Extract key concepts and their relationships from the text to build a visual mind map.\n"
            "Return ONLY valid JSON object in this format:\n"
            "{\n"
            '  "nodes": [{"id": 1, "label": "Operating System", "group": "main"}, {"id": 2, "label": "CPU Scheduling", "group": "sub"}],\n'
            '  "edges": [{"from": 1, "to": 2, "label": "manages"}]\n'
            "}\n\n"
            f"Text:\n{text_snippet[:2000]}"
        )

        raw_response = AICopilotEngine._generate(prompt)

        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                mindmap_data = json.loads(json_match.group(0))
                if 'nodes' in mindmap_data and 'edges' in mindmap_data:
                    return mindmap_data
        except Exception as e:
            print(f"Error parsing AI mindmap JSON: {e}")

        # Default fallback network graph
        return {
            "nodes": [
                {"id": 1, "label": "Course Foundation", "group": "main"},
                {"id": 2, "label": "Unit I: Overview", "group": "sub"},
                {"id": 3, "label": "Unit II: Core Architecture", "group": "sub"},
                {"id": 4, "label": "Key Formulas & Theorems", "group": "concept"}
            ],
            "edges": [
                {"from": 1, "to": 2, "label": "introduces"},
                {"from": 1, "to": 3, "label": "expands into"},
                {"from": 3, "to": 4, "label": "contains"}
            ]
        }
