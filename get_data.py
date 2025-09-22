import requests
from bs4 import BeautifulSoup
import time
import csv


def get_phone_specifications(product_url):
    """
    Scrapes the specifications from a single product page's prodSpecs table.
    """
    print(f"--- Fetching specs from: {product_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        specifications = {}

        specs_table = soup.find("table", id="prodSpecs")
        if specs_table:
            spec_rows = specs_table.find_all("tr")

            for row in spec_rows:
                if row.find("td", class_="h"):
                    continue

                cells = row.find_all("td")
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)

                    if cells[1].find("img"):
                        img_alt = cells[1].find("img").get("alt", "").lower()
                        value = "Yes" if "checkmark" in img_alt else "No"
                    else:
                        value = cells[1].get_text(strip=True)

                    if key and value:
                        specifications[key] = value

            print("--- Scraped specifications from 'prodSpecs' table.")
            return specifications

        print("--- No 'prodSpecs' table found.")
        return {}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {product_url}: {e}")
        return {}


def main_scraper():
    """
    Main function to scrape all phones from all category pages and their specific specs.
    """
    # Use '&' instead of '#' to properly pass page numbers in the URL
    base_url = "https://www.multitronic.fi/phones-and-accessories/mobile-phones?page={page_number}"
    # You can loop through a range of pages you want to scrape, for example from 1 to 5
    start_page = 10
    end_page = 37
    all_phones_data = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    csv_headers = [
        "name",
        "brand",
        "model",
        "image url",
        "cost",
        "RAM capacity",
        "Internal storage capacity",
        "Display diagonal",
        "Processor cores",
        "Rear camera type",
        "Mobile network generation",
    ]

    for page_number in range(start_page, end_page + 1):
        url = base_url.format(page_number=page_number)

        print(f"\n--- Scraping Category Page {page_number} ---")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            phone_listings = soup.find_all("div", class_="item_wrapper listGridV3")

            if not phone_listings:
                print("No more phones found on this page. Exiting loop.")
                break

            for index, phone_item in enumerate(phone_listings):
                data_entry = phone_item.find("div", class_="productDataEntry")

                if data_entry:
                    name = data_entry.get("data-name", "N/A")
                    brand = data_entry.get("data-brand", "N/A")
                    price = data_entry.get("data-price", "N/A")

                    image_tag = phone_item.find("img", class_="img-responsive")
                    image_url = image_tag.get("src", "N/A") if image_tag else "N/A"

                    product_url_tag = phone_item.find("a", class_="pTitle")
                    if product_url_tag and "href" in product_url_tag.attrs:
                        relative_url = product_url_tag["href"]
                        full_product_url = "https://www.multitronic.fi" + relative_url
                    else:
                        full_product_url = "N/A"

                    phone_data = {
                        "name": name,
                        "brand": brand,
                        "image url": image_url,
                        "cost": price,
                    }

                    if full_product_url != "N/A":
                        specs = get_phone_specifications(full_product_url)

                        phone_data["model"] = specs.get("Original model name", "N/A")
                        phone_data["RAM capacity"] = specs.get("RAM capacity", "N/A")
                        phone_data["Internal storage capacity"] = specs.get(
                            "Internal storage capacity", "N/A"
                        )
                        phone_data["Display diagonal"] = specs.get(
                            "Display diagonal", "N/A"
                        )
                        phone_data["Processor cores"] = specs.get(
                            "Processor cores", "N/A"
                        )
                        phone_data["Rear camera type"] = specs.get(
                            "Rear camera type", "N/A"
                        )
                        phone_data["Mobile network generation"] = specs.get(
                            "Mobile network generation", "N/A"
                        )

                    all_phones_data.append(phone_data)

                    time.sleep(1)  # Delay between product pages

            time.sleep(3)  # Delay between category pages

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

    print("\n--- Scraping Complete ---")
    print(f"Total phones processed: {len(all_phones_data)}")

    output_file = "scraped_phones_summary.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        writer.writerows(all_phones_data)

    print(f"Data successfully saved to '{output_file}'.")


if __name__ == "__main__":
    main_scraper()
