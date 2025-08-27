import tkinter as tk
import random
from tkinter import messagebox


class NumberGuessingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Number Guessing Game")
        self.master.geometry("300x200")
        self.master.configure(bg="#f0f0f0")

        self.target_number = random.randint(1, 100)
        self.attempts = 0

        # Create widgets
        self.title_label = tk.Label(
            master,
            text="Guess a number between 1 and 100",
            bg="#f0f0f0",
            font=("Arial", 10, "bold")
        )

        self.guess_entry = tk.Entry(master, width=10, font=("Arial", 12))

        self.submit_button = tk.Button(
            master,
            text="Submit Guess",
            command=self.check_guess,
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED
        )

        self.hint_label = tk.Label(
            master,
            text="",
            bg="#f0f0f0",
            font=("Arial", 10)
        )

        self.attempts_label = tk.Label(
            master,
            text="Attempts: 0",
            bg="#f0f0f0",
            font=("Arial", 10)
        )

        self.new_game_button = tk.Button(
            master,
            text="New Game",
            command=self.new_game,
            bg="#2196F3",
            fg="white",
            relief=tk.RAISED
        )

        # Layout widgets
        self.title_label.pack(pady=10)
        self.guess_entry.pack(pady=5)
        self.submit_button.pack(pady=5)
        self.hint_label.pack(pady=5)
        self.attempts_label.pack(pady=5)
        self.new_game_button.pack(pady=5)

        # Bind Enter key to submit
        self.master.bind('<Return>', lambda event: self.check_guess())

    def check_guess(self):
        try:
            guess = int(self.guess_entry.get())
            self.attempts += 1
            self.attempts_label.config(text=f"Attempts: {self.attempts}")

            if guess < 1 or guess > 100:
                self.hint_label.config(text="Please enter a number between 1 and 100")
            elif guess < self.target_number:
                self.hint_label.config(text="Too low! Try again.")
            elif guess > self.target_number:
                self.hint_label.config(text="Too high! Try again.")
            else:
                messagebox.showinfo("Congratulations!", f"You guessed it in {self.attempts} attempts!")
                self.new_game()

            self.guess_entry.delete(0, tk.END)
            self.guess_entry.focus()

        except ValueError:
            self.hint_label.config(text="Please enter a valid number")

    def new_game(self):
        self.target_number = random.randint(1, 100)
        self.attempts = 0
        self.attempts_label.config(text="Attempts: 0")
        self.hint_label.config(text="")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus()


if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()