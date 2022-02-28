✈️ Scrape FlightRadar
How-To Guide: This web GUI scrapes the tables in FlightRadar and outputs them as a downloadable Excel file. Note that this tool uses Selenium, BeautifulSoup, and Chrome for web scraping. It is recommended to use this tool with a Google Chrome browser. Fill out the input fields, launch, wait for the scraping to finish, and finally click Download Result to save the outputs.

- Fleet or flights page: A link for fleets (e.g. https://www.flightradar24.com/data/airlines/2i-csb/fleet) or aircraft (e.g. https://www.flightradar24.com/data/aircraft/n881yv). This automatically scrapes tables for all aircraft that can be found on these pages. Other links with tables will likely work, but each tab in the output may no longer be grouped by aircraft.
- Load earlier: Number of times to click "Load Earlier" on the page to retrieve historical data. The earliest date saved will vary by aircraft by the distribution of dates in the table.

<img width="583" alt="screenshot" src="gui.png">