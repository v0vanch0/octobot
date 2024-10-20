import json

# Save this data to a JSON file for demonstration purposes
audio_data_file_path = "C:\\PYTHON\\projects\\anotherProj\\audio\\audio_data.json"


# Function to load audio data from JSON
def load_audio_data(json_file_path):
    try:
        with open(json_file_path, "r", encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Ошибка загрузки JSON файла: {e}")
        return {}


# Assuming the path to the JSON file
audiod = load_audio_data(audio_data_file_path)
