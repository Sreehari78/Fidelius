from csvhandler import maskobfcsv
from pdfhandler import predictpdfheaders
import json

json_data = {'fileName': 'Ecommerce Customers Short.csv', 'headers': [{'name': 'Email', 'mode': 'male', 'prompt': 'change id names to random names and not domain names'}, {'name': 'Address', 'mode': 'female', 'prompt': 'only change street names'}, {'name': 'Avatar', 'mode': 'male', 'prompt': 'generate random value'}]}
#maskobfcsv(json_data)
predictpdfheaders("bank_form.pdf")