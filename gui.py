import streamlit as st
import json 
import requests

# Title
st.title("Passivebot's Facebook Marketplace Scraper")

# List of supported cities
supported_cities = [
    "New York", "Los Angeles", "Las Vegas", "Chicago", "Houston", "San Antonio",
    "Miami", "Orlando", "San Diego", "Arlington", "Baltimore", "Cincinnati", 
    "Denver", "Fort Worth", "Jacksonville", "Memphis", "Nashville", "Philadelphia", 
    "Portland", "San Jose", "Tucson", "Atlanta", "Boston", "Columbus", "Detroit", 
    "Honolulu", "Kansas City", "New Orleans", "Phoenix", "Seattle", "Washington DC", 
    "Milwaukee", "Sacramento", "Austin", "Charlotte", "Dallas", "El Paso", 
    "Indianapolis", "Louisville", "Minneapolis", "Oklahoma City", "Pittsburgh", 
    "San Francisco", "Tampa"
]

# User inputs
city = st.selectbox("City", supported_cities, 0)
query = st.text_input("Query", "Macbook Pro")
max_price = st.text_input("Max Price", "1000")

# Submit button
submit = st.button("Submit")

if submit:
    # Clean max_price
    max_price = max_price.replace(",", "")

    try:
        res = requests.get(
            f"http://127.0.0.1:8000/crawl_facebook_marketplace?city={city}&query={query}&max_price={max_price}"
        )
        st.write("Status code:", res.status_code)

        # Convert JSON
        results = res.json()
        st.write(f"Number of results: {len(results)}")

        # Display results
        for item in results:
            st.header(item["title"])
            st.image(item["image"], width=200)
            st.write(item["price"])
            st.write(item["location"])
            st.write(f"https://www.facebook.com{item['link']}")
            st.write("----")

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    except json.decoder.JSONDecodeError:
        st.error("Could not parse response from server.")