# DSC 510
# Week 5
# Programming Assignment Week 5
# Author Kimberly Adams
# 4/17/2022

"""
Description: This program is a point of sale transaction where the user inputs
their company name and length of fiber optic cable they wish to purchase and gives
a receipt showing the total cost and other details of the transaction.
"""
# Change Control Log:
# Change#:2
"""
Changes Made: 
Added functions in process to help compartmentalize steps
Added main function
Simplified some of the calculations
Changed Length variable to float instead of integer
made variable names lowercase
"""
# Date of Change: 4/6/2022
# Author: Kimberly Adams
# Change Approved by: Kimberly Adams
# Date Moved to Production: 4/9/2022

# Get current date
import datetime
from datetime import date
today = date.today()


def get_info():
    """Ask user for name of purchasing company and length of cable needed."""
    print('Welcome to Viper Optics')
    print('')
    company = input('Please enter the name of the company you are purchasing for: ')
    length = input('How many feet of fiber optic cable are you needing to install today? ')
    return company, length


def bulk_discount(length):
    """Checks for applicable bulk discount."""
    if length <= 100:
        return 0.87, 'No'
    elif length <= 250:
        return 0.80, '100+ feet'
    elif length <= 500:
        return 0.70, '250+ feet'
    else:
        return 0.50, '500+ feet'


def subtotal_calc(length, cost):
    """Calculate the installation cost of fiber optic cable with a 7% sales tax."""
    return length * cost


def main():
    """Creates a printable receipt"""

    company, length = get_info()

    # Checks for valid length input.
    try:
        length = float(length)
    except:
        print('The number you entered was not a valid number. Please re-enter your value.')
        length = input('How many feet of fiber optic cable are you needing to install today? ')

    length = float(length)
    cost, bulk = bulk_discount(length)

    subtotal = subtotal_calc(length, cost)
    tax = subtotal * 0.07
    total = subtotal + tax

    # Receipt
    print('------------------------')
    print('Viper Optics')
    print("Date:", today)
    print('')
    print('Buyer:', company)
    print('')
    print('Length (feet): ', length)
    print('Bulk Discount: ', bulk)
    print('Cost per foot: ', "${:,.2f}".format(cost))
    print('Subtotal:      ', "${:,.2f}".format(subtotal))
    print('Sales Tax 7%:  ', "${:,.2f}".format(tax))
    print('')
    print('Total Due:     ', "${:,.2f}".format(total))
    print('------------------------')
    print('')
    print('Thank you for your business. Have a great day!')


if __name__ == "__main__":
    main()

# Exits the program when finished.
quit()
