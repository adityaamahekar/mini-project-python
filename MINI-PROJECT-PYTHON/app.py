import csv
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

BASE = Path(__file__).resolve().parent
STUDENTS = BASE / 'students.csv'
HALLS = BASE / 'halls.csv'
ALLOCATIONS = BASE / 'allocations.csv'


def read_csv(path, fields):
    if not path.exists():
        return []
    with path.open('r', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class ExamSeatingApp:
    def __init__(self, root):
        self.root = root
        root.title('Smart Exam Seating Arrangement System')
        root.geometry('1000x650')
        root.minsize(780, 500)
        self.students = read_csv(STUDENTS, ['roll', 'name', 'department', 'division'])
        self.halls = read_csv(HALLS, ['hall', 'rows', 'columns'])
        self.allocations = read_csv(ALLOCATIONS, ['roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'])
        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        title = ttk.Label(self.root, text='Smart Exam Seating Arrangement System', font=('Arial', 18, 'bold'))
        title.pack(pady=12)
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill='both', expand=True, padx=12, pady=8)
        self.student_tab = ttk.Frame(self.tabs, padding=12)
        self.hall_tab = ttk.Frame(self.tabs, padding=12)
        self.seating_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.student_tab, text='Students')
        self.tabs.add(self.hall_tab, text='Exam Halls')
        self.tabs.add(self.seating_tab, text='Seat Allocation')
        self.make_students_tab()
        self.make_halls_tab()
        self.make_seating_tab()

    def make_table(self, parent, columns):
        holder = ttk.Frame(parent)
        holder.pack(fill='both', expand=True, pady=10)
        tree = ttk.Treeview(holder, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, width=110, anchor='center')
        scrollbar = ttk.Scrollbar(holder, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        return tree

    def make_students_tab(self):
        form = ttk.Frame(self.student_tab)
        form.pack(fill='x')
        self.student_entries = {}
        for i, (key, label) in enumerate([('roll', 'Roll No'), ('name', 'Name'), ('department', 'Department'), ('division', 'Division')]):
            ttk.Label(form, text=label).grid(row=0, column=i, padx=5, sticky='w')
            entry = ttk.Entry(form, width=20)
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.student_entries[key] = entry
        buttons = ttk.Frame(self.student_tab)
        buttons.pack(fill='x', pady=4)
        ttk.Button(buttons, text='Add Student', command=self.add_student).pack(side='left', padx=4)
        ttk.Button(buttons, text='Delete Selected', command=self.delete_student).pack(side='left', padx=4)
        ttk.Button(buttons, text='Import Students CSV', command=self.import_students).pack(side='left', padx=4)
        self.student_tree = self.make_table(self.student_tab, ('roll', 'name', 'department', 'division'))

    def make_halls_tab(self):
        form = ttk.Frame(self.hall_tab)
        form.pack(fill='x')
        self.hall_entries = {}
        for i, (key, label) in enumerate([('hall', 'Hall Name'), ('rows', 'Rows'), ('columns', 'Columns')]):
            ttk.Label(form, text=label).grid(row=0, column=i, padx=5, sticky='w')
            entry = ttk.Entry(form, width=22)
            entry.grid(row=1, column=i, padx=5, pady=5)
            self.hall_entries[key] = entry
        buttons = ttk.Frame(self.hall_tab)
        buttons.pack(fill='x', pady=4)
        ttk.Button(buttons, text='Add Hall', command=self.add_hall).pack(side='left', padx=4)
        ttk.Button(buttons, text='Delete Selected', command=self.delete_hall).pack(side='left', padx=4)
        self.hall_tree = self.make_table(self.hall_tab, ('hall', 'rows', 'columns', 'capacity'))

    def make_seating_tab(self):
        actions = ttk.Frame(self.seating_tab)
        actions.pack(fill='x')
        ttk.Button(actions, text='Generate Seating', command=self.generate).pack(side='left', padx=4)
        ttk.Button(actions, text='Export CSV', command=self.export).pack(side='left', padx=4)
        ttk.Button(actions, text='Save PDF', command=self.save_pdf).pack(side='left', padx=4)
        ttk.Label(actions, text='Search Roll No:').pack(side='left', padx=(20, 4))
        self.search_entry = ttk.Entry(actions, width=15)
        self.search_entry.pack(side='left')
        ttk.Button(actions, text='Search', command=self.search).pack(side='left', padx=4)
        ttk.Button(actions, text='Show All', command=lambda: self.refresh_table(self.seat_tree, self.allocations, ('roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'))).pack(side='left', padx=4)
        self.status = ttk.Label(self.seating_tab, text='')
        self.status.pack(anchor='w', pady=6)
        self.seat_tree = self.make_table(self.seating_tab, ('roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'))

    def refresh_table(self, tree, data, keys):
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert('', 'end', values=[row.get(k, '') for k in keys])

    def refresh_all(self):
        self.refresh_table(self.student_tree, self.students, ('roll', 'name', 'department', 'division'))
        halls = [{**h, 'capacity': int(h['rows']) * int(h['columns'])} for h in self.halls]
        self.refresh_table(self.hall_tree, halls, ('hall', 'rows', 'columns', 'capacity'))
        self.refresh_table(self.seat_tree, self.allocations, ('roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'))
        self.status.config(text=f'Students: {len(self.students)}  |  Halls: {len(self.halls)}  |  Allocated: {len(self.allocations)}')

    def invalidate_allocations(self):
        self.allocations = []
        write_csv(ALLOCATIONS, ['roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'], [])

    def add_student(self):
        record = {k: e.get().strip() for k, e in self.student_entries.items()}
        if not all(record.values()):
            return messagebox.showerror('Missing Data', 'Please fill in all student fields.')
        if any(s['roll'] == record['roll'] for s in self.students):
            return messagebox.showerror('Duplicate', 'This roll number already exists.')
        self.students.append(record)
        write_csv(STUDENTS, ['roll', 'name', 'department', 'division'], self.students)
        self.invalidate_allocations()
        for entry in self.student_entries.values():
            entry.delete(0, 'end')
        self.refresh_all()

    def delete_student(self):
        selected = self.student_tree.selection()
        if not selected:
            return messagebox.showwarning('Select Student', 'Select a student first.')
        roll = self.student_tree.item(selected[0], 'values')[0]
        self.students = [s for s in self.students if s['roll'] != roll]
        write_csv(STUDENTS, ['roll', 'name', 'department', 'division'], self.students)
        self.invalidate_allocations()
        self.refresh_all()

    def import_students(self):
        filename = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if not filename:
            return
        try:
            with open(filename, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                if not {'roll', 'name', 'department', 'division'}.issubset(reader.fieldnames or []):
                    raise ValueError('CSV headers must be: roll,name,department,division')
                incoming = [{k: row[k].strip() for k in ('roll', 'name', 'department', 'division')} for row in reader]
            if any(not all(row.values()) for row in incoming):
                raise ValueError('CSV contains empty student fields.')
            existing = {s['roll'] for s in self.students}
            added = 0
            for row in incoming:
                if row['roll'] not in existing:
                    self.students.append(row)
                    existing.add(row['roll'])
                    added += 1
            write_csv(STUDENTS, ['roll', 'name', 'department', 'division'], self.students)
            if added:
                self.invalidate_allocations()
            self.refresh_all()
            messagebox.showinfo('Imported', f'Added {added} students.')
        except (OSError, ValueError, csv.Error) as error:
            messagebox.showerror('Import Failed', str(error))

    def add_hall(self):
        record = {k: e.get().strip() for k, e in self.hall_entries.items()}
        if not all(record.values()):
            return messagebox.showerror('Missing Data', 'Please fill in all hall fields.')
        try:
            rows, cols = int(record['rows']), int(record['columns'])
            if rows <= 0 or cols <= 0:
                raise ValueError
        except ValueError:
            return messagebox.showerror('Invalid Capacity', 'Rows and columns must be positive whole numbers.')
        if any(h['hall'].lower() == record['hall'].lower() for h in self.halls):
            return messagebox.showerror('Duplicate', 'This hall already exists.')
        self.halls.append(record)
        write_csv(HALLS, ['hall', 'rows', 'columns'], self.halls)
        self.invalidate_allocations()
        for entry in self.hall_entries.values():
            entry.delete(0, 'end')
        self.refresh_all()

    def delete_hall(self):
        selected = self.hall_tree.selection()
        if not selected:
            return messagebox.showwarning('Select Hall', 'Select a hall first.')
        name = self.hall_tree.item(selected[0], 'values')[0]
        self.halls = [h for h in self.halls if h['hall'] != name]
        write_csv(HALLS, ['hall', 'rows', 'columns'], self.halls)
        self.invalidate_allocations()
        self.refresh_all()

    def generate(self):
        if not self.students or not self.halls:
            return messagebox.showwarning('Missing Data', 'Add students and exam halls first.')
        capacity = sum(int(h['rows']) * int(h['columns']) for h in self.halls)
        if capacity < len(self.students):
            return messagebox.showerror('Not Enough Seats', f'Need {len(self.students)} seats, but only {capacity} available.')
        # Greedy allocation: favor a different department from neighboring seats.
        remaining = self.students[:]
        random.shuffle(remaining)
        allocations = []
        for hall in self.halls:
            cols = int(hall['columns'])
            rows = int(hall['rows'])
            last_row_departments = {}
            for r in range(1, rows + 1):
                current_row_departments = {}
                for c in range(1, cols + 1):
                    if not remaining:
                        break
                    neighbors = set()
                    if c - 1 in current_row_departments:
                        neighbors.add(current_row_departments[c - 1])
                    if c in last_row_departments:
                        neighbors.add(last_row_departments[c])
                    choice = next((i for i, s in enumerate(remaining) if s['department'] not in neighbors), 0)
                    student = remaining.pop(choice)
                    current_row_departments[c] = student['department']
                    allocations.append({**student, 'hall': hall['hall'], 'row': str(r), 'column': str(c), 'seat': f'R{r}-C{c}'})
                last_row_departments = current_row_departments
        self.allocations = allocations
        write_csv(ALLOCATIONS, ['roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'], self.allocations)
        self.refresh_all()
        messagebox.showinfo('Success', f'Seats allocated for {len(allocations)} students.\nDifferent departments are separated where possible.')

    def search(self):
        roll = self.search_entry.get().strip()
        results = [a for a in self.allocations if a['roll'] == roll]
        self.refresh_table(self.seat_tree, results, ('roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'))
        if not results:
            messagebox.showinfo('No Result', 'No allocated seat found for this roll number.')

    def export(self):
        if not self.allocations:
            return messagebox.showwarning('No Data', 'Generate seats first.')
        filename = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files', '*.csv')])
        if filename:
            write_csv(Path(filename), ['roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat'], self.allocations)
            messagebox.showinfo('Exported', 'CSV saved successfully.')

    def save_pdf(self):
        if not self.allocations:
            return messagebox.showwarning('No Data', 'Generate seats first.')
        try:
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.pagesizes import A4, landscape
        except ImportError:
            return messagebox.showerror('Missing Package', 'Install reportlab: pip install reportlab')
        filename = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF Files', '*.pdf')])
        if not filename:
            return
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            data = [['Roll No', 'Name', 'Department', 'Division', 'Hall', 'Row', 'Column', 'Seat']]
            data += [[a[k] for k in ('roll', 'name', 'department', 'division', 'hall', 'row', 'column', 'seat')] for a in self.allocations]
            table = Table(data, repeatRows=1, colWidths=[65, 125, 110, 65, 75, 55, 60, 65])
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DDE8F5')), ('GRID', (0, 0), (-1, -1), .4, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTSIZE', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            doc.build([Paragraph('Exam Seating Arrangement', styles['Title']), Spacer(1, 12), table])
            messagebox.showinfo('Saved', 'PDF report created successfully.')
        except Exception as error:
            messagebox.showerror('PDF Error', str(error))


if __name__ == '__main__':
    root = tk.Tk()
    ExamSeatingApp(root)
    root.mainloop()
