import streamlit as st
from stqdm import stqdm

from seleniumrequests import Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import time
import pickle
import pandas as pd
from io import BytesIO
import re

def login(driver, cookies):
  for cookie in cookies:
    try:
      driver.add_cookie(cookie)
    except Exception as e:
      print(e)

def scrape_csvs(driver, url, load_earlier):
  driver.get(url)
  time.sleep(2)

  for _ in range(load_earlier):
    try:
      load = driver.find_element(By.ID, 'btn-load-earlier-flights').click()
      time.sleep(2)
    except:
      continue

  time.sleep(2)
  after = driver.page_source
  plane_info = driver.find_elements(By.XPATH, '(//div[@class="row section-header"])')[0].text
  
  infos = []
  soup = BeautifulSoup(after, "lxml")
  rows = soup.find_all('tr')
  for row in rows:
    try:
      cols = row.find_all('td')
      cols = [ele.text.strip() for ele in cols]
      row_info = {}
      mappings = {2: "date", 3: "from", 4: "to", 5: "flight", 6: "flight time", 7: "std", 8: "atd", 9: "sta", 11: "status"}
      for i, td in enumerate(cols):
        if i in mappings:
          row_info[mappings[i]] = td
      if len(row_info.keys()) == len(mappings.values()):
        infos.append(row_info)
    except:
      continue
  return plane_info, infos

def get_driver():
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = Chrome(ChromeDriverManager().install(), options=chrome_options)
  driver.get("https://www.flightradar24.com")
  return driver

def scrape(driver, links, load_earlier):
  metadata = {}
  for url in stqdm(links):
    try:
      plane_info, infos = scrape_csvs(driver, url, load_earlier)
      metadata[url] = {"plane_info": plane_info, "infos": infos}
    except Exception as e:
      print(e)
  return metadata

def save_metadata(metadata):
  dfs, planes = {}, []
  for k, v in metadata.items():
      planes.append({"id": k.split("/")[-1], "plane_info": v["plane_info"]})
  dfs["planes"] = pd.DataFrame(planes)
  for k, v in metadata.items():
      infos = v["infos"]
      df = pd.DataFrame(infos)
      name = k.split("/")[-1]
      dfs[name] = df

  output = BytesIO()
  writer = pd.ExcelWriter(output, engine='xlsxwriter')
  for sheet, frame in dfs.items(): 
    frame.to_excel(writer, sheet_name = sheet)
  writer.save()
  return output.getvalue()

def get_fleet(driver, fleet):
  driver.get(fleet)
  html = driver.page_source
  links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
  links = ["https://www.flightradar24.com" + link for link in links if "/data/aircraft" in link and link != "/data/aircraft"]
  return links

def show_streamlit():
  title = "Scrape FlightRadar"
  icon = "✈️"
  body = """
    **How-To Guide:**
    This web GUI scrapes the tables in FlightRadar and outputs them as a downloadable Excel file.
    Note that this tool uses Selenium, BeautifulSoup, and Chrome for web scraping.
    It is recommended to use this tool with a Google Chrome browser. 
    Fill out the input fields, launch, wait for the scraping to finish, and finally click Download Result to save the outputs.

    - Fleet or flights page: A link for fleets (e.g. https://www.flightradar24.com/data/airlines/2i-csb/fleet) or aircraft (e.g. https://www.flightradar24.com/data/aircraft/n881yv). This automatically scrapes tables for all aircraft that can be found on these pages. Other links with tables will likely work, but each tab in the output may no longer be grouped by aircraft.
    - Load earlier: Number of times to click "Load Earlier" on the page to retrieve historical data. The earliest date saved will vary by aircraft by the distribution of dates in the table.
  """

  st.set_page_config(page_title=title, page_icon=icon, layout="centered")
  st.title(icon + " " + title)
  st.markdown(body)

  if "data" not in st.session_state:
    st.session_state.data = None

  page = st.text_input("Fleet or aircraft page")
  load_earlier = st.number_input("Load earlier", min_value=0, max_value=50)
  cookies = st.file_uploader(
    "Upload Cookies", 
    type=["pkl"], 
    accept_multiple_files=False,
  )
  launch = st.button(
    label="Launch",
    disabled=page == ""
  )
  
  if launch:
    driver = get_driver()
    if page.split("/")[-1] == "fleet":
      links = get_fleet(driver, page)
    else:
      links = [page]

    if cookies:
      login(driver, pickle.load(cookies))

    metadata = scrape(driver, links, load_earlier=load_earlier)
    st.session_state.data = save_metadata(metadata)
    st.download_button("Download Result", data=st.session_state.data, file_name='flightradar.xlsx', disabled=st.session_state.data is None)

if __name__ == "__main__":
  show_streamlit()