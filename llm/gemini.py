from pydantic import BaseModel
from google import genai

client = genai.Client(api_key="AIzaSyAl3zXcN2s_UVe3lnfJAA38iORw5dYAgJw")

class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    major_cities: list[str]
    gdp: int
    official_language: str
    total_area_sq_mi: int

response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents='Give me information of the United States.',
    config={
        'response_mime_type': 'application/json',
        'response_schema': CountryInfo,
    },
 )
print(response.text)

