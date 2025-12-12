import tkinter as tk
from tkinter import messagebox, ttk
import csv
import datetime
from turtle import RawTurtle, TurtleScreen



# BACKEND CLASSES


class Exercise:
    def __init__(self, name, weight, sets, reps):
        self.name = name
        self.weight = float(weight)
        self.sets = int(sets)
        self.reps = int(reps)


class WorkoutTracker:
    def __init__(self, filename="workouts.csv"):
        self.filename = filename

    def save_exercise(self, exercise):
        try:
            with open(self.filename, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.date.today(),
                    exercise.name,
                    exercise.weight,
                    exercise.sets,
                    exercise.reps
                ])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_history(self):
        data = []
        try:
            with open(self.filename, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            pass
        return data

    def get_progress(self, exercise_name):
        weights = []
        dates = []

        try:
            with open(self.filename, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    date, name, weight, sets, reps = row
                    if name.lower() == exercise_name.lower():
                        dates.append(date)
                        weights.append(float(weight))
        except FileNotFoundError:
            return [], []

        return dates, weights



# GUI


class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Progress Tracker")
        self.tracker = WorkoutTracker()

        tab_control = ttk.Notebook(root)

        self.tab_add = ttk.Frame(tab_control)
        self.tab_history = ttk.Frame(tab_control)
        self.tab_progress = ttk.Frame(tab_control)

        tab_control.add(self.tab_add, text="Add Workout")
        tab_control.add(self.tab_history, text="View History")
        tab_control.add(self.tab_progress, text="Progress")

        tab_control.pack(expand=1, fill="both")

        self.build_add_tab()
        self.build_history_tab()
        self.build_progress_tab()

    
    def build_add_tab(self):
        tk.Label(self.tab_add, text="Exercise Name").pack()
        self.name_entry = tk.Entry(self.tab_add)
        self.name_entry.pack()

        tk.Label(self.tab_add, text="Weight (lbs)").pack()
        self.weight_entry = tk.Entry(self.tab_add)
        self.weight_entry.pack()

        tk.Label(self.tab_add, text="Sets").pack()
        self.sets_entry = tk.Entry(self.tab_add)
        self.sets_entry.pack()

        tk.Label(self.tab_add, text="Reps").pack()
        self.reps_entry = tk.Entry(self.tab_add)
        self.reps_entry.pack()

        tk.Button(self.tab_add, text="Save Workout", command=self.save_workout).pack(pady=10)

    def save_workout(self):
        try:
            exercise = Exercise(
                self.name_entry.get(),
                self.weight_entry.get(),
                self.sets_entry.get(),
                self.reps_entry.get()
            )
            self.tracker.save_exercise(exercise)
            messagebox.showinfo("Saved", "Workout saved successfully!")
        except:
            messagebox.showerror("Error", "Invalid input")

 
    # History Tab
  
    def build_history_tab(self):
        self.history_box = tk.Text(self.tab_history, height=20, width=60)
        self.history_box.pack()

        tk.Button(self.tab_history, text="Load History", command=self.load_history).pack()

    def load_history(self):
        self.history_box.delete("1.0", tk.END)
        history = self.tracker.load_history()
        if not history:
            self.history_box.insert(tk.END, "No workout history found.")
            return
        for row in history:
            self.history_box.insert(tk.END, f"{row}\n")

 
    # Progress Tab

    def build_progress_tab(self):
        tk.Label(self.tab_progress, text="Select Exercise").pack()
        self.progress_exercise = ttk.Combobox(self.tab_progress, values=[], state="readonly")
        self.progress_exercise.pack(pady=5)

        tk.Button(self.tab_progress, text="Load Exercises", command=self.load_exercise_list).pack(pady=5)
        tk.Button(self.tab_progress, text="Show Progress", command=self.show_progress_graph).pack(pady=5)

        # Canvas for Turtle
        self.canvas = tk.Canvas(self.tab_progress, width=700, height=400)
        self.canvas.pack()
        self.screen = TurtleScreen(self.canvas)
        self.screen.bgcolor("white")
        self.turtle = RawTurtle(self.screen)
        self.turtle.speed(0)

    def load_exercise_list(self):
        history = self.tracker.load_history()
        names = sorted(list({row[1] for row in history}))
        self.progress_exercise["values"] = names

    def show_progress_graph(self):
        exercise_name = self.progress_exercise.get()
        if not exercise_name:
            messagebox.showwarning("Select Exercise", "Choose an exercise first")
            return

        dates, weights = self.tracker.get_progress(exercise_name)
        if not weights:
            messagebox.showinfo("No Data", f"No data found for {exercise_name}")
            return

        self.turtle.clear()

        # Graph settings
        x_start, y_start = -300, -150
        x_length, y_length = 600, 300
        max_weight = max(weights)
        scale_y = y_length / max_weight
        n_points = len(weights)
        x_step = x_length / (n_points - 1) if n_points > 1 else 1

        # Draw axes
        self.turtle.penup()
        self.turtle.goto(x_start, y_start)
        self.turtle.pendown()
        self.turtle.forward(x_length)  # X-axis
        self.turtle.penup()
        self.turtle.goto(x_start, y_start)
        self.turtle.pendown()
        self.turtle.left(90)
        self.turtle.forward(y_length)  # Y-axis
        self.turtle.right(90)
        self.turtle.penup()

        # Y-axis labels
        for i in range(6):
            y = y_start + i * (y_length / 5)
            label = round(i * max_weight / 5, 1)
            self.turtle.penup()
            self.turtle.goto(x_start - 40, y - 5)
            self.turtle.write(f"{label}", font=("Arial", 10, "normal"))

        # X-axis labels
        for i, date in enumerate(dates):
            x = x_start + i * x_step
            self.turtle.penup()
            self.turtle.goto(x - 20, y_start - 20)
            self.turtle.write(date, font=("Arial", 8, "normal"))

        # Plot points
        self.turtle.penup()
        for i, wt in enumerate(weights):
            x = x_start + i * x_step
            y = y_start + wt * scale_y
            if i == 0:
                self.turtle.goto(x, y)
                self.turtle.pendown()
            else:
                self.turtle.goto(x, y)
            # Write weight above point
            self.turtle.penup()
            self.turtle.goto(x - 10, y + 5)
            self.turtle.write(f"{wt}", font=("Arial", 8, "normal"))
            self.turtle.pendown()



# Run 

root = tk.Tk()
app = FitnessApp(root)
root.mainloop()
