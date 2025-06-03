from flask import Flask, request, render_template
import difflib
import pylint.lint
from io import StringIO
import sys
import ast
import tempfile
import os

app = Flask(__name__)


# Функція для генерації пояснень
def explain_topic(topic):
    explanations = {
        "bubble sort": "Bubble Sort is a simple sorting algorithm that repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order. It has a time complexity of O(n^2).",
        "binary search": "Binary Search is an efficient algorithm for finding an element in a sorted array. It works by repeatedly dividing the search interval in half, with a time complexity of O(log n).",
        "linked list": "A Linked List is a linear data structure where elements are stored in nodes, each containing a value and a reference to the next node. It allows dynamic memory allocation and efficient insertions/deletions.",
        "fibonacci sequence": "The Fibonacci Sequence is a series of numbers where each number is the sum of the two preceding ones, usually starting with 0 and 1. It can be implemented iteratively or recursively."
    }
    return explanations.get(topic.lower(), "Topic not found. Please try another.")


# Функція для генерації коду
def generate_code(topic):
    code_samples = {
        "bubble sort": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
""",
        "binary search": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
        "linked list": """
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
""",
        "fibonacci sequence": """
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
"""
    }
    return code_samples.get(topic.lower(), "# Code sample not available")


# Функція для перевірки на плагіат
def check_plagiarism(code):
    reference_code = generate_code("bubble sort")  # Використовуємо bubble sort як приклад шаблону
    similarity = difflib.SequenceMatcher(None, code, reference_code).ratio()
    return f"Similarity score: {similarity * 100:.2f}%"


# Функція для аналізу помилок
def analyze_code(code):
    try:
        # Перевіряємо синтаксис коду
        ast.parse(code)
        # Якщо синтаксис коректний, створюємо тимчасовий файл для pylint
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            output = StringIO()
            sys.stdout = output
            # Запускаємо pylint на тимчасовий файл
            pylint.lint.Run([temp_file_path], exit=False)
            sys.stdout = sys.__stdout__
            result = output.getvalue() or "No errors found."
        finally:
            # Видаляємо тимчасовий файл
            os.remove(temp_file_path)
        return result
    except SyntaxError as e:
        return f"Syntax Error: {str(e)}"
    except Exception as e:
        return f"Error during code analysis: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            topic = request.form.get("topic")
            code = request.form.get("code")
            if topic:
                explanation = explain_topic(topic)
                generated_code = generate_code(topic)
                return render_template("index.html", explanation=explanation, generated_code=generated_code)
            if code:
                plagiarism_result = check_plagiarism(code)
                errors = analyze_code(code)
                return render_template("index.html", plagiarism=plagiarism_result, errors=errors)
        return render_template("index.html")
    except Exception as e:
        return f"An error occurred: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)