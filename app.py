# Description: This file contains the code for Passivebot's Facebook Marketplace Scraper API.
# Date: 2024-01-24
# Author: Harminder Nijjar
# Version: 1.0.0.
# Usage: python app.py

# Import the necessary libraries.
# Playwright is used to crawl the Facebook Marketplace.
from playwright.sync_api import sync_playwright
# The os library is used to get the environment variables.
import os
# The time library is used to add a delay to the script.
import time
# The BeautifulSoup library is used to parse the HTML.
from bs4 import BeautifulSoup
# The FastAPI library is used to create the API.
from fastapi import HTTPException, FastAPI
# The JSON library is used to convert the data to JSON.
import json
# The uvicorn library is used to run the API.
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
                 
# Create an instance of the FastAPI class.
app = FastAPI()
# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Create a route to the root endpoint.
@app.get("/")
# Define a function to be executed when the endpoint is called.
def root():
    # Return a message.
    return {"message": "Welcome to Passivebot's Facebook Marketplace API. Documentation is currently being worked on along with the API. Some planned features currently in the pipeline are a ReactJS frontend, MongoDB database, and Google Authentication."}

    # TODO - Add documentation to the API.
    # TODO - Add a React frontend to the API.
    # TODO - Add a MongoDB database to the API.
    # TODO - Add Google Authentication to the React frontend.

