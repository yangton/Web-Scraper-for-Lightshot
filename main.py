import os
import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup

def generate_sequential_string(length, current_string):
    characters = "abcdefghijklmnopqrstuvwxyz0123456789"
    if current_string == "":
        return "aaaaaa"
    else:
        index = len(current_string) - 1
        while index >= 0:
            if current_string[index] == '9':
                current_string = current_string[:index] + 'a' + current_string[index + 1:]
                index -= 1
            elif current_string[index] == 'z':
                current_string = current_string[:index] + '0' + current_string[index + 1:]
                index -= 1
            else:
                if current_string[index].isdigit():
                    current_string = current_string[:index] + characters[characters.index(current_string[index]) + 1] + current_string[index + 1:]
                else:
                    current_string = current_string[:index] + characters[characters.index(current_string[index]) + 1]
                break
        return current_string

async def get_web_content_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def process_content_async(url, folder_path, json_path, downloaded_count, current_string):
    content = await get_web_content_async(url)
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img')
    div_tags = soup.find_all('div', class_="uploader__browse_button")
    if img_tags:
        save_to_json(url, json_path, "alive", downloaded_count)
        for img_tag in img_tags:
            if img_tag.has_attr('src') and "https://prnt.sc/" in img_tag['src']:
                img_src = img_tag['src']
                save_image(img_src, folder_path, downloaded_count)
    elif div_tags:
        save_to_json(url, json_path, "empty_upload", downloaded_count)
    else:
        save_to_json(url, json_path, "empty_removed", downloaded_count)

async def main_async():
    base_url = "https://prnt.sc/"
    output_folder = "downloaded_images"
    json_file_path = "output.json"
    downloaded_count = [0]
    current_string = ""

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tasks = []
    while downloaded_count[0] < 10:
        current_string = generate_sequential_string(6, current_string)
        for i in range(10):
            new_string = current_string + str(i)
            url = base_url + new_string
            tasks.append(process_content_async(url, output_folder, json_file_path, downloaded_count, new_string))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main_async())
