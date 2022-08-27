import sys
import requests
import calendar
import os
from datetime import date
import pandas as pd

API_KEY = '{API Key goes here}'
GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'
DIRECTIONS_URL = 'https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}'
HOME_ADDRESS = '2116 Mulberry Ln, Jenison, MI 49428'
OUTPUT_CSV = 'Script_Output_Miles_{}.csv'
SUCCESS_MESSAGE = 'Successfully populated {} in directory {}'

def callGeocodingAPI(address):

    def convertToAddressParameter(address):

        if address.find(')') != -1:
            address = address[address.find('(')+1:address.find(')')] # Grabs address from parenthesis
        return '%20'.join(address.replace(',', '').split())

    addressParameter = convertToAddressParameter(address)
    formattedUrl = GEOCODE_URL.format(addressParameter, API_KEY)
    return requests.request('GET', formattedUrl)
    
def callDirectionsAPI(originId, destinationId):

    formattedUrl = DIRECTIONS_URL.format(originId, destinationId, API_KEY)
    return requests.request('GET', formattedUrl)

def convertAddressToPlaceId(address):
    
    geocodingApiResponse = callGeocodingAPI(address)
    results = geocodingApiResponse.json().get('results')
    if len(results):
        placeId = results[0].get('place_id')
        return 'place_id:' + placeId

def getDrivingDistance(originPlaceId, destinationPlaceId):

    destinationApiResponse = callDirectionsAPI(originPlaceId, destinationPlaceId)
    legs = destinationApiResponse.json().get('routes')[0].get('legs') # Assumes first listed route is most time efficient

    totalMeters = 0
    for leg in legs:
        totalMeters += leg.get('distance').get('value')

    return totalMeters

def convertCsvToDataFrame(csvFiles):
    dataFrame = pd.concat(map(pd.read_csv, csvFiles), ignore_index=True) # Read all csv files
    dataFrame['Date'] = dataFrame['Start Date'] + ' ' + dataFrame['Start Time'] # Combine start date + time
    dataFrame = dataFrame[['Start Date', 'Date', 'Location']] # Get relevant columns
    dataFrame = dataFrame.dropna() # Drop columns without locations
    dataFrame['PlaceId'] = dataFrame.apply(lambda x: convertAddressToPlaceId(x['Location']), axis=1) # Convert locations to placeIds
    dataFrame = dataFrame.dropna() # Drop unrecognized locations
    dataFrame['Date'] = pd.to_datetime(dataFrame['Date']) # Convert Date column to datetime object
    dataFrame['Start Date'] = pd.to_datetime(dataFrame['Start Date']) # Convert Date column to datetime object
    dataFrame = dataFrame.sort_values(by=['Date']) # Sort dataframe by Date
    dataFrame = dataFrame.groupby('Start Date')['PlaceId'].apply(list) # Group place id's into list by Date
    dataFrame = dataFrame.reset_index() # Reset index
    return dataFrame

def calculateTotalMeters(dataFrame):

    totalDayMeters = {}
    totalMonthMeters = {}
    homeAddressPlaceId = convertAddressToPlaceId(HOME_ADDRESS)

    for index, row in dataFrame.iterrows():
        date, placeIdList = row['Start Date'], row['PlaceId']

        stop = 0
        dayMeters = getDrivingDistance(homeAddressPlaceId, placeIdList[stop])
        while stop < len(placeIdList) - 1:
            if placeIdList[stop] != placeIdList[stop + 1]:
                dayMeters += getDrivingDistance(placeIdList[stop], placeIdList[stop + 1])
            stop += 1
        dayMeters += getDrivingDistance(placeIdList[stop], homeAddressPlaceId)
        totalDayMeters[date.strftime("%m-%d-%Y")] = dayMeters

        month = calendar.month_name[date.month] + ' Total'
        if month not in totalMonthMeters:
            totalMonthMeters[month] = 0
        totalMonthMeters[month] += dayMeters

    return totalDayMeters, totalMonthMeters

def convertTotalMetersToOutput(totalDayMeters, totalMonthMeters):
    d = {'Date': [], 'Total Miles': []}
    for day, meters in totalDayMeters.items():
        d['Date'].append(day)
        d['Total Miles'].append(round(meters * 0.00062137, 2))
    d['Date'].append(None)
    d['Total Miles'].append(None)
    for month, meters in totalMonthMeters.items():
        d['Date'].append(month)
        d['Total Miles'].append(round(meters * 0.00062137, 2))
    return pd.DataFrame(d)

def main():
    dataFrame = convertCsvToDataFrame(sys.argv[1:])
    totalDayMeters, totalMonthMeters = calculateTotalMeters(dataFrame)
    outputDataFrame = convertTotalMetersToOutput(totalDayMeters, totalMonthMeters)
    outputCsvFile = OUTPUT_CSV.format(date.today())
    outputDataFrame.to_csv(outputCsvFile, index = False, header=True)
    print(SUCCESS_MESSAGE.format(outputCsvFile, os.getcwd()))

if __name__ == '__main__':
    main()
