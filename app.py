from flask import Flask, render_template, request, session, flash,redirect
from new_database import get_connection

app = Flask(__name__)
import os

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-key-change-before-deployment"
)

@app.route("/teacher-login", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return render_template(
                "teacher_login.html",
                error="Please enter username and password."
            )

        connection = get_connection()

        teacher = connection.execute(
            """
            SELECT teacher_id, name, username, password, subject
            FROM teachers
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        if teacher is None:
            return render_template(
                "teacher_login.html",
                error="Username not found."
            )

        if teacher["password"] != password:
            return render_template(
                "teacher_login.html",
                error="Incorrect password."
            )

        session.clear()

        session["role"] = "teacher"
        session["teacher_id"] = teacher["teacher_id"]
        session["teacher_name"] = teacher["name"]
        session["teacher_subject"] = teacher["subject"]

        return redirect("/teacher-dashboard")

    return render_template("teacher_login.html")

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        student_id = request.form["student_id"].strip()
        password = request.form["password"]

        if not student_id or not password:
            return render_template(
                "student_login.html",
                error="Please enter Student ID and password."
            )

        connection = get_connection()

        student = connection.execute(
            """
            SELECT student_id, name, password
            FROM students
            WHERE student_id = ?
            """,
            (student_id,)
        ).fetchone()

        connection.close()

        if student is None:
            return render_template(
                "student_login.html",
                error="Student ID not found."
            )

        if student["password"] != password:
            return render_template(
                "student_login.html",
                error="Incorrect password."
            )

        # Clear old role/session information
        session.clear()

        # Create student session
        session["role"] = "student"
        session["student_id"] = student["student_id"]
        session["student_name"] = student["name"]

        return redirect("/student-dashboard")

    return render_template("student_login.html")

@app.route("/student-dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect("/student-login")

    connection = get_connection()

    student_id = session["student_id"]

    # Total doubts
    total_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchone()["count"]

    # Unresolved doubts
    unresolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        AND status = 'Unresolved'
        """,
        (student_id,)
    ).fetchone()["count"]

    # Resolved doubts
    resolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        AND status = 'Resolved'
        """,
        (student_id,)
    ).fetchone()["count"]

    # Recent doubts
    recent_doubts = connection.execute(
        """
        SELECT *
        FROM doubts
        WHERE student_id = ?
        ORDER BY doubt_id DESC
        LIMIT 5
        """,
        (student_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "student_dashboard.html",
        student_name=session["student_name"],
        total_doubts=total_doubts,
        unresolved_doubts=unresolved_doubts,
        resolved_doubts=resolved_doubts,
        recent_doubts=recent_doubts
    )

@app.route("/")
def home():
    return render_template("role_selection.html")


@app.route("/submit-doubt", methods=["GET", "POST"])
def submit_doubt():

    # Only logged-in students can submit doubts
    if session.get("role") != "student" or "student_id" not in session:
        return redirect("/student-login")

    if request.method == "POST":

        subject = request.form["subject"].strip()
        topic = request.form["topic"].strip()
        description = request.form["description"].strip()
        doubt_type = request.form["doubt_type"]
        difficulty = request.form["difficulty"]

        # Basic validation
        if not subject or not topic or not description:
            return render_template(
                "submit_doubt.html",
                error="Please fill in all required fields."
            )

        student_id = session["student_id"]

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO doubts
            (
                student_id,
                subject,
                topic,
                description,
                doubt_type,
                difficulty
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                subject,
                topic,
                description,
                doubt_type,
                difficulty
            )
        )

        connection.commit()
        connection.close()

        return redirect("/my-doubts")

    return render_template(
        "submit_doubt.html",
        student_name=session.get("student_name")
    )

@app.route("/my-doubts")
def my_doubts():

    if "student_id" not in session:
        return "Please submit a doubt first."

    connection = get_connection()

    doubts = connection.execute(
        """
        SELECT *
        FROM doubts
        WHERE student_id = ?
        ORDER BY doubt_id DESC
        """,
        (session["student_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "my_doubts.html",
        doubts=doubts
    )

# ==========================================
# 4. SEARCH DOUBTS
# ==========================================

@app.route("/search-doubts", methods=["GET", "POST"])
def search_doubts():

    doubts = []
    searched = False

    if request.method == "POST":

        search = request.form["search"]

        connection = get_connection()

        doubts = connection.execute(
            """
            SELECT * FROM doubts
            WHERE subject LIKE ?
            OR topic LIKE ?
            """,
            (
                "%" + search + "%",
                "%" + search + "%"
            )
        ).fetchall()

        connection.close()

        searched = True

    return render_template(
        "search_doubts.html",
        doubts=doubts,
        searched=searched
    )

# ==========================================
# 5. LEARNING RESOURCES
# ==========================================

@app.route("/resources")
def resources():

    connection = get_connection()

    resources = connection.execute(
        "SELECT * FROM resources"
    ).fetchall()

    connection.close()

    return render_template(
        "resources.html",
        resources=resources
    )

# ==========================================
# 6. DOUBT ANALYTICS
# ==========================================

@app.route("/analytics")
def analytics():

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    connection = get_connection()

    # Total doubts
    total_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        """,
        (teacher_subject,)
    ).fetchone()["count"]

    # Unresolved doubts
    unresolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        AND status = 'Unresolved'
        """,
        (teacher_subject,)
    ).fetchone()["count"]

    # Resolved doubts
    resolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        AND status = 'Resolved'
        """,
        (teacher_subject,)
    ).fetchone()["count"]

    # Most asked subject
    subject_result = connection.execute(
        """
        SELECT subject, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(subject)
        ORDER BY count DESC
        LIMIT 1
        """,
        (teacher_subject,)
    ).fetchone()

    if subject_result:
        most_asked_subject = subject_result["subject"]
    else:
        most_asked_subject = "No data yet"

    # Most common topic
    topic_result = connection.execute(
        """
        SELECT topic, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(topic)
        ORDER BY count DESC
        LIMIT 1
        """,
        (teacher_subject,)
    ).fetchone()

    if topic_result:
        most_common_topic = topic_result["topic"]
    else:
        most_common_topic = "No data yet"

    # Most common doubt type
    type_result = connection.execute(
        """
        SELECT doubt_type, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(doubt_type)
        ORDER BY count DESC
        LIMIT 1
        """,
        (teacher_subject,)
    ).fetchone()

    if type_result:
        most_common_type = type_result["doubt_type"]
    else:
        most_common_type = "No data yet"

    # Subject data
    subject_data = connection.execute(
        """
        SELECT subject, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(subject)
        """,
        (teacher_subject,)
    ).fetchall()

    # Difficulty data
    difficulty_data = connection.execute(
        """
        SELECT difficulty, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(difficulty)
        ORDER BY count DESC
        """,
        (teacher_subject,)
    ).fetchall()

    connection.close()

    return render_template(
        "analytics.html",
        teacher_name=session["teacher_name"],
        teacher_subject=teacher_subject,
        total_doubts=total_doubts,
        unresolved_doubts=unresolved_doubts,
        resolved_doubts=resolved_doubts,
        most_asked_subject=most_asked_subject,
        most_common_topic=most_common_topic,
        most_common_type=most_common_type,
        subject_data=subject_data,
        difficulty_data=difficulty_data
    )
