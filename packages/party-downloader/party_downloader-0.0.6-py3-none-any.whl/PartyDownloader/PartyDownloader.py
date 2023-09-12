import requests
import time
from tqdm import tqdm
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import threading
from random import choice


def run_in_parallel(function, args, max_workers=5, sleep_time=.5):
    def function_wrapper(result_index, *args_wrapper):
        results[result_index] = function(*args_wrapper)

    results = [None] * len(args)
    threads = [None] * max_workers
    res_index = 0
    while len(args) > 0:
        for i, thread in enumerate(threads):
            if thread is None or not thread.is_alive():
                if len(args) > 0:
                    args_i = args.pop(0)
                    threads[i] = threading.Thread(target=function_wrapper, args=(res_index, *args_i))
                    threads[i].start()
                    res_index += 1
                else:
                    break
        time.sleep(sleep_time)
    for i, thread in enumerate(threads):
        if thread is not None:
            thread.join()
    return results


class PartyDownloader:
    def __init__(self, progress_bar=True):
        self._display_progress_bar = progress_bar
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/87.0.4280.88 Safari/537.36"
            }
        )
        self._max_workers: int = 5  # Adjust this value as needed
        self._request_delay: float = .5  # Adjust this value as needed
        self._number_of_pages: int = 0
        self._links: list = []
        self._base_url: str = ""
        self._model: str = ""
        # create folder if downloads folder doesn't exist
        os.makedirs("downloads", exist_ok=True)
        # change directory to downloads folder
        os.chdir("downloads")

    def display_progress_bar(self, value: bool):
        self._display_progress_bar = value

    def _get_number_of_pages(self):
        errs = 0
        self._number_of_pages = 0
        while True:
            try:
                random_page = self._session.get(self._base_url)
                if random_page.status_code != 200:
                    raise Exception("Status code is not 200")
                random_page = BeautifulSoup(random_page.text, 'html.parser')
                if random_page.find("menu") is None:
                    self._number_of_pages = 1
                else:
                    self._number_of_pages = int(
                        random_page.find("menu").find_all("a")[-1].get("href").split("=")[1]) // 50 + 1
                break
            except:
                errs += 1
                if errs > 2:
                    print("Error getting number of pages")
                    break
                time.sleep(1)

    def _get_coomer_links(self, skip_scraping):
        if self._display_progress_bar:
            progress_bar = tqdm(total=self._number_of_pages, unit="page")

        def process_page(i):
            url = self._base_url + f"?o={i}"
            try:
                soup = BeautifulSoup(self._session.get(url, timeout=15).text, 'html.parser')
                page_links = []
                for art in soup.find_all("article"):
                    post_url = self._base_url + "/post/" + art.find("a").get("href").split("post/")[1]
                    post_soup = BeautifulSoup(self._session.get(post_url, timeout=15).text, 'html.parser')
                    for a in post_soup.find_all("a", {"class": "fileThumb"}):
                        page_links.append(a.get("href"))
                    for a in post_soup.find_all("a", {"class": "post__attachment-link"}):
                        page_links.append(a.get("href"))
                    time.sleep(.1)
                if self._display_progress_bar:
                    progress_bar.update(1)
                return page_links
            except requests.RequestException:
                return []

        links = []
        if not skip_scraping:
            links = run_in_parallel(process_page, [[i] for i in range(0, self._number_of_pages * 50, 50)],
                                    max_workers=self._max_workers, sleep_time=self._request_delay)
            links = [l for page_links in links for l in page_links]
            links = [urlparse(l) for l in links]

        if os.path.exists(f"{self._model}/.scraped"):
            with open(f"{self._model}/.scraped", "r") as f:
                old_links = f.read().split("\n")
            old_links = [urlparse(l) for l in old_links]
            links = list(set(links + old_links))
        with open(f"{self._model}/.scraped", "w") as f:
            f.write("\n".join([l.geturl() for l in links]))

        self._links = links

    def _download_links(self, times=0):
        failed = []

        def download_link(link, ts=0):
            content = None
            if not os.path.exists(os.path.join(self._model, link.path.split("/")[-1])):
                try:
                    response = self._session.get(link.geturl())
                    response.raise_for_status()
                    content = response.content
                except requests.RequestException as e:
                    # tqdm.write(f"Failed to download {link} due to {e}")
                    # print the error message and return None
                    if ts < 1:
                        time.sleep(self._request_delay)
                        return download_link(link, ts + 1)
                if content is not None:
                    with open(os.path.join(self._model, link.path.split("/")[-1]), 'wb') as f:
                        f.write(content)
            if self._display_progress_bar:
                progress_bar.update(1)

        # Filter out links that have already been downloaded
        download_queue = []
        for link in self._links:
            name = os.path.join(self._model, link.path.split("/")[-1])
            if not os.path.exists(name):
                download_queue.append(link)
        links = download_queue

        if self._display_progress_bar:
            progress_bar = tqdm(total=len(links), desc="Downloading files", unit="files", position=0)
        run_in_parallel(download_link, [[l] for l in links], max_workers=self._max_workers,
                        sleep_time=self._request_delay)

        if len(failed) > 0:
            if times < 1:
                print("Retrying failed downloads")
                return self._download_links(times + 1)
            tqdm.write(f"Failed to download {len(failed)} files")
        with open(f"{self._model}/.failed", "w") as f:
            f.write("\n".join([l.geturl() for l in failed]))

    def download_coomer_files(self, model, *, skip_scraping=False):
        full_path = get_model_url(model)
        if full_path is None:
            raise Exception("Model not found")
        print(f"Downloading {model}")
        os.makedirs(model, exist_ok=True)
        self._model = model

        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            }
        )
        if not skip_scraping:
            self._get_number_of_pages()
        self._get_coomer_links(skip_scraping)
        self._download_links()


def demo():
    model = input("Enter model name: ")
    skip_scraping = input("Skip scraping? (y/n): ").lower() == "y"
    party_downloader = PartyDownloader()
    party_downloader.download_coomer_files(model, skip_scraping=skip_scraping)


def json_to_url(model_json: dict) -> str:
    if model_json['service'] == 'onlyfans':
        return f"https://coomer.party/onlyfans/user/{model_json['name']}"
    elif model_json['service'] == 'fansly':
        return f"https://coomer.party/fansly/user/{model_json['id']}"


def get_model_url(model: str) -> str:
    r = requests.get("https://coomer.party/api/creators")
    model = model.lower()
    # sort by favorited
    rjson = sorted(r.json(), key=lambda k: k['favorited'], reverse=True)
    possible_models = []
    for i in rjson:
        if i["name"].lower() == model:
            return json_to_url(i)
        if i['name'].count(model) > 0:
            possible_models.append(i)
    if len(possible_models) == 0:
        return None
    if len(possible_models) == 1:
        return json_to_url(possible_models[0])
    print("Multiple models found")
    for i, m in enumerate(possible_models):
        print(f"{i + 1}: {m['name']}")
    while True:
        try:
            model = int(input("Enter model number: ")) - 1
            if model < 0 or model >= len(possible_models):
                raise ValueError
            break
        except ValueError:
            print("Invalid input")
    return json_to_url(possible_models[model])


def get_random_model_url():
    r = requests.get("https://coomer.party/api/creators")
    rjson = sorted(r.json(), key=lambda k: k['favorited'], reverse=True)
    # get the top 10000 models
    rjson = rjson[:10000]
    # pick a random model
    model = choice(rjson)
    return json_to_url(model)


if __name__ == "__main__":
    demo()
    # print(get_random_model_url())
