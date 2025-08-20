import random

COLOURS = ["R", "G", "B", "Y", "W", "O"]

TRIES = 10
CODE_LENGTH = 4

def generate_code():
  code = []
  
  for _ in range(CODE_LENGTH):
    colour = random.choice(COLOURS)
    code.append(colour)
    
  return code

def guess_code():
  while True:
    guess = input("Guess: ").split(" ")
    
    if len(guess) != CODE_LENGTH:
      print(f"You have to guess {CODE_LENGTH} colours.")
      continue
    
    for colour in guess:
      if colour not in COLOURS:
        print(f"Invalid colour: {colour}. Try again")
        break
      
    else:
      break
    
  return guess

def check_code(guess, real_code):
  colour_counts = {}
  correct_pos = 0
  incorrect_pos = 0
  
  for colour in real_code:
    if colour not in colour_counts:
      colour_counts[colour] = 0
    colour_counts[colour] += 1
    
  for guess_colour, real_colour in zip(guess, real_code):
    if guess_colour == real_colour:
      correct_pos += 1
      colour_counts[guess_colour] -= 1
      
  for guess_colour, real_colour in zip(guess, real_code):
    if guess_colour in colour_counts and colour_counts[guess_colour] > 0:
      incorrect_pos += 1
      colour_counts[guess_colour] -= 1
      
  return correct_pos, incorrect_pos

def game():
  code = generate_code()
  for attempts in range(1, TRIES + 1):
    guess = guess_code()
    correct_pos, incorrect_pos = check_code(guess, code)
    
    if correct_pos == CODE_LENGTH:
      print(f"You guessed the code in {attempts} tries!")
      break
    
    print(f"Correct positions: {correct_pos} | Incorrect positions: {incorrect_pos}")
    
  else:
    print(f"You run out of tries, the code was: {code}")
    
if __name__ == "__main__":
  game()
    