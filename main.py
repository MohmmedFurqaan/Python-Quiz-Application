import csv
import random
import threading
import time


class Question:
    def __init__(self, category, sub_category, question, options, correct_answer):
        self.category = category
        self.sub_category = sub_category
        self.question = question
        self.options = options
        self.correct_answer = correct_answer.strip().upper()  # Ensuring the answer is in uppercase for comparison

    def check_correct(self, answer):
        return answer.strip().upper() == self.correct_answer

    def display_question(self, index):
        print(f"\nQuestion {index + 1}: {self.question}")
        for i, option in enumerate(self.options):
            print(f"{chr(65 + i)}. {option}")  # A, B, C, D


class QuizLoader:
    @staticmethod
    def load_questions(file_path):
        """Loads questions from a CSV file."""
        questions = []
        try:
            with open(file_path, mode="r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row
                for row in reader:
                    if len(row) < 8:  # Ensure the row has enough columns
                        print(f"Skipping invalid row: {row}")
                        continue
                    try:
                        # Create a Question object
                        question = Question(
                            category=row[0],
                            sub_category=row[1],
                            question=row[2],
                            options=row[3:7],  # Options are in columns 4 to 7
                            correct_answer=row[7]  # Correct answer is in column 8
                        )
                        questions.append(question)
                    except ValueError:
                        print(f"Skipping invalid row (conversion error): {row}")
        except FileNotFoundError:
            print("Error: The specified file was not found.")
        except csv.Error as e:
            print(f"CSV error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return questions


class Quiz:
    """Manages the quiz flow, including filtering and conducting the quiz."""

    def __init__(self, questions, time_limit=10):
        self.questions = questions
        self.time_limit = time_limit  # Time limit for each question
        self.time_expired = False  # Flag to check if time has expired

    def filter_questions(self, category, subcategory):
        """Filters questions by category and subcategory."""
        return [q for q in self.questions if q.category == category and q.sub_category == subcategory]

    def select_option(self, prompt, options):
        """Prompts the user to select an option from a list."""
        while True:
            print(prompt)
            for i, option in enumerate(options):
                print(f"{i + 1}. {option}")
            try:
                choice = int(input(f"Select an option (1-{len(options)}): "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def get_number_of_questions(self, max_number):
        """Prompts the user for the number of questions to ask."""
        while True:
            try:
                num_to_ask = int(input(f"How many questions would you like to be asked (1-{max_number})? "))
                if 1 <= num_to_ask <= max_number:
                    return num_to_ask
                else:
                    print(f"Please enter a number between 1 and {max_number}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def ask_question_with_timer(self, question, index):
        """Displays a question and checks the user's answer within a time limit."""
        self.time_expired = False

        def timer():
            """Timer thread that sets the flag when time runs out."""
            time.sleep(self.time_limit)
            self.time_expired = True
            print(f"\nTime's up! The correct answer was: {question.correct_answer}\n")

        # Start the timer
        threading.Thread(target=timer, daemon=True).start()

        # Display the question and get the user's answer
        question.display_question(index)
        while not self.time_expired:
            try:
                answer = input(f"Your answer (A, B, C, or D) [Time limit: {self.time_limit}s]: ").strip().upper()
                if self.time_expired:
                    return False
                if answer in ["A", "B", "C", "D"]:
                    if question.check_correct(answer):
                        print("Correct!\n")
                        return True
                    else:
                        print(f"Wrong! The correct answer was: {question.correct_answer}\n")
                        return False
                else:
                    print("Please enter a valid option (A, B, C, or D).")
            except ValueError:
                print("Invalid input. Please try again.")
        return False

    def conduct(self):
        """Conducts the quiz based on user choices and displays the final score."""
        if not self.questions:
            print("No questions available.")
            return

        # Step 1: Choose a category
        categories = list(set(q.category for q in self.questions))
        category = self.select_option("Available categories:", categories)

        # Step 2: Choose a subcategory
        subcategories = list(set(q.sub_category for q in self.questions if q.category == category))
        subcategory = self.select_option(f"Available subcategories for '{category}':", subcategories)

        # Step 3: Filter questions
        filtered_questions = self.filter_questions(category, subcategory)
        if not filtered_questions:
            print("No questions available for the selected category and subcategory.")
            return

        # Shuffle questions and determine the number of questions
        random.shuffle(filtered_questions)
        num_questions = len(filtered_questions)
        num_to_ask = self.get_number_of_questions(num_questions)

        # Step 4: Conduct the quiz
        print("\nStarting the quiz! Good luck!\n")
        score = 0
        for idx, question in enumerate(filtered_questions[:num_to_ask]):
            if self.ask_question_with_timer(question, idx):
                score += 1

        # Step 5: Display the final score
        print(f"\nQuiz completed! Your final score: {score}/{num_to_ask}")
        print("Thanks for playing!")


if __name__ == "__main__":
    FILE_PATH = "question.csv"
    questions = QuizLoader.load_questions(FILE_PATH)
    if questions:
        quiz = Quiz(questions, time_limit=15)  # Set a 15-second time limit per question
        quiz.conduct()
    else:
        print("No questions loaded. Exiting.")
