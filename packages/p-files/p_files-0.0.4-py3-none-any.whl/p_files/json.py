""" Manipulate JSON files in Python. """

import json
import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Logging level (you can adjust this level as needed)
    format="%(levelname)s: %(message)s",
)


def update_json_value(file_path, key, new_value):
    """Update the value for a key in a JSON file.

    :param file_path: json file path
    :type file_path: str
    :param key: key to update
    :type key: str
    :param new_value: new value for the key
    :type new_value: str
    """
    logger = logging.getLogger(__name__)  # Create a logger instance

    try:
        # Open the JSON file in read mode
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)  # Load the JSON content

        # Update the value for the key
        data[key] = new_value

        # Open the JSON file in write mode and save the changes
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)  # Write the JSON content with formatting

        logger.info(
            "The value for key '%s' has been successfully updated in '%s'.",
            key,
            file_path,
        )
    except FileNotFoundError:
        logger.error("The file '%s' does not exist.", file_path)
        raise
    except json.JSONDecodeError:
        logger.error("The file '%s' is not a valid JSON file.", file_path)
        raise
    except Exception as exception:
        logger.error("An error occurred: %s", str(exception))
        raise