# ==========================================
# 7. RECURRING DOUBTS
# ==========================================

# ==========================================
# RECURRING DOUBTS / DOUBT INTELLIGENCE
# ==========================================

@app.route("/recurring-doubts")
def recurring_doubts():

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    connection = get_connection()

    recurring_topics = connection.execute(
        """
        SELECT
            subject,
            topic,
            COUNT(*) AS doubt_count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(subject), LOWER(topic)
        HAVING COUNT(*) > 1
        ORDER BY doubt_count DESC
        """,
        (teacher_subject,)
    ).fetchall()

    connection.close()

    return render_template(
        "recurring_doubts.html",
        recurring_topics=recurring_topics,
        teacher_name=session["teacher_name"],
        teacher_subject=teacher_subject
    )
# ==========================================
# EDIT DOUBT
# ==========================================

@app.route("/edit-doubt/<int:doubt_id>", methods=["GET", "POST"])
def edit_doubt(doubt_id):

    if "student_id" not in session:
        return "Please submit a doubt first."

    connection = get_connection()

    student_id = session["student_id"]

    doubt = connection.execute(
        """
        SELECT *
        FROM doubts
        WHERE doubt_id = ?
        AND student_id = ?
        """,
        (doubt_id, student_id)
    ).fetchone()

    if doubt is None:
        connection.close()
        return "You are not allowed to edit this doubt."

    if request.method == "POST":

        subject = request.form["subject"].strip().title()
        topic = request.form["topic"].strip().title()
        description = request.form["description"].strip()
        doubt_type = request.form["doubt_type"]
        difficulty = request.form["difficulty"]

        connection.execute(
            """
            UPDATE doubts
            SET subject = ?,
                topic = ?,
                description = ?,
                doubt_type = ?,
                difficulty = ?
            WHERE doubt_id = ?
            AND student_id = ?
            """,
            (
                subject,
                topic,
                description,
                doubt_type,
                difficulty,
                doubt_id,
                student_id
            )
        )

        connection.commit()
        connection.close()

        flash("Doubt updated successfully!", "success")

        return redirect("/my-doubts")

    connection.close()

    return render_template("edit_doubt.html", doubt=doubt)

