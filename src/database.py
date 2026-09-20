import sqlite3
import pandas as pd


# ==========================================
# Initialize Database
# ==========================================
def init_db():
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            ats_score REAL,
            quality_score REAL,
            job_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# Save Resume Analysis
# ==========================================
def save_resume_analysis(filename, ats_score, quality_score, job_category):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO resume_history
        (filename, ats_score, quality_score, job_category)
        VALUES (?, ?, ?, ?)
    """,
        (filename, ats_score, quality_score, job_category),
    )

    conn.commit()
    conn.close()


# ==========================================
# Get Resume History
# ==========================================
def get_resume_history():
    conn = sqlite3.connect("resume_history.db")

    query = """
        SELECT filename, ats_score, quality_score,
               job_category, created_at
        FROM resume_history
        ORDER BY created_at DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df
