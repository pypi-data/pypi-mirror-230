from ascii_magic import AsciiArt
from colorama import Fore
import requests

def get_devops_details():

    logo_url = "https://firebasestorage.googleapis.com/v0/b/findalawyer-8eb1b.appspot.com/o/logo.png?alt=media&token=faa2884d-2315-4170-ac90-4e74004447e2"
    json_url = "https://firebasestorage.googleapis.com/v0/b/findalawyer-8eb1b.appspot.com/o/details_of_employee.json?alt=media&token=d06771b8-42e1-415d-bf85-acf2e8d422d0"

    presidio_logo = AsciiArt.from_url(logo_url)

    print("\n \n")
    presidio_logo.to_terminal()
    print("\n \n")

    print(Fore.MAGENTA + "Presidio DevOps Team : ")
    print("\n")

    employee_data = requests.get(json_url)

    for employee in employee_data.json():
        print(Fore.CYAN + employee['name'], end = " - ")
        print(Fore.BLUE + employee['domain'], end = " - ")
        print(Fore.GREEN + employee['designation'], end = "")
        print("\n")
