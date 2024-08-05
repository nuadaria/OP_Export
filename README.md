# Data Fetcher and Processor

This Python script fetches data from a specified URL, processes it, and standardizes it based on a mapping configuration. It supports fetching data in JSON and HTML formats and utilizes regular expressions for parsing HTML content.

## Constants

### HEADERS

Hard coded header values simply present to avoid some basic traffic denial

### URL_BASE

The base campaign of your Obsidian Portal Campaign. Follows the format

-   https://
-   YOUR_CAMPAIGN_SLUG
-   .obsidianportal.com

### URL_CAMPAIGN_INDEX

Do not change

### MAPPING_BASE_PATH

Do not change unless you alter the file structure of the project

## Functions

### `fetch_data(url: str, response_type: str) -> Union[Dict[str, Any], str, None]`

Fetches data from a given URL.

-   **Parameters**:

    -   `url` (str): The URL to fetch data from.
    -   `response_type` (str): The expected format of the response ('json' or 'html').

-   **Returns**:

    -   Dictionary if `response_type` is 'json' and the response is valid JSON.
    -   String if `response_type` is 'html'.
    -   None in case of errors or unsupported response types.

-   **Error Handling**:
    -   Catches and prints errors related to HTTP requests and invalid JSON.

### `load_mapping(file_path: str) -> Dict[str, str]`

Loads a mapping configuration from a JSON file.

-   **Parameters**:

    -   `file_path` (str): The path to the JSON file containing the mapping.

-   **Returns**:
    -   Dictionary containing the mapping loaded from the JSON file.

### `map_to_standard_format(data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]`

Converts data to a standardized format based on a given mapping.

-   **Parameters**:

    -   `data` (dict): The data to be standardized.
    -   `mapping` (dict): A dictionary mapping dynamic keys to standard keys.

-   **Returns**:
    -   List of dictionaries, each representing a standardized item.

### `extract_data_from_html(html: str, character_page: bool) -> Optional[Dict[str, str]]`

Extracts specific data from HTML content using regular expressions.

-   **Parameters**:

    -   `html` (str): The HTML content to parse.
    -   `character_page` (bool): A boolean to fork logic for retrieving campaign_type

-   **Returns**:
    -   A dictionary with extracted data if successful; otherwise, None.

### `unescape_json_values(data: Any) -> Any`

Recursively unescape HTML entities within JSON-like structures. It handles nested dictionaries, lists, and strings, ensuring that all HTML-encoded characters are properly decoded.

-   **Parameters**:

    -   `data` (Any): The input data, which can be a dictionary, list, string, or any other type.

-   **Returns**:

    -   `Any`: The data with all HTML entities unescaped, maintaining the original structure.

## Main Execution Flow

1. **Fetch Data**: Retrieves the Campaing System from the base page.
2. **Fetch Data**: Retrieves a JSON file from a URL containing character data.
3. **Initialize Character Data**: Prepares a dictionary with character details.
4. **Process Each Character**:
    - Fetches the associated HTML page.
    - Extracts attributes and slugs from the HTML.
    - Loads the mapping file based on the slug.
    - Standardizes the character data using the mapping.
5. **Updates**: Stores the standardized data back in the character dictionary.
