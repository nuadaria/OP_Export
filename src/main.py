import requests
import html
import json
import re
import os
from typing import Any, Dict, Union, Optional

# Constants
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}
URL_BASE = 'https://testymctestface-1.obsidianportal.com'
URL_CAMPAIGN_INDEX = '/content_summary_gm.json'
MAPPING_BASE_PATH = "src\\mappings\\"

def fetch_data(url: str, response_type: str) -> Union[Dict[str, Any], str, None]:
    """Fetch data from a given URL and return it in the specified format."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)

        if response_type == 'json':
            try:
                return response.json()
            except json.JSONDecodeError:
                print("Error: Response content is not valid JSON.")
                return None
        
        elif response_type == 'html':
            return response.content.decode("utf-8")
        
        else:
            raise ValueError(f"Unsupported response_type: {response_type}")
    
    except requests.RequestException as req_err:
        print(f"Request error: {req_err}")
        return None
    
    except ValueError as val_err:
        print(f"Value error: {val_err}")
        return None

def load_mapping(file_path: str) -> Dict[str, str]:
    """Load mapping from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def map_to_standard_format(data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """Map data to a standardized format using the provided mapping."""
    return {standard_key: (data.get(dynamic_key) if data.get(dynamic_key) is not None else '') for standard_key, dynamic_key in mapping.items()}

def extract_data_from_html(html: str, character_page: bool) -> Optional[Dict[str, str]]:
    """Extract data from HTML using a combined regular expression with named capturing groups."""
    if character_page:
        pattern = re.compile(r'(?P<dynamic_sheet_attrs>(?<=dynamic_sheet_attrs = ).*?(?=;\n))|(?P<dst_slug>(?<=class="dst_slug">).*?(?=</))')
        matches = pattern.finditer(html)
        
        result = {}
        for match in matches:
            if match.group('dynamic_sheet_attrs'):
                result['dynamic_sheet_attrs'] = match.group('dynamic_sheet_attrs')
            if match.group('dst_slug'):
                result['dst_slug'] = match.group('dst_slug')

        return result if result else None
    else:
        pattern = re.compile(r'<div class=[\'"]system-logo-container[^>]*>.*?<img[^>]*title=[\'"]([^\'"]+)[\'"][^>]*>', re.DOTALL)
        match = pattern.search(html)
        
        if match:
            return unescape_json_values(match.group(1))  # Unescape HTML entities
            #return {'title': title}
        
        return None

def unescape_json_values(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: unescape_json_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [unescape_json_values(item) for item in data]
    elif isinstance(data, str):
        # Unescape HTML entities in the string
        data = html.unescape(data)
        return data
    else:
        return data
    
def main() -> None:
    """Main function to execute the script logic."""
    # Fetch campaign data
    campaign_system_page = fetch_data(URL_BASE, 'html')
    campaign_type = extract_data_from_html(campaign_system_page, False)
    campaign_data = fetch_data(URL_BASE + URL_CAMPAIGN_INDEX, 'json')
    
    game_characters = {}
    sheet_types = set()
    
    # Initialize game characters dictionary and temporarily store HTML data
    extracted_data_map = {}
    
    for item in campaign_data['game_characters']:
        game_characters[item['title']] = {
            'path': item['path'],
            'sheetType': '',
            'standardizedSheet': ''
        }
        extracted_data_map[item['title']] = extract_data_from_html(fetch_data(URL_BASE + item['path'], 'html'), True)

    # Collect all unique sheet types
    for character, details in game_characters.items():
        extracted_data = extracted_data_map[character]
        if extracted_data:
            sheet_attrs = unescape_json_values(extracted_data.get('dynamic_sheet_attrs'))
            sheet_type = extracted_data.get('dst_slug')
            
            if sheet_type:
                details['sheetType'] = sheet_type
                sheet_types.add(sheet_type)

    # Create a map of sheetType to loaded file
    sheet_type_mappings = {}
    for sheet_type in sheet_types:
        #mapping_file_path = f"{sheet_type}.json"
        mapping_file_path = os.path.join(MAPPING_BASE_PATH, campaign_type, f"{sheet_type}.json")
        sheet_type_mappings[sheet_type] = load_mapping(mapping_file_path)

    # Map each character's sheetType and sheetAttrs appropriately
    for character, details in game_characters.items():
        if details['sheetType']:
            sheet_attrs = unescape_json_values(extracted_data_map[character].get('dynamic_sheet_attrs'))
            details['standardizedSheet'] = map_to_standard_format(json.loads(sheet_attrs), sheet_type_mappings[details['sheetType']])

    # Print or return the game_characters for further processing or validation
    print(game_characters)

if __name__ == "__main__":
    main()