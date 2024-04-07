# DSC 510
# Week 12
# Final Project
# Author: Kimberly Adams
# 5/23/2022

"""
Description: This program retrieves current weather conditions based on US city
or zip code input from the user using APIs from https://openweathermap.org/.

Change Control Log: 0
Change#: Original
Date of Change: 5/23/2022
Author: Kimberly Adams
Change Approved by: Kimberly Adams
Date Moved to Production: 5/23/2022
"""


def internet_check():
    #  Checks that the user has an active internet connection.
    import requests
    import sys

    try:
        requests.head('https://openweathermap.org/', timeout=5)
    except requests.ConnectionError:
        print('No internet connection detected.  Please check your internet connection and then run the program again.')
        sys.exit(0)


def unit_def():
    #  Asks user for unit type to display weather data.
    user_unit = input("What units would you like your forecast displayed in? \n(Once this is set, it will not change until the program is restarted.)\n    'F' for Fahrenheit\n    'C' for Celsius\n    'K' for Kelvin\n\n     Units choice: ")
    units_list = ['F', 'C', 'K']

    #  Verifies valid units are entered by the user.
    error = 'Yes'
    while error == 'Yes':
        user_unit = str.upper(user_unit)
        if user_unit in units_list:
            error = 'No'
        else:
            error = 'Yes'
            print('\nError: The unit value you entered is not valid.')
            user_unit = input("What units would you like your forecast displayed in? Once this is set, it will not change until the program is restarted.\n    'F' for Fahrenheit\n    'C' for Celsius\n    'K' for Kelvin\n\n     Units choice: ")

    #  Sets units value into API query standards.
    if user_unit == 'F':
        units = 'imperial'
    elif user_unit == 'C':
        units = 'metric'
    else:
        units = 'standard'

    return units, user_unit


def zip_code_value():
    #  This function looks up the location using a user-inputted zip code value.
    zip_code = input('\nPlease enter a 5 digit zip code: ')

    #  Error checks to see if zip code is numeric
    error = 'Yes'
    while error == 'Yes':
        if zip_code.isnumeric():
            error = 'No'
        else:
            error = 'Yes'
            print('Error: The zip code you entered is not numeric.\n')
            zip_code = input('Please enter a numeric 5 digit zip code: ')

    #  Error checks to see if zip code is 5 digits
    error = 'Yes'
    while error == 'Yes':
        if len(zip_code) == 5:
            error = 'No'
        else:
            error = 'Yes'
            print('Error: The zip code you entered is not 5 digits.\n')
            zip_code = input('Please enter a 5 digit zip code: ')

    location = zip_code
    return location


def city_value():
    #  This function looks up the location using a user-inputted city value.
    print('To look up a forecast by US city, you will need the name of the city and state.')
    city = input('Please enter a US city name (city only): ')
    state = input('Please enter a 2 letter US state abbreviation: ')

    #  Tests entered state abbreviation against list of acceptable abbreviations.
    states_set = {'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY'}
    error = 'Yes'
    while error == 'Yes':
        state = str.upper(state)
        if state in states_set:
            error = 'No'
        else:
            error = 'Yes'
            print('Error: The state abbreviation you entered is not valid.')
            state = input('Please enter a 2 letter US state abbreviation: ')

    #  Replaces special characters like spaces and apostrophes.
    city = city.replace(' ', '%20')
    city = city.replace("'", '%27')

    location = city.title() + ', ' + state.upper()
    return location


def geocode(location, search_query):
    #  Searches for GPS coordinates from user-entered location using Geocoding API.
    #  http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&appid={API key}
    #  http://api.openweathermap.org/geo/1.0/zip?zip={zip code},{country code}&appid={API key}
    import requests
    import json

    #  Builds the URL for the API.
    url_base_geo = 'http://api.openweathermap.org/geo/1.0/'
    api_key = '&appid=29ed0d133b38f32d487f604b6aa160c0'

    input_error = 'yes'
    while input_error != 'no':
        if search_query.upper() == 'Z':
            location_query = 'zip?zip=' + location + ',' + 'US'
        else:
            location.replace(' ', '')
            location_query = 'direct?q=' + location + ',' + 'US'
        url_query_geo = str(url_base_geo) + str(location_query) + str(api_key)

        #  Uses the API to fetch the raw data.
        raw_geodata = requests.request("GET", url_query_geo)
        response = json.loads(raw_geodata.text)

        #  Checks for error codes in the API response.
        if "cod" in response:
            error_code = str(response.get('cod'))
        else:
            error_code = 'None'
            pass

        #  Verifies user-entered search keywords are found by API and data is returned.
        if str(error_code) == '404':  # Checks for values not found.
            print('Error 404')
            if search_query.upper() == 'C':
                print('\nError: City not found.  Please re-enter.\n')
                location = city_value()
            else:
                print('\nError: Zip code not found.  Please re-enter.\n')
                location = zip_code_value()
        elif len(str(response)) < 3:  # Checks for empty returns.
            print('Error: empty')
            if search_query.upper() == 'C':
                print('\nError: City not found.  Please re-enter.\n')
                location = city_value()
            else:
                print('\nError: Zip code not found.  Please re-enter.\n')
                location = zip_code_value()
        else:
            input_error = 'no'
            break

    #  Searches for GPS values in the raw data that is returned by the geocoding API.
    if search_query.upper() == 'Z':
        latitude = str(response.get('lat'))
        longitude = str(response.get('lon'))
    else:
        latitude = str(response[0]['lat'])
        longitude = str(response[0]['lon'])
    lat_long_query = 'lat=' + latitude + '&lon=' + longitude
    return lat_long_query


