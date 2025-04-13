import json

def extract_token(json_file_path):
    """Extracts bearer token and store ID from CDP logs"""
    print(json_file_path)
    try:
        with open(json_file_path, 'r') as f:
            cdp_logs = json.load(f)
        bearer_token = None

        # Iterate through the logs to extract the required data
        for entry in cdp_logs:
            try:
                # Check if the 'message' field is present
                message = entry.get('message', None)
                if message:
                    # Parse the 'message' field (it's a JSON string)
                    parsed_message = json.loads(message)
                    params = parsed_message.get('message', {}).get('params', {})
                    headers = params.get('headers', {})
                    
                    # Check for the Bearer token
                    if bearer_token is None:  # Only look for token if not found
                        auth = headers.get('authorization', '')
                        if auth.startswith('Bearer '):
                            bearer_token = auth
                            
                           

                    # Stop searching if both are found
                    if bearer_token:
                        break

            except Exception as e:
                print(f"Error processing entry: {e}")
        return bearer_token
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from file {json_file_path}.")
        return None