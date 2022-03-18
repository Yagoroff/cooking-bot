from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests
import re
import json
import os

CONST_URL = 'https://eda.ru'
CONST_RECIPES = "/recepty/"
CONST_PAGE = "?page="


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'lxml')


def get_data_about_dish(url):
    soup = get_soup(url)

    parse_ingredients = soup("span", itemprop='recipeIngredient')
    parse_count_ingredients = soup("span", class_='emotion-15im4d2')
    parse_cooking_instructions = soup("span", itemprop="text")
    ingredients = []

    for i in range(len(parse_ingredients)):
        ingredients.append([parse_ingredients[i].text.strip(), parse_count_ingredients[i].text.strip()])

    dish = {
        "name": soup.find(class_="emotion-gl52ge").text.strip().replace("\xa0", " "),
        "url": url,
        "count_ingredient": len(parse_ingredients),
        "ingredients": ingredients,
        "calories": soup.find('span', itemprop="calories").text.strip() if soup.find('span',
                                                                                     itemprop="calories") is not None else 0,
        "protein": soup.find('span', itemprop="proteinContent").text.strip() if soup.find('span',
                                                                                          itemprop="proteinContent") is not None else 0,
        "fat": soup.find('span', itemprop="fatContent").text.strip() if soup.find('span',
                                                                                  itemprop="fatContent") is not None else 0,
        "carbohydrate": soup.find('span', itemprop="carbohydrateContent").text.strip() if soup.find('span',
                                                                                                    itemprop="carbohydrateContent") is not None else 0,
        "cooking_instructions": [str(i + 1) + '.' + c.text.strip().replace("\xa0", " ").replace("­", "") for i, c in
                                 enumerate(parse_cooking_instructions)]
    }
    return dish


def get_dish_images(url):
    soup = get_soup(url)

    images = {
        "main_image": (img["src"] for img in soup.find('img', class_='emotion-1mzi351')) if soup.find('img', class_='emotion-1mzi351') is not None else 0,
        "gallery_images": (img["src"] for img in soup('img', class_='emotion-1sh0a0t')) if soup('img', class_='emotion-1sh0a0t') is not None else 0,
        "instruction_images": (img["src"] for img in soup('img', class_='emotion-1vbvoti')) if soup('img',class_='emotion-1sh0a0t') is not None else 0
    }

    return images


def parse_dishes(category, first_dish, last_dish, folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

    for index in range(first_dish, last_dish if last_dish <= len(category) else len(category)):
        dishes = []

        new_soup = get_soup(CONST_URL + CONST_RECIPES + category[index]["data-select-suggest-value"])
        number_recipes = int(re.findall(r'\d+', new_soup.find('span', class_="emotion-1ad0u8b").text.strip())[0])

        print(category[index].text.strip(), f"Найдено рецептов {number_recipes}", sep="; ")
        if not number_recipes:
            continue
        for page in range(1, number_recipes // 14 + 10):
            try:
                new_soup = get_soup(
                    CONST_URL + CONST_RECIPES + category[index]["data-select-suggest-value"] + CONST_PAGE + str(page))
            except:
                break

            name_dishes = new_soup('span', class_="emotion-1j2opmb")

            for i, name_dish in enumerate(name_dishes):
                dishes.append({"name": name_dish.text.strip(), "url": CONST_URL + name_dish.findParent()["href"]})

                print(index, category[index].text.strip(), i + (page - 1) * 14 + 1, name_dish.text.strip(), sep="; ")
                # print(CONST_URL + name_dish.findParent()["href"])

        with open(f'{folder}\\{category[index].text.strip()}.json', 'w+', encoding='utf-8') as json_file:
            json.dump(dishes, json_file, indent=4, ensure_ascii=False)
        json_file.close()


def main():
    soup = get_soup(CONST_URL)

    recipe_selection_categories = soup('ul', class_="select-suggest__result js-select-suggest__result")
    country = recipe_selection_categories[2]('li')
    category = recipe_selection_categories[0]('li')

    try:
        parse_dishes(country,44, len(country),"country_cuisine")
        parse_dishes(category, 1, len(category), "category_cuisine")
    except IndexError:
        print("index out of range")


if __name__ == "__main__":
    main()
