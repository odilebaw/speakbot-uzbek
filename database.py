import sqlite3
from datetime import datetime, date

from config import DATABASE_NAME


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Create the students and answers tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT,
            username TEXT,
            joined_date TEXT NOT NULL,
            total_answers INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            student_answer TEXT,
            ai_feedback TEXT,
            score INTEGER,
            answered_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            english_question TEXT NOT NULL,
            uzbek_translation TEXT NOT NULL,
            example_answer TEXT NOT NULL,
            topic TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            challenge_date TEXT NOT NULL,
            student_answer TEXT,
            ai_feedback TEXT,
            score INTEGER,
            answered_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answered_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    # Add streak and last_daily_date columns to students table if not present
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN streak INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN last_daily_date TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def add_student(telegram_id, name, username):
    """Add a new student to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO students (telegram_id, name, username, joined_date)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, name, username, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_student(telegram_id):
    """Get a student by their Telegram ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE telegram_id = ?", (telegram_id,))
    student = cursor.fetchone()

    conn.close()
    return student


def save_answer(student_id, question_id, student_answer, ai_feedback, score):
    """Save a student's answer to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO answers (student_id, question_id, student_answer, ai_feedback, score, answered_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, question_id, student_answer, ai_feedback, score, datetime.now().isoformat()))

    # Update student stats
    cursor.execute("""
        UPDATE students
        SET total_answers = total_answers + 1,
            correct_answers = correct_answers + (CASE WHEN ? >= 3 THEN 1 ELSE 0 END)
        WHERE id = ?
    """, (score, student_id))

    conn.commit()
    conn.close()


def get_student_stats(student_id):
    """Get statistics for a student."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT total_answers, correct_answers FROM students WHERE id = ?", (student_id,))
    stats = cursor.fetchone()

    conn.close()
    return stats


def get_all_students():
    """Get all registered students."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students ORDER BY joined_date DESC")
    students = cursor.fetchall()

    conn.close()
    return students


def get_top_students(limit=5):
    """Get top students by average score."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.username, s.total_answers,
               ROUND(AVG(a.score), 1) as avg_score
        FROM students s
        JOIN answers a ON s.id = a.student_id
        GROUP BY s.id
        HAVING s.total_answers > 0
        ORDER BY avg_score DESC
        LIMIT ?
    """, (limit,))
    students = cursor.fetchall()

    conn.close()
    return students


def get_today_answers_count():
    """Get the count of answers given today."""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) as count FROM answers
        WHERE answered_at LIKE ?
    """, (f"{today}%",))
    result = cursor.fetchone()

    conn.close()
    return result["count"] if result else 0


def get_total_answers_count():
    """Get the total count of all answers."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM answers")
    result = cursor.fetchone()

    conn.close()
    return result["count"] if result else 0


def get_average_score_all():
    """Get the average score of all students."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ROUND(AVG(score), 1) as avg_score FROM answers")
    result = cursor.fetchone()

    conn.close()
    return result["avg_score"] if result and result["avg_score"] else 0


def get_most_popular_topic():
    """Get the most popular topic based on answers."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question_id, COUNT(*) as count
        FROM answers
        GROUP BY question_id
        ORDER BY count DESC
        LIMIT 1
    """)
    result = cursor.fetchone()

    conn.close()
    return result


def get_all_student_telegram_ids():
    """Get all student telegram IDs for broadcasting."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT telegram_id FROM students")
    students = cursor.fetchall()

    conn.close()
    return [s["telegram_id"] for s in students]


def get_student_average_score(student_id):
    """Get the average score for a specific student."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ROUND(AVG(score), 1) as avg_score
        FROM answers
        WHERE student_id = ?
    """, (student_id,))
    result = cursor.fetchone()

    conn.close()
    return result["avg_score"] if result and result["avg_score"] else 0


# --- Daily Challenge Functions ---

def get_daily_challenge(challenge_date=None):
    """Get the daily challenge for a given date (defaults to today)."""
    if challenge_date is None:
        challenge_date = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM daily_challenges WHERE date = ?", (challenge_date,))
    challenge = cursor.fetchone()

    conn.close()
    return challenge


def save_daily_challenge(challenge_date, english_question, uzbek_translation, example_answer, topic=None):
    """Save a daily challenge to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO daily_challenges (date, english_question, uzbek_translation, example_answer, topic)
        VALUES (?, ?, ?, ?, ?)
    """, (challenge_date, english_question, uzbek_translation, example_answer, topic))

    conn.commit()
    conn.close()


def get_student_daily_answer(student_id, challenge_date=None):
    """Check if a student has already answered today's daily challenge."""
    if challenge_date is None:
        challenge_date = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM daily_answers
        WHERE student_id = ? AND challenge_date = ?
    """, (student_id, challenge_date))
    answer = cursor.fetchone()

    conn.close()
    return answer


def save_daily_answer(student_id, challenge_date, student_answer, ai_feedback, score):
    """Save a student's daily challenge answer."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO daily_answers (student_id, challenge_date, student_answer, ai_feedback, score, answered_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_id, challenge_date, student_answer, ai_feedback, score, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def update_student_streak(student_id, new_streak, challenge_date=None):
    """Update a student's streak and last daily date."""
    if challenge_date is None:
        challenge_date = date.today().isoformat()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET streak = ?, last_daily_date = ?
        WHERE id = ?
    """, (new_streak, challenge_date, student_id))

    conn.commit()
    conn.close()


def get_student_streak(student_id):
    """Get a student's current streak and last daily date."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT streak, last_daily_date FROM students WHERE id = ?", (student_id,))
    result = cursor.fetchone()

    conn.close()
    return result


# --- Student Questions Tracking ---

def get_answered_question_ids(student_id):
    """Returns list of question IDs student already answered."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT question_id FROM student_questions WHERE student_id = ?", (student_id,))
    results = cursor.fetchall()

    conn.close()
    return [row["question_id"] for row in results]


def mark_question_answered(student_id, question_id):
    """Marks question as answered by the student."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student_questions (student_id, question_id, answered_at)
        VALUES (?, ?, ?)
    """, (student_id, question_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def reset_student_questions(student_id):
    """Resets when all 150 questions are done."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM student_questions WHERE student_id = ?", (student_id,))

    conn.commit()
    conn.close()
