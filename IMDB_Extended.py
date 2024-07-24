from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time
from PyMovieDb import IMDB


# Joy Albertini

class IMDB_Extended(IMDB):

    def __init__(self, show_chrome):
        super().__init__()  # Initialize the base class
        chrome_options = Options()
        if not show_chrome:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def fetch_reviews(self, title_id, verbose=True):
        if verbose:
            print(f"Fetching reviews for film {title_id}")
        url = f"https://www.imdb.com/title/{title_id}/reviews?ref_=tt_urv"
        self.driver.get(url)
        all_reviews = []

        while True:
            try:
                load_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'load-more-trigger'))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(0.1)
                self.driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(0.5)
            except TimeoutException:
                # Correct behaviour for now
                #self.driver.save_screenshot("debug_timeout.png")
                break
            except NoSuchElementException:
                print("No more Load More button to click")
                #self.driver.save_screenshot("debug_no_element.png")
                break
            except ElementClickInterceptedException:
                print("Button is not clickable")
                #self.driver.save_screenshot("debug_not_clickable.png")
                break

        reviews = self.driver.find_elements(By.CLASS_NAME, "imdb-user-review")
        if not reviews:
            if verbose:
                print("No reviews found")
            self.driver.quit()
            return all_reviews

        for review in reviews:
            review_title = review.find_element(By.CLASS_NAME, "title").text.strip() if review.find_elements(
                By.CLASS_NAME, "title") else None
            review_body = review.find_element(By.CLASS_NAME,
                                              "text.show-more__control").text.strip() if review.find_elements(
                By.CLASS_NAME, "text.show-more__control") else None
            rating_elements = review.find_elements(By.CLASS_NAME, "rating-other-user-rating")
            rating = rating_elements[0].text.strip() if rating_elements else None
            name = review.find_element(By.CLASS_NAME, "display-name-link").text.strip() if review.find_elements(
                By.CLASS_NAME, "display-name-link") else None
            review_date = review.find_element(By.CLASS_NAME, "review-date").text.strip() if review.find_elements(
                By.CLASS_NAME, "review-date") else None

            all_reviews.append({
                "review_title": review_title,
                "review_body": review_body,
                "rating": rating,
                "reviewer_name": name,
                "review_date": review_date
            })

        self.driver.quit()
        return all_reviews


def testFunction():
    imdb_instance = IMDB_Extended(show_chrome=False)
    reviews = imdb_instance.fetch_reviews("tt10676048")
    print(len(reviews))
    for review in reviews:
        print(review)


if __name__ == "__main__":
    testFunction()
