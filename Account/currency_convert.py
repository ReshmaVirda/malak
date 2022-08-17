from google_currency import convert 
import json

class Currency_Exchange:
    def exchange(from_currency, to_currency, amount):
        output = json.loads(convert(from_currency, to_currency, float(amount)))
        return output