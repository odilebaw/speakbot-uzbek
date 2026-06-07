"""
SpeakBot Uzbek - Test Script
Tests database operations to verify everything works correctly.
"""

import os
import sys
import sqlite3
from datetime import date

# Use a separate test database
TEST_DB = "test_speakbot.db"

# Override DATABASE_NAME before importing database module
import config
config.DATABASE_NAME = TEST_DB

from database import (
    create_tables, add_student, get_student, save_answer,
    get_student_stats, get_all_students, get_top_students,
    get_student_average_score, get_daily_challenge, save_daily_challenge,
    get_student_daily_answer, save_daily_answer, update_student_streak,
    get_student_streak,
)


def cleanup():
    """Remove test database file."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_database_connection():
    """Test that we can connect to the database."""
    conn = sqlite3.connect(TEST_DB)
    assert conn is not None, "Database connection failed"
    conn.close()
    print("  [+] Database connection works")


def test_tables_created():
    """Test that all tables are created successfully."""
    create_tables()
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "students" in tables, "students table not found"
    assert "answers" in tables, "answers table not found"
    assert "daily_challenges" in tables, "daily_challenges table not found"
    assert "daily_answers" in tables, "daily_answers table not found"
    print("  [+] All tables created successfully")


def test_add_student():
    """Test adding a student to the database."""
    add_student(123456789, "Test Student", "test_user")
    student = get_student(123456789)

    assert student is not None, "Student not found after adding"
    assert student["name"] == "Test Student", "Student name mismatch"
    assert student["username"] == "test_user", "Student username mismatch"
    assert student["telegram_id"] == 123456789, "Student telegram_id mismatch"
    print("  [+] Can add a test student")


def test_save_answer():
    """Test saving an answer to the database."""
    student = get_student(123456789)
    save_answer(student["id"], 1, "My name is Ali.", "BAHO: 4\nYAXSHI TOMONI: Yaxshi\nXATO: Xato yoq\nTO'G'RI JAVOB: My name is Ali.\nMASLAHAT: Davom eting!", 4)

    stats = get_student_stats(student["id"])
    assert stats["total_answers"] == 1, "Answer count should be 1"
    print("  [+] Can save a test answer")


def test_retrieve_stats():
    """Test retrieving student statistics."""
    student = get_student(123456789)
    stats = get_student_stats(student["id"])

    assert stats is not None, "Stats not found"
    assert stats["total_answers"] >= 1, "Total answers should be at least 1"
    assert stats["correct_answers"] >= 1, "Correct answers should be at least 1 (score was 4)"
    print("  [+] Can retrieve student stats")


def test_daily_challenge():
    """Test daily challenge operations."""
    today = date.today().isoformat()
    save_daily_challenge(today, "What is your name?", "Ismingiz nima?", "My name is Ali.", "family")

    challenge = get_daily_challenge(today)
    assert challenge is not None, "Daily challenge not found"
    assert challenge["english_question"] == "What is your name?", "Challenge question mismatch"
    print("  [+] Daily challenge save/retrieve works")


def test_daily_answer():
    """Test daily answer operations."""
    student = get_student(123456789)
    today = date.today().isoformat()

    save_daily_answer(student["id"], today, "My name is Test.", "BAHO: 5\nYAXSHI TOMONI: Ajoyib!\nXATO: Xato yoq\nTO'G'RI JAVOB: My name is Test.\nMASLAHAT: Zo'r!", 5)

    answer = get_student_daily_answer(student["id"], today)
    assert answer is not None, "Daily answer not found"
    assert answer["score"] == 5, "Daily answer score mismatch"
    print("  [+] Daily answer save/retrieve works")


def test_streak():
    """Test streak operations."""
    student = get_student(123456789)
    today = date.today().isoformat()

    update_student_streak(student["id"], 3, today)
    streak_info = get_student_streak(student["id"])

    assert streak_info is not None, "Streak info not found"
    assert streak_info["streak"] == 3, "Streak count mismatch"
    assert streak_info["last_daily_date"] == today, "Last daily date mismatch"
    print("  [+] Streak update/retrieve works")


def test_top_students():
    """Test top students query."""
    # Add another student with an answer
    add_student(987654321, "Second Student", "second_user")
    student2 = get_student(987654321)
    save_answer(student2["id"], 2, "I am 15 years old.", "BAHO: 5\nYAXSHI TOMONI: Mukammal!\nXATO: Xato yoq\nTO'G'RI JAVOB: I am 15 years old.\nMASLAHAT: Ajoyib!", 5)

    top = get_top_students(5)
    assert len(top) >= 1, "Top students should have at least 1 entry"
    print("  [+] Top students query works")


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("SpeakBot Uzbek - Test Script")
    print("=" * 50 + "\n")

    # Clean up any previous test database
    cleanup()

    try:
        print("Running tests...\n")

        test_database_connection()
        test_tables_created()
        test_add_student()
        test_save_answer()
        test_retrieve_stats()
        test_daily_challenge()
        test_daily_answer()
        test_streak()
        test_top_students()

        print("\n" + "=" * 50)
        print("\u2705 Barcha testlar muvaffaqiyatli!")
        print("=" * 50 + "\n")

    except AssertionError as e:
        print(f"\n\u274c Xato: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\u274c Xato: {e}")
        sys.exit(1)
    finally:
        # Clean up test database
        cleanup()


if __name__ == "__main__":
    main()
