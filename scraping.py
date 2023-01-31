from selenium import webdriver
import json
import subprocess

"""
Usage :
Create an instance of 'Crafts' class

Method :
develop(name_of_ingredient) : replace it by its component
add(name_of_wanted_item, quantity) : increase the wanted quantity of the item
remove(name) : remove item

"""


def getStorageJson():
    """
    get local storage of dofus.db and json it
    """
    subprocess.call("TASKKILL /f /IM chrome.exe")
    url = "https://dofusdb.fr/fr/tools/craft-manager"
    options = webdriver.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\Users\noahf\AppData\Local\Google\Chrome\User Data")
    driver = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\chromedriver\chromedriver.exe", chrome_options=options)
    driver.get(url)
    local_storage = driver.execute_script("return window.localStorage.getItem('dofusdb-local2');")
    return json.loads(local_storage)


def getItemsInfos(storage):
    """
    :param storage: json storage
    :return: [item object, ...]
    """

    def developRecipeItem(recipe: dict):
        """
        :param recipe: recipe of an item
        :return: list of object Item
        """
        l = []
        for i in range(len(recipe['quantities'])):
            ingredients = [] if 'recipe' not in recipe['ingredients'][i] else developRecipeItem(recipe['ingredients'][i]['recipe'])
            item = Item(
                recipe['ingredients'][i]['name']['fr'],
                recipe['quantities'][i],
                recipe['ingredients'][i]['level'],
                ingredients
            )
            l.append(item)
        return l


    items = []
    for itemJson in storage['crafts']['crafts']:
        itemObject = Item(
            itemJson['item']['name']['fr'],
            itemJson['quantity'],
            itemJson['item']['level'],
            developRecipeItem(itemJson['item']['recipe'])
        )
        items.append(itemObject)
    return items


def multiply(d, factor):
    return {key: val*factor for key, val in d.items()}


class Item:
    def __init__(self, name, quantity, level, recipe:list):
        self.name = name
        self.quantity = quantity
        self.level = level
        self.recipe = recipe # list of objects
        self.ingredients = self.calculateIngredients() # dic name : quantity

    def getName(self): return self.name
    def getQuantity(self): return self.quantity
    def getLevel(self): return self.level
    def getRecipe(self): return self.recipe
    def getIngredient(self): return self.ingredients

    def increase(self, quantity): self.quantity += quantity

    def resetIngredients(self):
        self.ingredients = self.calculateIngredients()

    def calculateIngredients(self):
        l = {}
        for item in self.getRecipe():
            l[item.getName()] = (l.get(item.getName(), 0) + item.getQuantity()) * self.getQuantity()
        return l

    def develop(self, item_name, developed):
        for item in self.getRecipe():
            if item.getName().lower() == item_name.lower():
                recipe = item.getRecipe()
                if len(recipe) == 0:
                    print("This item has no recipe, you can't develop it. Nothing happened")
                    return
                self.recipe += recipe
                self.recipe.remove(item)
                self.resetIngredients()
                for n in developed:
                    self.develop(n, [])
                return

    def __str__(self):
        return f"{self.getQuantity()} de {self.getName()}, level {self.getLevel()} se craft avec :\n {multiply(self.getIngredient(), self.getQuantity())}\n"


class Crafts:

    def __init__(self):
        self.json_file = getStorageJson()
        self.items = getItemsInfos(self.json_file) # list of objects
        self.ingredients = self.calculIngredients()
        self.developed = []

    def getItems(self): return self.items
    def getIngredients(self):
        """
        :return: dic of ingredients 'name':quantity
        """
        return self.ingredients
    def getIngredientList(self):
        """
        :return: ingredient in list format [(name, quantity), ...]
        """
        return list(self.ingredients.items())

    def calculIngredients(self):
        ing = {}
        for item in self.getItems():
            for ingredient in item.getIngredient():
                ing[ingredient] = item.getIngredient()[ingredient] + ing.get(ingredient, 0)
        return ing

    def resetIngredients(self):
        self.ingredients = self.calculIngredients()

    def develop(self, name):
        """"""
        """
        :param name: item we want to develop
        """
        for item in self.getItems():
            item.develop(name, self.developed)
        self.developed.append(name)
        self.resetIngredients()

    def add(self, name, quantity):
        for item in self.getItems():
            if item.getName().lower() == name.strip().lower():
                item.increase(quantity)
                if item.getQuantity() <= 0:
                    self.items.remove(item)
                item.resetIngredients()
                self.resetIngredients()
                return
        print("Item not in current list, we don't know its recipe. Nothing happened.")

    def remove(self, name):
        for item in self.getItems():
            if item.getName().lower() == name.strip().lower():
                self.items.remove(item)
                self.resetIngredients()
                return

    def print_ingredients(self):
        print("Total ingrédients :")
        print(self.getIngredients())

    def __str__(self):
        s = ""
        for item in self.getItems():
            s += "\n" + "-"*50 + "\n"
            s += item.__str__()
        return s


if __name__ == "__main__":
    a = Crafts()
    b = a.getItems()
    c = a.getIngredients()
    input()