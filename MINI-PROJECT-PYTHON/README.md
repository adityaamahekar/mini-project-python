# Smart Exam Seating Arrangement System

Python desktop mini project using Tkinter and CSV (no database).

## Requirements
- Python 3.9 or later (Tkinter is included in most Windows Python installations)
- Optional for PDF export: `pip install -r requirements.txt`

## Run
1. Extract the ZIP.
2. Open the extracted folder in VS Code or Command Prompt.
3. Run: `python app.py`
4. Under **Students**, add students manually or import a CSV file.
5. Under **Exam Halls**, add hall name, number of rows and columns.
6. Under **Seat Allocation**, click **Generate Seating**.
7. Search by roll number, export CSV, or save PDF.

## CSV import format
Headers must be exactly: `roll,name,department,division`.
See `sample_students.csv`.

## Storage
The application creates `students.csv`, `halls.csv`, and `allocations.csv` in its folder as you use it. Changes to students or halls clear old allocations so you can regenerate them.

## Allocation algorithm
The system assigns each student one unique seat, filling halls in the order they were added. It tries to avoid assigning students from the same department directly beside or behind one another. Separation is best-effort, not guaranteed.
