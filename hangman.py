import random

# Word bank
WORD_BANK = ["horse", "python", "computer", "science", "programming", "hangman", "university", "keyboard"]

def choose_word():
    """Randomly selects a word from the word bank."""
    return random.choice(WORD_BANK)

def display_word(word, guessed_letters):
    """Returns the current display of the word with underscores for unguessed letters."""
    display = ""
    for letter in word:
        if letter in guessed_letters:
            display += letter + " "
        else:
            display += "_ "
    return display.strip()

def valid_guess(guess):
    """Checks if the user's guess is a single alphabetic character."""
    return len(guess) == 1 and guess.isalpha()

def play_game():
    """single game"""
    word = choose_word()
    guessed_letters = []
    lives = 6
    print("\nLet's play hangman!")
    print("Lives left:", lives)
    print(display_word(word, guessed_letters))

    while lives > 0:
        guess = input("Guess a letter: ").lower()

        # Bonus: Guess entire word
        if guess.startswith("guess "):
            full_guess = guess[6:].strip().lower()
            if full_guess == word:
                print(word)
                print("Word guessed, you've won!")
                return
            else:
                print("Incorrect guess. Game over!")
                return

        # Input validation
        if not valid_guess(guess):
            print("Not a valid guess. Please enter a single letter.")
            print("Lives left:", lives)
            continue

        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try a different letter.")
            print("Lives left:", lives)
            continue

        guessed_letters.append(guess)

        if guess in word:
            print(display_word(word, guessed_letters))
            if all(letter in guessed_letters for letter in word):
                print("Word guessed, you've won!")
                return
        else:
            lives -= 1
            print("Letter not found!")
            print(display_word(word, guessed_letters))
        print("Lives left:", lives)

    print("Out of lives, game over!")
    print("The word was:", word)

def main():
    """loop and replay"""
    while True:
        play_game()
        while True:
            replay = input("Play again? (yes/no): ").lower()
            if replay == "yes":
                break
            elif replay == "no":
                print("Thanks for playing!")
                return
            else:
                print("Invalid input. Play again? (yes/no)")

if __name__ == "__main__":
    main()
