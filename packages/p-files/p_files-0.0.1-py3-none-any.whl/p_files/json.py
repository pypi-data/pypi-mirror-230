import json
import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Logging level (you can adjust this level as needed)
    format="%(levelname)s: %(message)s",
)


def update_json_value(file_path, key, new_value):
    logger = logging.getLogger(__name__)  # Create a logger instance

    try:
        # Open the JSON file in read mode
        with open(file_path, "r") as file:
            data = json.load(file)  # Load the JSON content

        # Update the value for the key
        data[key] = new_value

        # Open the JSON file in write mode and save the changes
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)  # Write the JSON content with formatting

        logger.info(
            f"The value for key '{key}' has been successfully updated in '{file_path}'."
        )
    except FileNotFoundError:
        logger.error(f"The file '{file_path}' does not exist.")
        raise
    except json.JSONDecodeError:
        logger.error(f"The file '{file_path}' is not a valid JSON file.")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