@app.get("/crawl_facebook_marketplace")
# Define a function to be executed when the endpoint is called.
# Add a description to the function.
def crawl_facebook_marketplace(city: str, query: str, max_price: int):
    # Define dictionary of cities from the facebook marketplace directory for United States.
    # https://m.facebook.com/marketplace/directory/US/?_se_imp=0oey5sMRMSl7wluQZ
    # TODO - Add more cities to the dictionary.
    cities = {
        'New York': 'nyc',
        'Los Angeles': 'la',
        'Las Vegas': 'vegas',
        'Chicago': 'chicago',
        'Houston': 'houston',
        'San Antonio': 'sanantonio',
        'Miami': 'miami',
        'Orlando': 'orlando',
        'San Diego': 'sandiego',
        'Arlington': 'arlington',
        'Balitmore': 'baltimore',
        'Cincinnati': 'cincinnati',
        'Denver': 'denver',
        'Fort Worth': 'fortworth',
        'Jacksonville': 'jacksonville',
        'Memphis': 'memphis',
        'Nashville': 'nashville',
        'Philadelphia': 'philly',
        'Portland': 'portland',
        'San Jose': 'sanjose',
        'Tucson': 'tucson',
        'Atlanta': 'atlanta',
        'Boston': 'boston',
        'Columnbus': 'columbus',
        'Detroit': 'detroit',
        'Honolulu': 'honolulu',
        'Kansas City': 'kansascity',
        'New Orleans': 'neworleans',
        'Phoenix': 'phoenix',
        'Seattle': 'seattle',
        'Washington DC': 'dc',
        'Milwaukee': 'milwaukee',
        'Sacremento': 'sac',
        'Austin': 'austin',
        'Charlotte': 'charlotte',
        'Dallas': 'dallas',
        'El Paso': 'elpaso',
        'Indianapolis': 'indianapolis',
        'Louisville': 'louisville',
        'Minneapolis': 'minneapolis',
        'Oaklahoma City' : 'oklahoma',
        'Pittsburgh': 'pittsburgh',
        'San Francisco': 'sanfrancisco',
        'Tampa': 'tampa'
    }
    # If the city is in the cities dictionary...
    if city in cities:
        # Get the city location id from the cities dictionary.
        city = cities[city]
    # If the city is not in the cities dictionary...
    else:
        # Exit the script if the city is not in the cities dictionary.
        # Capitalize only the first letter of the city.
        city = city.capitalize()
        # Raise an HTTPException.
        raise HTTPException (404, f'{city} is not a city we are currently supporting on the Facebook Marketplace. Please reach out to us to add this city in our directory.')
        # TODO - Try and find a way to get city location ids from Facebook if the city is not in the cities dictionary.

    # Define the URL to scrape.
    marketplace_url = f'https://www.facebook.com/marketplace/{city}/search/?query={query}&maxPrice={max_price}'
    # Define the login URL (used only on first login).
    initial_url = "https://www.facebook.com/login/device-based/regular/login/"

    # Get listings of particular item in a particular city for a particular price.
    # Initialize the session using Playwright.
    with sync_playwright() as p:
        # Launch persistent context to reuse login session.
        user_data_dir = os.path.join(os.getcwd(), "playwright_profile")
        context = p.chromium.launch_persistent_context(user_data_dir=user_data_dir, headless=False)
        page = context.new_page()       

        #print("Launching browser...")
        #browser = p.chromium.launch(headless=False)
        #print("Creating page...")
        #page = browser.new_page()

        # Navigate to Facebook Marketplace homepage.
        print("Going to Facebook...")
        page.goto("https://www.facebook.com/marketplace")
        time.sleep(3)

        # --- Added: Pause for manual login if redirected to login page or popup detected ---
        if "login" in page.url or page.query_selector('form#login_popup_cta_form') is not None:
            print("🔐 Please log into Facebook in the opened browser window.")
            input("✅ After you finish logging in, press ENTER here to continue...")
        # --------------------------------------------------------------------------------------

        # Now navigate to the search results page.
        page.goto(marketplace_url)

        if page.url == "https://www.facebook.com/marketplace":
            print("Fallback: Performing search using UI...")
            try:
                search_input = page.wait_for_selector('input[placeholder="Search Marketplace"]', timeout=10000)
                search_input.fill(query)
                search_input.press("Enter")
                time.sleep(5)
            except Exception as e:
                print("Search input not found:", e)

        # Wait until at least one listing has appeared
        page.wait_for_selector("div.x9f619.x78zum5.x1r8uery.xdt5ytf", timeout=15000)  # wait up to 15 seconds

        # --- Added: Check for login popup again, pause if needed ---
        popup = page.query_selector('form#login_popup_cta_form')
        if popup is not None:
            print("🔐 Login popup detected! Please complete manual login.")
            input("✅ After logging in, press ENTER here to continue...")
        # --------------------------------------------------------------------------------------

        # Get the HTML content of the page.
        html = page.content()
        # Parse the HTML using BeautifulSoup.
        soup = BeautifulSoup(html, 'html.parser')
        parsed = []

        # Find all listing containers on the page.
        listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')
        for listing in listings:
            try:
                # Get the item image.
                image = listing.find('img', class_='xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3')['src']
                # Get the item title from span.
                title = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6').text
                # Get the item price.
                price = listing.find('span', 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u').text
                # Get the item URL.
                post_url = listing.find('a', class_='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv')['href']
                base_url = "https://www.facebook.com"
                post_url = base_url + post_url             
                # Get the item location.
                location = listing.find('span', 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84').text
                # Append the parsed data to the list.
                parsed.append({
                    'image': image,
                    'title': title,
                    'price': price,
                    'post_url': post_url,
                    'location': location
                })
            except:
                pass
        
        listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')
        print(f"Found {len(listings)} listings")


        # --- Added: Pause here before closing the browser so you can inspect or interact if needed ---
        print("Scraping done. Press ENTER to close the browser and exit.")
       # input()
        # --------------------------------------------------------------------------------------

        # Close the browser context (not the session data).
        context.close()

        # Return the parsed data as a JSON.
        result = []
        for item in parsed:
            try:
                result.append({
                    'name': item['title'],
                    'price': item['price'],
                    'location': item['location'],
                    'title': item['title'],
                    'image': item['image'],
                    #'link': "https://www.facebook.com" + item['post_url']
                    'link': item['post_url']
                })
            except Exception as e:
                print("Error building result:", e)

        if not result:
            raise HTTPException(404, "No valid listings were scraped.")

        # Ensure the result is serializable
        try:
            json.dumps(result)
        except Exception as e:
            raise HTTPException(500, f"Serialization error: {e}")

        return result



# Create a route to the return_html endpoint.
@app.get("/return_ip_information")
# Define a function to be executed when the endpoint is called.
def return_ip_information():
    # Initialize the session using Playwright.
    with sync_playwright() as p:
        # Open a new browser page.
        browser = p.chromium.launch()
        page = browser.new_page()
        # Navigate to the URL.
        page.goto('https://www.ipburger.com/')
        # Wait for the page to load.
        time.sleep(5)
        # Get the HTML content of the page.
        html = page.content()
        # Beautify the HTML content.
        soup = BeautifulSoup(html, 'html.parser')
        # Find the IP address.
        ip_address = soup.find('span', id='ipaddress1').text
        # Find the country.
        country = soup.find('strong', id='country_fullname').text
        # Find the location.
        location = soup.find('strong', id='location').text
        # Find the ISP.
        isp = soup.find('strong', id='isp').text
        # Find the Hostname.
        hostname = soup.find('strong', id='hostname').text
        # Find the Type.
        ip_type = soup.find('strong', id='ip_type').text
        # Find the version.
        version = soup.find('strong', id='version').text
        # Close the browser.
        browser.close()
        # Return the IP information as JSON.
        return {
            'ip_address': ip_address,
            'country': country,
            'location': location,
            'isp': isp,
            'hostname': hostname,
            'type': ip_type,
            'version': version
        }

if __name__ == "__main__":

    # Run the app.
    uvicorn.run(
        # Specify the app as the FastAPI app.
        'app:app',
        host='127.0.0.1',
        port=8000
    )
