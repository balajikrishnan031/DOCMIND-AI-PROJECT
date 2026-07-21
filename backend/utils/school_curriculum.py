from typing import Dict, List, Any

class SchoolCurriculumRegistry:
    """
    Standard 1 to 12 School Curriculum & Subject Master Registry for DocMind AI.
    Covers Primary (Std 1-5), Middle (Std 6-8), High School (Std 9-10), and Higher Secondary (Std 11-12).
    """

    @staticmethod
    def get_tier_for_grade(grade_std: int) -> str:
        if 1 <= grade_std <= 5:
            return "Primary School (Std 1 - 5)"
        elif 6 <= grade_std <= 8:
            return "Middle School (Std 6 - 8)"
        elif 9 <= grade_std <= 10:
            return "High School (Std 9 - 10)"
        elif 11 <= grade_std <= 12:
            return "Higher Secondary (Std 11 - 12)"
        return "General School"

    @staticmethod
    def get_subjects_for_grade(grade_std: int) -> List[Dict[str, Any]]:
        """
        Returns structured subjects, core topics, and formula guides for any grade from Std 1 to 12.
        """
        tier = SchoolCurriculumRegistry.get_tier_for_grade(grade_std)
        
        if grade_std <= 5:
            return [
                {
                    "subject": "Mathematics",
                    "icon": "fa-calculator",
                    "topics": ["Addition & Subtraction", "Multiplication Tables", "Fractions & Shapes", "Measurement & Time"]
                },
                {
                    "subject": "Environmental Studies (EVS)",
                    "icon": "fa-leaf",
                    "topics": ["Plants & Animals", "Human Body & Health", "Water & Air Cycle", "Our Neighborhood & Solar System"]
                },
                {
                    "subject": "English & Grammar",
                    "icon": "fa-book-open",
                    "topics": ["Nouns, Verbs & Adjectives", "Sentence Formation", "Reading Comprehension", "Vocabulary Building"]
                },
                {
                    "subject": "General Knowledge (GK)",
                    "icon": "fa-globe",
                    "topics": ["Famous Monuments", "Indian National Symbols", "Inventions & Discoveries", "Good Habits"]
                }
            ]
        elif 6 <= grade_std <= 8:
            return [
                {
                    "subject": "Mathematics",
                    "icon": "fa-square-root-variable",
                    "topics": ["Integers & Rational Numbers", "Algebraic Expressions", "Linear Equations", "Geometry & Mensuration"]
                },
                {
                    "subject": "Science (Physics / Chemistry / Biology)",
                    "icon": "fa-flask",
                    "topics": ["Nutrition in Plants & Animals", "Heat & Temperature", "Light, Shadows & Reflection", "Acids, Bases & Salts"]
                },
                {
                    "subject": "Social Science",
                    "icon": "fa-landmark",
                    "topics": ["Ancient & Medieval India", "Globe & Maps", "Our Constitution & Civics", "Resources & Environment"]
                },
                {
                    "subject": "Computer Science & Coding",
                    "icon": "fa-laptop-code",
                    "topics": ["Computer Hardware & Software", "Algorithms & Flowcharts", "Scratch Block Coding", "Internet Safety"]
                }
            ]
        elif 9 <= grade_std <= 10:
            return [
                {
                    "subject": "Mathematics",
                    "icon": "fa-calculator",
                    "topics": ["Real Numbers & Polynomials", "Pair of Linear Equations", "Quadratic Equations & AP", "Trigonometry & Statistics"]
                },
                {
                    "subject": "Physics",
                    "icon": "fa-atom",
                    "topics": ["Motion, Force & Laws of Motion", "Gravitation & Work Energy", "Light Reflection & Refraction", "Electricity & Magnetic Effects"]
                },
                {
                    "subject": "Chemistry",
                    "icon": "fa-vial",
                    "topics": ["Matter & Atomic Structure", "Chemical Reactions & Equations", "Acids, Bases & Metals", "Carbon & Its Compounds"]
                },
                {
                    "subject": "Biology",
                    "icon": "fa-dna",
                    "topics": ["Cell - Fundamental Unit of Life", "Life Processes & Control", "How Organisms Reproduce", "Heredity & Our Environment"]
                }
            ]
        else: # Std 11 & 12
            return [
                {
                    "subject": "Physics",
                    "icon": "fa-bolt",
                    "topics": ["Kinematics & Laws of Motion", "Work, Power & Energy", "Electrostatics & Current", "Optics & Modern Physics"]
                },
                {
                    "subject": "Chemistry",
                    "icon": "fa-flask-vial",
                    "topics": ["Chemical Bonding & Thermodynamics", "Equilibrium & Electrochemistry", "Organic Chemistry Mechanisms", "Coordination Compounds"]
                },
                {
                    "subject": "Mathematics",
                    "icon": "fa-infinity",
                    "topics": ["Sets, Relations & Functions", "Limits & Differential Calculus", "Integral Calculus & Vectors", "Probability & Matrices"]
                },
                {
                    "subject": "Biology",
                    "icon": "fa-microscope",
                    "topics": ["Diversity in Living World", "Plant & Human Physiology", "Genetics & Molecular Biology", "Biotechnology & Ecology"]
                },
                {
                    "subject": "Computer Science (Python)",
                    "icon": "fa-code",
                    "topics": ["Python Functions & File Handling", "Data Structures (Stack, Queue)", "Relational Database SQL", "Computer Networks"]
                }
            ]
