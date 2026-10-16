\# DoubtMap — Student Doubt Intelligence \& Learning Support System



DoubtMap is a web-based academic support application that helps students organize and track their academic doubts while allowing teachers to manage subject-specific questions, learning resources and recurring-topic analysis.



\## Overview



Students can submit doubts, review their submissions, edit or delete their own records, search for questions and access learning resources. Teachers can view doubts associated with their assigned subjects, mark questions as resolved, manage resources and review doubt analytics.



The project demonstrates how frontend technologies, Python backend logic and relational database operations work together in a web application.



\## Features



\### Student features

\- Student login and personalized dashboard

\- Submit academic doubts

\- View, edit and delete personal doubts

\- Search doubts

\- View similar or recurring doubts where supported

\- Access learning resources

\- Review doubt-related progress



\### Teacher features

\- Separate teacher accounts associated with subjects

\- Subject-specific dashboard and doubt listing

\- Mark doubts as resolved

\- Analytics for doubt counts, topics, types and difficulty levels

\- Identify recurring topics

\- Add, view, edit and delete learning resources



\## Technology Stack



\- \*\*Frontend:\*\* HTML, CSS, JavaScript

\- \*\*Backend:\*\* Python and Flask

\- \*\*Database:\*\* SQLite

\- \*\*Database access:\*\* Python `sqlite3` module and SQL

\- \*\*Templating:\*\* Jinja templates through Flask



\## Architecture



Browser interface → Flask backend → SQLite database



The frontend collects user input and displays information. Flask processes requests, applies application logic and executes database queries. SQLite stores application records.



\## Database Design



The application uses tables for:

\- `students` — student account information

\- `teachers` — teacher accounts and assigned subjects

\- `doubts` — academic questions and their status

\- `resources` — learning-resource details and links

\- `solutions` — solution records associated with doubts, where implemented



The doubts table associates each doubt with its student through `student\_id`. Primary keys identify records, and related key columns connect records across tables.



\## CRUD Operations



DoubtMap demonstrates the four basic database operations:



\- \*\*Create:\*\* Submit a doubt or add a resource

\- \*\*Read:\*\* View doubts, analytics and resources

\- \*\*Update:\*\* Edit a doubt or mark it as resolved

\- \*\*Delete:\*\* Remove a doubt or resource



\## Getting Started



\### Prerequisites

\- Python 3

\- pip

\- Git (optional if downloading the source as a ZIP)



\### Installation



1\. Clone or download this repository.

2\. Open a terminal in the project directory.

3\. Create a virtual environment:



&nbsp;  ```bash

&nbsp;  python -m venv .venv

&nbsp;  ```



4\. Activate it on Windows:



&nbsp;  ```bash

&nbsp;  .venv\\Scripts\\activate

&nbsp;  ```



5\. Install dependencies:



&nbsp;  ```bash

&nbsp;  pip install -r requirements.txt

&nbsp;  ```



6\. Configure the database using the project's database initialization procedure and sample data, if provided.

7\. Configure the required Flask session secret and any demo account credentials according to the local setup instructions.

8\. Start the application:



&nbsp;  ```bash

&nbsp;  python app.py

&nbsp;  ```



9\. Open the local address printed by Flask in your browser.



\## Database and Privacy



The real development database, student information, passwords, database backups and local secrets are not included in the public repository.



Use a clean demonstration database and test accounts when sharing or demonstrating the application. Do not publish real credentials or private records.



\## Limitations and Future Improvements



Potential improvements include secure password hashing, stronger input validation and security, expanded analytics, notifications, more advanced similarity detection and a mobile-friendly application experience.



\## Learning Outcomes



This project provided practical experience with frontend development, Flask routes, form handling, database connectivity, SQL queries, CRUD operations, authentication, sessions and data-driven summaries.



\## Author



\*\*Isha Sherj\*\*



Academic website development project — Integrated MCA.

