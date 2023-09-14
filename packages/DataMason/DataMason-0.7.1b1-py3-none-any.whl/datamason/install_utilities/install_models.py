from contextlib import redirect_stdout
import io
from polyglot.downloader import Downloader
import logging
from polyglot.text import Text
import pandas as pd

# Initialize or import your logger here
polyglot_logger = logging.getLogger("polyglot_logger")

downloader = Downloader()

def download_model(model, max_retries=3):
    f = io.StringIO()
    retries = 0
    while retries < max_retries:
        with redirect_stdout(f):
            try:
                downloader.download(model)
                print(f"Successfully downloaded {model}")
                return True
            except Exception as e:
                print(f"Failed to download {model}: {e}")
                retries += 1
    print(f"Giving up on {model} after {max_retries} attempts.")
    captured_output = f.getvalue()
    polyglot_logger.info(captured_output)
    return False

# Global variables
downloaded_langs = []
iw_to_he_logged = False

def install_models(data):
    global downloaded_langs
    global iw_to_he_logged
    
    # Function to handle single text input
    def process_text(text):
        try:
            _ = Text(text).language.code
        except Exception as e:
            error_message = str(e)
            if "polyglot download LANG." in error_message:
                start_index = error_message.index("polyglot download LANG.") + len("polyglot download LANG.")
                end_index = start_index + 2
                missing_model_code = error_message[start_index:end_index]
                
                if missing_model_code == "iw":
                    if not iw_to_he_logged:
                        polyglot_logger.info("Converting .iw to .he")
                        iw_to_he_logged = True
                    missing_model_code = "he"
                
                lang_model = f'LANG:{missing_model_code}'
                
                if lang_model not in downloaded_langs:
                    download_model(lang_model)
                    downloaded_langs.append(lang_model)
            else:
                polyglot_logger.error(f"An error occurred: {e}")
    
    if isinstance(data, str):
        process_text(data)
    elif isinstance(data, list):
        for text in data:
            process_text(str(text))
    elif isinstance(data, pd.DataFrame):
        for column in data.columns:
            for text in data[column]:
                process_text(str(text))
    else:
        polyglot_logger.error(f"Unsupported data type: {type(data)}")
