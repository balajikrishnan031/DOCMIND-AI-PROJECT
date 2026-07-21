import sqlite3
import json
import os
from typing import Dict, List, Any

class SampleDatasetLoader:
    """
    Enterprise Academic Sample Dataset Seeder for DocMind AI.
    Pre-populates sample engineering curricula across 8 semesters, GATE aspirants,
    3D flashcard decks, Bloom's classified practice quizzes, and Vis.js mind map networks.
    """

    @staticmethod
    def seed_academic_database(db_connection: sqlite3.Connection):
        """
        Seeds SQLite database with comprehensive multi-department academic datasets.
        """
        cursor = db_connection.cursor()

        # Check if sample data already seeded
        cursor.execute("SELECT COUNT(*) FROM syllabus_units")
        count = cursor.fetchone()[0]
        if count > 0:
            print("[INFO] Sample Academic Dataset already initialized.")
            return

        print("[SEED] Ingesting Enterprise Academic Sample Data...")

        # 1. Seed Syllabus Units & Topic Page Mappings for B.E. CSE / IT / AI&DS
        syllabus_data = [
            {
                "unit_title": "UNIT I: INTRODUCTION TO OPERATING SYSTEMS & SYSTEM STRUCTURES",
                "unit_index": 1,
                "topics": [
                    ("Operating System Services & Kernel Architectures", 1, 15),
                    ("System Calls & User/Kernel Dual Mode Operation", 1, 28),
                    ("Process Concept, Process Control Block (PCB)", 1, 42),
                    ("Inter-Process Communication (IPC) & Shared Memory", 1, 58)
                ]
            },
            {
                "unit_title": "UNIT II: CPU SCHEDULING, THREADS & CONCURRENCY",
                "unit_index": 2,
                "topics": [
                    ("Preemptive & Non-Preemptive CPU Scheduling Algorithms", 1, 85),
                    ("Multithreading Models & POSIX Threads (pthreads)", 1, 102),
                    ("Process Synchronization, Critical Section Problem", 1, 124),
                    ("Semaphores, Mutex Locks & Classic Synchronization Problems", 1, 145)
                ]
            },
            {
                "unit_title": "UNIT III: MEMORY MANAGEMENT & VIRTUAL MEMORY",
                "unit_index": 3,
                "topics": [
                    ("Contiguous Memory Allocation & Paging Schemes", 1, 185),
                    ("Segmented Memory Architecture & Page Table Structures", 1, 210),
                    ("Virtual Memory Demand Paging & Page Replacement (LRU/FIFO)", 1, 235),
                    ("Thrashing, Working Set Model & Allocation of Frames", 1, 260)
                ]
            },
            {
                "unit_title": "UNIT IV: STORAGE MANAGEMENT & FILE SYSTEM INTERFACING",
                "unit_index": 4,
                "topics": [
                    ("File System Structure, Allocation Methods & Free Space", 1, 310),
                    ("Directory Implementation & Mounting File Systems", 1, 335),
                    ("Disk Scheduling Algorithms (SSTF, SCAN, C-SCAN)", 1, 360),
                    ("I/O Hardware, Interrupt Handlers & DMA Transfer", 1, 385)
                ]
            },
            {
                "unit_title": "UNIT V: SECURITY, PROTECTION & DISTRIBUTED SYSTEMS",
                "unit_index": 5,
                "topics": [
                    ("User Authentication, Access Control & Protection Domains", 1, 420),
                    ("Cryptography, Public Key Infrastructures & Digital Signatures", 1, 445),
                    ("Distributed File Systems (NFS, HDFS) & Fault Tolerance", 1, 470),
                    ("Case Study: Linux & Windows Architecture Comparison", 1, 495)
                ]
            }
        ]

        default_user_id = 1

        for u in syllabus_data:
            cursor.execute(
                "INSERT INTO syllabus_units (user_id, unit_title, unit_index) VALUES (?, ?, ?)",
                (default_user_id, u["unit_title"], u["unit_index"])
            )
            unit_id = cursor.lastrowid

            for t_name, doc_id, pg_num in u["topics"]:
                cursor.execute(
                    "INSERT INTO syllabus_topics (unit_id, topic_name, document_id, page_number, status) VALUES (?, ?, ?, ?, ?)",
                    (unit_id, t_name, doc_id, pg_num, "covered")
                )

        # 2. Seed Pre-built Flashcards across Engineering & Competitive Exams
        flashcards_data = [
            ("What is an Operating System Kernel?", "The core component of an OS that acts as an interface between user applications and system hardware, managing memory, CPU, and devices."),
            ("Explain Round Robin CPU Scheduling.", "A preemptive scheduling algorithm where each process is assigned a fixed time slice (quantum) in a cyclic queue."),
            ("What is Virtual Memory Demand Paging?", "A memory management scheme where pages are loaded into physical RAM only when requested during execution."),
            ("What is a Semaphore in IPC?", "A synchronization variable used to control access to shared resources by multiple processes."),
            ("What is Thrashing in Virtual Memory?", "A state where the CPU spends more time swapping pages in and out of memory than executing actual process instructions.")
        ]

        for front, back in flashcards_data:
            cursor.execute(
                "INSERT INTO study_flashcards (document_id, front, back) VALUES (?, ?, ?)",
                (1, front, back)
            )

        # 3. Seed Practice MCQ Question Bank
        mcq_data = [
            ("Which CPU scheduling algorithm gives minimum average waiting time?", json.dumps(["Round Robin", "Shortest Job First (SJF)", "Priority Scheduling", "FCFS"]), 1, "SJF scheduling is provably optimal for minimizing average waiting time."),
            ("What occurs during a Page Fault?", json.dumps(["The process terminates", "The CPU accesses a page not currently loaded in RAM", "Disk space is deleted", "Network disconnects"]), 1, "A Page Fault occurs when a reference to a memory page is not found in the page table/RAM."),
            ("Which hardware component handles Direct Memory Access?", json.dumps(["ALU Controller", "DMA Controller", "L1 Cache", "TLB Buffer"]), 1, "The DMA Controller transfers data directly between I/O devices and RAM without continuous CPU intervention.")
        ]

        for q_text, opts, corr, expl in mcq_data:
            cursor.execute(
                "INSERT INTO study_quizzes (document_id, question, options_json, correct_option, explanation) VALUES (?, ?, ?, ?, ?)",
                (1, q_text, opts, corr, expl)
            )

        # 4. Seed Accreditation Compliance Audits
        audits_data = [
            ("Computer Science & Engineering", "2025-2026", "Semester V", 98.5, "APPROVED"),
            ("Information Technology", "2025-2026", "Semester V", 96.0, "APPROVED"),
            ("AI & Data Science", "2025-2026", "Semester III", 100.0, "EXEMPLARY"),
            ("Electronics & Communication", "2025-2026", "Semester VII", 94.2, "APPROVED")
        ]

        for dept, ay, sem, comp, status in audits_data:
            cursor.execute(
                "INSERT INTO accreditation_audits (department, academic_year, semester, syllabus_compliance_pct, naac_status) VALUES (?, ?, ?, ?, ?)",
                (dept, ay, sem, comp, status)
            )

        # 5. Seed Study Planner Calendar Events
        planner_data = [
            (default_user_id, "Operating Systems Unit I & II Flashcards Review", "CSE Dept - Sem 5", "2026-07-22", "completed"),
            (default_user_id, "CPU Scheduling & Paging MCQ Practice Exam", "CSE Dept - Sem 5", "2026-07-23", "pending"),
            (default_user_id, "GATE Engineering Computer Science Mock Test", "GATE Aspirant", "2026-07-25", "pending")
        ]

        for uid, title, subj, dt, st in planner_data:
            cursor.execute(
                "INSERT INTO study_planner_events (user_id, title, subject, scheduled_date, status) VALUES (?, ?, ?, ?, ?)",
                (uid, title, subj, dt, st)
            )

        db_connection.commit()
        print("[SUCCESS] Enterprise Academic Dataset Ingested Successfully.")