# ==========================================
# DELETE DOUBT
# ==========================================

@app.route("/delete-doubt/<int:doubt_id>", methods=["GET", "POST"])
def delete_doubt(doubt_id):

    if "student_id" not in session:
        return "Please submit a doubt first."

    connection = get_connection()

    student_id = session["student_id"]

    connection.execute(
        """
        DELETE FROM doubts
        WHERE doubt_id = ?
        AND student_id = ?
        """,
        (doubt_id, student_id)
    )

    connection.commit()
    connection.close()

    flash("Doubt deleted successfully!", "success")

    return redirect("/my-doubts")
# ==========================================
# RESOLVE DOUBT
# ==========================================

# ==========================================
# RESOLVE DOUBT - TEACHER ONLY
# ==========================================


@app.route("/similar-doubts/<int:doubt_id>")
def similar_doubts(doubt_id):
    if "student_id" not in session:
        return "Please submit a doubt first."
    connection = get_connection()

    # Get the selected doubt
    current_doubt = connection.execute(
        """
        SELECT *
        FROM doubts
        WHERE doubt_id = ?
        AND student_id = ?
        """,
        (doubt_id, session["student_id"])
    ).fetchone()

    if current_doubt is None:
        connection.close()
        return "You are not allowed to view similar doubts for this doubt."

    # Get all other doubts
    all_doubts = connection.execute(
        """
        SELECT * FROM doubts
        WHERE doubt_id != ?
        """,
        (doubt_id,)
    ).fetchall()

    connection.close()

    # Words that do not help determine the actual topic
    stopwords = {
        "how", "what", "why", "when", "where",
        "is", "are", "was", "were",
        "the", "a", "an",
        "to", "of", "in", "on", "for",
        "and", "or", "but",
        "do", "does", "did",
        "can", "could", "would", "should",
        "i", "we", "you", "my", "your",
        "it", "this", "that",
        "dont", "don't",
        "know", "understand",
        "understood", "learn", "learning",
        "work", "working",
        "want", "need", "help",
        "explain", "explanation",
        "problem", "problems"
    }

    # Convert text into meaningful words
    def get_words(text):

        import string

        text = text.lower()

        # Remove punctuation
        text = text.translate(
            str.maketrans("", "", string.punctuation)
        )

        words = text.split()

        meaningful_words = {
            word
            for word in words
            if word not in stopwords
        }

        return meaningful_words

    # Get the topic and description of current doubt
    current_topic = get_words(
        current_doubt["topic"]
    )

    current_description = get_words(
        current_doubt["description"]
    )

    # Combine topic + description
    current_words = (
        current_topic |
        current_description
    )

    similar = []

    for doubt in all_doubts:

        # Subjects must match
        # Example: DSA should not be compared with DBMS
        if current_doubt["subject"].lower() != doubt["subject"].lower():
            continue

        other_topic = get_words(
            doubt["topic"]
        )

        other_description = get_words(
            doubt["description"]
        )

        other_words = (
            other_topic |
            other_description
        )

        # Avoid division by zero
        if len(current_words) == 0 or len(other_words) == 0:
            continue

        # Find common meaningful words
        common_words = current_words.intersection(
            other_words
        )

        # Jaccard similarity
        union_words = current_words.union(
            other_words
        )

        similarity = (
            len(common_words) /
            len(union_words)
        ) * 100

        # Only display reasonably similar doubts
        if similarity >= 20:

            similar.append({
                "doubt": doubt,
                "similarity": round(similarity)
            })

    # Highest similarity first
    similar.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return render_template(
        "similar_doubts.html",
        current_doubt=current_doubt,
        similar_doubts=similar
    )

# ==========================================
# RECOMMENDED RESOURCES
# ==========================================

