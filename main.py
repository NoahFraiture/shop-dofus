from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from pynput import keyboard
import scraping
import time


def write(word):
    keyboard = KeyboardController()
    for char in word:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(0.02)


def click(pos, mouse, left):
    mouse.position = pos
    mouse.press(left)
    mouse.release(left)

def search(word):
    delete = (546, 188)
    bar = (500, 188)
    item = (657, 220)
    mouse = MouseController()
    key = KeyboardController()
    left = Button.left

    click(delete, mouse, left)
    click(bar, mouse, left)
    write(word)
    key.press(keyboard.Key.enter)
    key.release(keyboard.Key.enter)
    time.sleep(0.7)
    click(item, mouse, left)


def listen():
    def on_press(key):
        global index, ignore
        ignore = False
        match key:
            case keyboard.Key.f5:
                pass
            case keyboard.Key.f7:
                index += 1
            case keyboard.Key.f6:
                index -= 1
            case keyboard.Key.f8:
                index = -1
                ignore = True
            case _:
                ignore = True
        return False

    # Collect events until released
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def shopping(ingredients):
    """
    :param ingredients: [(name, quantity), ...]
    """
    print("Commands :")
    print("f5 : stay")
    print("f6 : previous item")
    print("f7 : next item")
    print("f8 : end list")
    global index, ignore
    while index != -1:
        if index >= len(ingredients):
            print("End of the shopping list")
            return

        listen()
        if ignore: continue
        print(f"{ingredients[index][1]} : {ingredients[index][0]} -- {index}/{len(ingredients)}")
        search(ingredients[index][0])
    print("You ended the shopping list before it ends")

def command(crafts, instruction, name=None, quantity=0):
    match instruction:
        case "show":
            crafts.print_ingredients()
        case "develop":
            crafts.develop(name)
        case "add":
            crafts.add(name, quantity)
        case "remove":
            crafts.remove(name)
        case _:
            return 1
    return 0


def main():
    global index
    index = 0

    crafts = scraping.Crafts()
    print(f"Items to be crafted : {crafts.getIngredientList()}\n")
    crafts.print_ingredients()
    print("\nCommands :")
    print("add name quantity")
    print("remove name")
    print("show")
    print("-"*50)
    while True:
        instruction = input("input : ").split(" ")
        out = 0
        if len(instruction) == 1: out = command(crafts, instruction[0])
        if len(instruction) > 1: out = command(crafts, instruction[0], name=" ".join(instruction[1:-1]), quantity=int(instruction[-1]))
        if out:
            shopping(crafts.getIngredientList())


if __name__ == "__main__":
    main()
