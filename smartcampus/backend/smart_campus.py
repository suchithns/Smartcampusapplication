import os
import json
import numpy as np
import pandas as pd

class InvalidDirectoryError(Exception): pass
class EmptyDirectoryError(Exception): pass

class SmartCampusSystem:
    def __init__(self):
        self.student_records = {}  # {id: {"name": str, "age": int, "grades": dict}}
        self.courses = {}          # {course_name: credits}
        self.student_ids = []
        
        self.records_file = "academic_records.txt"
        self.analytics_file = "student_performance.csv"
        self._seed_analytics_data()
        self.load_records_from_file()

    def evaluate_grade(self, score):
        if score >= 90: return "A", "Excellent"
        elif score >= 80: return "B", "Very Good"
        elif score >= 70: return "C", "Good"
        elif score >= 60: return "D", "Average"
        else: return "F", "Needs Improvement"

    def register_student_backend(self, student_id, name, age, score):
        if student_id in self.student_records:
            return False, "Student ID already exists."
        
        grade, remark = self.evaluate_grade(score)
        self.student_records[student_id] = {
            "name": name,
            "age": age,
            "grades": {"Exam Score": score, "Grade": grade, "Remark": remark}
        }
        if student_id not in self.student_ids:
            self.student_ids.append(student_id)
        self.save_records_to_file()
        return True, f"Registered successfully! Grade: {grade}"

    def add_course_backend(self, course_name, credits):
        self.courses[course_name] = credits

    def binary_search(self, sorted_arr, x):
        low, high = 0, len(sorted_arr) - 1
        while low <= high:
            mid = (low + high) // 2
            if sorted_arr[mid] == x: return mid
            elif sorted_arr[mid] < x: low = mid + 1
            else: high = mid - 1
        return -1

    def calculate_total_fees(self, tuition, hostel=0.0, transportation=0.0):
        return tuition + hostel + transportation

    def save_records_to_file(self):
        with open(self.records_file, "w") as f:
            json.dump(self.student_records, f, indent=4)

    def load_records_from_file(self):
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, "r") as f:
                    self.student_records = json.load(f)
                    # Convert string keys from JSON back to integers
                    self.student_records = {int(k): v for k, v in self.student_records.items()}
                    self.student_ids = list(self.student_records.keys())
            except Exception:
                pass

    def scan_directory_backend(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            raise InvalidDirectoryError(f"The path '{path}' is not a valid directory.")
        contents = os.listdir(path)
        if not contents:
            raise EmptyDirectoryError("The target directory is empty.")
        return contents

    def _seed_analytics_data(self):
        if not os.path.exists(self.analytics_file):
            np.random.seed(42)
            data = {
                "StudentID": np.arange(1001, 1051),
                "Math_Score": np.random.randint(55, 100, size=50),
                "Science_Score": np.random.randint(60, 98, size=50),
                "English_Score": np.random.randint(65, 95, size=50),
                "Attendance_Rate": np.random.uniform(75, 100, size=50)
            }
            pd.DataFrame(data).to_csv(self.analytics_file, index=False)