@app.route("/recommended-resources/<int:doubt_id>")
def recommended_resources(doubt_id):

    if "student_id" not in session:
        return "Please submit a doubt first."

    connection = get_connection()

    student_id = session["student_id"]

    # Get the selected doubt
    # Only if it belongs to the current student
    doubt = connection.execute(
        """
        SELECT *
        FROM doubts
        WHERE doubt_id = ?
        AND student_id = ?
        """,
        (doubt_id, student_id)
    ).fetchone()

    if doubt is None:
        connection.close()
        return "You are not allowed to view resources for this doubt."

    # Find resources matching the subject and topic
    resources = connection.execute(
        """
        SELECT DISTINCT
            subject,
            topic,
            resource_name,
            resource_type,
            resource_link
        FROM resources
        WHERE LOWER(subject) = LOWER(?)
        AND LOWER(topic) = LOWER(?)
        """,
        (
            doubt["subject"],
            doubt["topic"]
        )
    ).fetchall()

    connection.close()

    return render_template(
        "recommended_resources.html",
        doubt=doubt,
        resources=resources
    )

# ==========================================
# 10. MY PROGRESS
# ==========================================

@app.route("/my-progress")
def my_progress():

    # Check whether a student is selected
    if "student_id" not in session:
        return "Please submit a doubt first."

    connection = get_connection()

    student_id = session["student_id"]

    # Total doubts
    total_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        """,
        (student_id,)
    ).fetchone()["count"]


    # Resolved doubts
    resolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        AND status = 'Resolved'
        """,
        (student_id,)
    ).fetchone()["count"]


    # Unresolved doubts
    unresolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        AND status = 'Unresolved'
        """,
        (student_id,)
    ).fetchone()["count"]


    # Resolution percentage
    if total_doubts > 0:
        resolution_percentage = round(
            (resolved_doubts / total_doubts) * 100
        )
    else:
        resolution_percentage = 0


    # Most asked subject
    subject_result = connection.execute(
        """
        SELECT subject, COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        GROUP BY subject
        ORDER BY count DESC
        LIMIT 1
        """,
        (student_id,)
    ).fetchone()

    if subject_result:
        most_asked_subject = subject_result["subject"]
    else:
        most_asked_subject = "No data yet"


    # Most common topic
    topic_result = connection.execute(
        """
        SELECT topic, COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        GROUP BY topic
        ORDER BY count DESC
        LIMIT 1
        """,
        (student_id,)
    ).fetchone()

    if topic_result:
        most_common_topic = topic_result["topic"]
    else:
        most_common_topic = "No data yet"


    # Most common doubt type
    type_result = connection.execute(
        """
        SELECT doubt_type, COUNT(*) AS count
        FROM doubts
        WHERE student_id = ?
        GROUP BY doubt_type
        ORDER BY count DESC
        LIMIT 1
        """,
        (student_id,)
    ).fetchone()

    if type_result:
        most_common_type = type_result["doubt_type"]
    else:
        most_common_type = "No data yet"


    connection.close()


    return render_template(
        "my_progress.html",
        student_name=session["student_name"],
        total_doubts=total_doubts,
        resolved_doubts=resolved_doubts,
        unresolved_doubts=unresolved_doubts,
        resolution_percentage=resolution_percentage,
        most_asked_subject=most_asked_subject,
        most_common_topic=most_common_topic,
        most_common_type=most_common_type
    )

# ==========================================
# TEACHER DASHBOARD
# ==========================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    connection = get_connection()

    total_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        """,
        (teacher_subject,)
    ).fetchone()["count"]

    unresolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        AND status = 'Unresolved'
        """,
        (teacher_subject,)
    ).fetchone()["count"]

    resolved_doubts = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        AND status = 'Resolved'
        """,
        (teacher_subject,)
    ).fetchone()["count"]

    subject_result = connection.execute(
        """
        SELECT subject, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(subject)
        ORDER BY count DESC
        LIMIT 1
        """,
        (teacher_subject,)
    ).fetchone()

    if subject_result:
        most_asked_subject = subject_result["subject"]
    else:
        most_asked_subject = "No data yet"

    topic_result = connection.execute(
        """
        SELECT topic, COUNT(*) AS count
        FROM doubts
        WHERE LOWER(subject) = LOWER(?)
        GROUP BY LOWER(topic)
        ORDER BY count DESC
        LIMIT 1
        """,
        (teacher_subject,)
    ).fetchone()

    if topic_result:
        most_common_topic = topic_result["topic"]
    else:
        most_common_topic = "No data yet"

    connection.close()

    return render_template(
        "teacher_dashboard.html",
        teacher_name=session["teacher_name"],
        teacher_subject=teacher_subject,
        total_doubts=total_doubts,
        unresolved_doubts=unresolved_doubts,
        resolved_doubts=resolved_doubts,
        most_asked_subject=most_asked_subject,
        most_common_topic=most_common_topic
    )