def location_name(lat_long_query):
    #  Returns location name of API weather lookup using reverse geocoding API.
    #  Used to doublecheck that the forecast returned is what the user was looking for.
    #  http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&appid={API key}
    import requests

    #  Builds the URL for the reverse geocoding API.
    url_base_geo_rev = 'http://api.openweathermap.org/geo/1.0/reverse?'
    api_key = '&appid=29ed0d133b38f32d487f604b6aa160c0'
    url_query_geo_rev = url_base_geo_rev + lat_long_query + api_key

    #  Uses the API to fetch the raw data.
    raw_geodata = requests.request("GET", url_query_geo_rev)

    import json

    response = json.loads(raw_geodata.text)

    #  Searches for key data values in the raw data that is returned by the API.
    location_main = str(response[0]['name'])
    location_state = str(response[0]['state'])
    location = location_main + ', ' + location_state

    return location


def forecast_data(lat_long_query, units):
    #  Returns forecast for GPS coordinates using the Current Weather API.

    #  Builds the URL for the API.
    #  https://api.openweathermap.org/data/2.5/weather?lat=57&lon=-2.15&appid={API key}&units=imperial
    url_base = 'https://api.openweathermap.org/data/2.5/weather?'
    api_key = '&appid=29ed0d133b38f32d487f604b6aa160c0'
    url_query = url_base + lat_long_query + api_key + '&units=' + units

    #  Uses the Current Weather API to fetch the raw weather data.
    import requests
    raw_data = requests.request("GET", url_query)

    return raw_data


def pretty_forecast(raw_data, location, user_unit):
    #  Takes the raw weather data returned by the API and puts it in a user-friendly format.
    import json

    response = json.loads(raw_data.text)

    #  Searches for key data values in the raw data that is returned by the API.
    conditions = str(response['weather'][0]['main'])
    temp = str(response['main']['temp'])
    feels_like = str(response['main']['feels_like'])
    temp_hi = str(response['main']['temp_max'])
    temp_low = str(response['main']['temp_min'])
    pressure = str(response['main']['pressure'])
    humidity = str(response['main']['humidity'])
    clouds = str(response['clouds']['all'])

    #  Prints key data values in a nice format.
    degree_sign = u'\N{DEGREE SIGN}'

    print('\n-------------------------------------------------------')
    print(location)
    print('Current Weather Conditions: \n')
    print('Overall: ' + conditions)
    print('Current Temp: ' + temp + degree_sign + user_unit)
    print('  Feels like: ' + feels_like + degree_sign + user_unit)
    print('  High: ' + temp_hi + degree_sign + user_unit)
    print('  Low: ' + temp_low + degree_sign + user_unit)
    print('Pressure: ' + pressure + ' hPa')
    print('Humidity: ' + humidity + '%')
    print('Cloud Cover: ' + clouds + '%')
    print('-------------------------------------------------------')


def main():
    print('Welcome to Super Simple Weather Forecasts')
    internet_check()
    print('     Internet connection: Verified\n')

    #  Asks the user what units to display the forecast in.
    units, user_unit = unit_def()

    #  Asks user for their preferred search criteria and creates a loop for multiple searches.
    search_query = 'Undefined'
    cont = 'Y'
    while cont.upper() == 'Y':
        internet_check()
        while search_query == 'Undefined':
            search_query = input('\nHow would you like to search for your weather forecast? \n     Z = Zip Code \n     C = City \n\n     Search choice: ')
            if search_query.upper() == 'Z':  # Searches via zip code.
                location = zip_code_value()
            elif search_query.upper() == 'C':  # Searches via city name.
                print('\n')
                location = city_value()
            else:
                search_query = 'Undefined'
                print('Your input is invalid. You must enter Z or C.')

        #  Retrieve location and forecast data.
        internet_check()
        lat_long_query = geocode(location, search_query)
        location = location_name(lat_long_query)
        raw_data = forecast_data(lat_long_query, units)
        pretty_forecast(raw_data, location, user_unit)

        # Asks user if they want to look up another forecast or close the program.
        cont = input("\nWould you like to look up another forecast (Y/N)? ")
        if cont.upper() == "N" or cont == "n":
            print("\nThank you for using this program.  \nHopefully it was useful and accurate.")
        else:
            search_query = 'Undefined'


if __name__ == "__main__":
    main()
