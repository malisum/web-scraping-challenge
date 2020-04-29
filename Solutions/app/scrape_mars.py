# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Import dependencies
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import time 
import re

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Scrape all Mars data
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def mars_scrape_all():

    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': 'chromedriver_win32/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    # browser = Browser("chrome", executable_path="chromedriver", headless=True)

    # Scrape Mars data:
    # Get Mars news
    mars_news_info = get_mars_news(browser)
    mars_news_title = mars_news_info[0]
    mars_news_paragraph = mars_news_info[1]
    # Get Mars featured image
    mars_featured_image = get_mars_featured_image(browser)
    # Get Mars hemisphere
    mars_hemispheres = get_mars_hemispheres(browser)  
    # Get Mars twitter 
    mars_twitter_weather = get_mars_twitter_weather(browser)
    # Get Mars facts table
    mars_facts = get_mars_facts()
    # Date modified (when last scrapped) 
    last_modified = dt.datetime.now()


    # Save the output Mars data to dictionary
    mars_data = {
        "news_title": mars_news_title,
        "news_paragraph": mars_news_paragraph,
        "featured_image": mars_featured_image,
        "hemispheres": mars_hemispheres,
        "weather": mars_twitter_weather,
        "facts": mars_facts,
        "last_modified": last_modified
    }

    # Stop browser
    browser.quit()

    # Return 
    return mars_data

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Get Mars news
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def get_mars_news(browser):


    # Intialize no error 
    error = False

    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Get list item 
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_summary = slide_elem.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        error = True

    # output None if error 
    if error == True:
        news_title = None
        news_summary = None

    # Return 
    return news_title, news_summary

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Mars Featured Image
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def get_mars_featured_image(browser):

    # Intialize no error 
    error = False

    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    # Find and click the full image button
    full_image_elem = browser.find_by_id("full_image")
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_elem = browser.find_link_by_partial_text("more info")
    more_info_elem.click()

    # Parse resulting html
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    # Find relative image url
    img = img_soup.select_one("figure.lede a img")

    try:
        img_url_rel = img.get("src")

    except:
        error = True

    if error == False:
        # Use the base url to create an absolute url
        img_url = f"https://www.jpl.nasa.gov{img_url_rel}"
    else:
        img_url = None


    # Return
    return img_url

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Mars hemispheres
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def get_mars_hemispheres(browser):

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    browser.visit(url)

    # Scrape the 4 url results in list
    
    # Initialize 
    hemisphere_image_urls = []
 
    for i in range(4):
        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()
        hemi_data = scrape_mars_hemisphere_data(browser.html)
        # Append hemisphere 
        hemisphere_image_urls.append(hemi_data)
        # navigate back to scrape again
        browser.back()

    return hemisphere_image_urls

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Mars twiiter weather 
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def get_mars_twitter_weather(browser):

    try:
        url = "https://twitter.com/marswxreport?lang=en"
        browser.visit(url)
        
        # Pause for 5 seconds to load
        time.sleep(5)

        html = browser.html
        weather_soup = BeautifulSoup(html, "html.parser")

        # The wetaher updates are stored under element 'span' and class = "css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0"
        # Use soup find to get the 1st found weather update

        # Note: Mars weather tweets are under the following tags in sequence: 
        # div class="css-1dbjc4n r-my5ep6 r-qklmqi r-1adg3ll"
        # article class="css-1dbjc4n r-1loqt21 r-1udh08x r-o7ynqc r-1j63xyz"
        # div class "css-1dbjc4n r-1j3t67a"
        # div class="css-1dbjc4n r-18u37iz r-thb0q2"
        # div class="css-1dbjc4n r-1iusvr4 r-16y2uox r-1777fci r-5f2r5o r-1mi0q7o"
        # div class="css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"
        # span class="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0"
        #
        # Just by using span results in other sections that are not weather tweets, but if searched by 
        # div class="css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0" 
        # followed by
        # span class="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0"
        # results in the last tweet about mars weather 

        mars_weather_div = weather_soup.find('div', class_="css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0")
        mars_weather_span = mars_weather_div.find('span', class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")
        mars_weather = mars_weather_span.text

    except:
        mars_weather = None

    # Return
    return mars_weather

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Scrape Mars Hemisphere Link  
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def scrape_mars_hemisphere_data(html_text):

    # HTML soup 
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # Get information
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")
    except:
        # Default to None
        title_elem = None
        sample_elem = None

    # Load to dictionary for output 
    hemisphere = {
        "title": title_elem,
        "img_url": sample_elem
    }

    # Return 
    return hemisphere

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Get Mars Facts  
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def get_mars_facts():
 
    # Load HTM pot Dataframe 
    try:
        mars_facts_df = pd.read_html("http://space-facts.com/mars/")[0]
    except:
        return None

    # Define columns and set index
    mars_facts_df.columns = ["description", "value"]
    mars_facts_df.set_index("description", inplace=True)

    # Convert dataframe to HTML and Return 
    return mars_facts_df.to_html(classes="table table-striped")

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# Main - Execute   
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------- #
if __name__ == "__main__":

    # If running as script, print scraped data
    print(mars_scrape_all())