@app.route("/teacher-logout")
def teacher_logout():

    session.clear()

    return redirect("/")
# ==========================================
# TEACHER - VIEW ALL DOUBTS
# ==========================================

@app.route("/teacher-doubts")
def teacher_doubts():

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    connection = get_connection()

    doubts = connection.execute(
        """
        SELECT
            doubts.*,
            students.name AS student_name
        FROM doubts
        JOIN students
        ON doubts.student_id = students.student_id
        WHERE LOWER(doubts.subject) = LOWER(?)
        ORDER BY doubts.doubt_id DESC
        """,
        (teacher_subject,)
    ).fetchall()

    connection.close()

    return render_template(
        "teacher_doubts.html",
        doubts=doubts,
        teacher_name=session["teacher_name"],
        teacher_subject=teacher_subject
    )

@app.route("/resolve-doubt/<int:doubt_id>", methods=["POST"])
def resolve_doubt(doubt_id):

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    connection = get_connection()

    connection.execute(
        """
        UPDATE doubts
        SET status = 'Resolved'
        WHERE doubt_id = ?
        """,
        (doubt_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/teacher-doubts")

@app.route("/manage-resources")
def manage_resources():

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    connection = get_connection()

    resources = connection.execute(
        """
        SELECT *
        FROM resources
        WHERE LOWER(subject) = LOWER(?)
        ORDER BY topic, resource_name
        """,
        (teacher_subject,)
    ).fetchall()

    connection.close()

    return render_template(
        "manage_resources.html",
        resources=resources,
        teacher_name=session["teacher_name"],
        teacher_subject=teacher_subject
    )

@app.route("/add-resource", methods=["GET", "POST"])
def add_resource():

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    if request.method == "POST":

        topic = request.form["topic"].strip()
        resource_name = request.form["resource_name"].strip()
        resource_type = request.form["resource_type"].strip()
        resource_link = request.form["resource_link"].strip()

        if not topic or not resource_name or not resource_type or not resource_link:
            return render_template(
                "add_resource.html",
                error="Please fill in all fields.",
                teacher_subject=teacher_subject
            )

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO resources
            (
                subject,
                topic,
                resource_name,
                resource_type,
                resource_link
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                teacher_subject,
                topic,
                resource_name,
                resource_type,
                resource_link
            )
        )

        connection.commit()
        connection.close()

        return redirect("/manage-resources")

    return render_template(
        "add_resource.html",
        teacher_subject=teacher_subject
    )

@app.route("/edit-resource/<int:resource_id>", methods=["GET", "POST"])
def edit_resource(resource_id):

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    connection = get_connection()

    teacher_subject = session["teacher_subject"]

    resource = connection.execute(
        """
        SELECT *
        FROM resources
        WHERE resource_id = ?
        AND LOWER(subject) = LOWER(?)
        """,
        (resource_id, teacher_subject)
    ).fetchone()

    if resource is None:
        connection.close()
        return redirect("/manage-resources")

    if request.method == "POST":

        subject = request.form["subject"].strip()
        topic = request.form["topic"].strip()
        resource_name = request.form["resource_name"].strip()
        resource_type = request.form["resource_type"].strip()
        resource_link = request.form["resource_link"].strip()

        if not subject or not topic or not resource_name or not resource_type or not resource_link:

            connection.close()

            return render_template(
                "edit_resource.html",
                resource=resource,
                error="Please fill in all fields."
            )

        connection.execute(
            """
            UPDATE resources
            SET
                topic = ?,
                resource_name = ?,
                resource_type = ?,
                resource_link = ?
            WHERE resource_id = ?
            AND LOWER(subject) = LOWER(?)
            """,
            (
                topic,
                resource_name,
                resource_type,
                resource_link,
                resource_id,
                teacher_subject
            )
        )

        connection.commit()
        connection.close()

        return redirect("/manage-resources")

    connection.close()

    return render_template(
        "edit_resource.html",
        resource=resource
    )

@app.route("/delete-resource/<int:resource_id>", methods=["POST"])
def delete_resource(resource_id):

    if session.get("role") != "teacher":
        return redirect("/teacher-login")

    teacher_subject = session["teacher_subject"]

    connection = get_connection()

    connection.execute(
        """
        DELETE FROM resources
        WHERE resource_id = ?
        AND LOWER(subject) = LOWER(?)
        """,
        (resource_id, teacher_subject)
    )

    connection.commit()
    connection.close()

    return redirect("/manage-resources")

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
