# Mileage-Calculator
Script to calculate total mileage per day &amp; month using Google Maps API

## Prerequisites
* Install python3 on your device
  * https://realpython.com/installing-python/
* Install pip3 (python package manager) on your device
  * https://www.activestate.com/resources/quick-reads/how-to-install-and-use-pip3/
* Install python external libraries
  * Install pandas (Data Analysis library)
    * `pip3 install pandas`
  * Install requests (HTTP library)
    * `pip3 install requests`
* Download Script
  * Navigate to `totalMileageCalculator.py` in this Repository
  * In the top right, right click the Raw button
  * Right click - Save as...
* Add API Key to script
  * Replace `{API Key goes here}` with your API key using your text editor of choice (VIM, Emacs, etc)
  * ex. on line #8: `API_KEY = '123456789'`

## Running the script
Script will take any number of CSV files as input and aggregate the data

Run `python3 {script_path} {csv_file_1} {csv_file_2} ... {csv_file_n}`

Upon completing script, `Script_Output_Miles_{today's date}.csv` will be downloaded to current working directory

Output CSV format example: 

|Date|Total Miles|
| --- | --- |
|07-27-2022|121.51|
|07-28-2022|8.15|
|07-29-2022|58.14|
|08-01-2022|22.32|
|08-02-2022|24.4|
|08-03-2022|121.51|
|08-04-2022|58.14|
| | |
|July Total|187.36|
|August Total|225.94|

### Script Notes
* Script assumes no travel will occur overnight - mileage is collected from locations grouped by `Start Date` column
* Mileage calculated comes from Google Map's top recommended route at the time of invoking the script
* All `Location` column values Google Maps doesn't recognize will be dropped from calculation
