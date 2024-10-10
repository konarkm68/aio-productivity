import requests
import time
import winsound  # For Windows beep sound

def successful_response(url):
  """
  Pings the given URL and checks for a successful response.

  Args:
      url: The URL to ping.

  Returns:
      True if the response status code is 200, False otherwise.
  """
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raises exception for non-200 status codes
    return True
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return False

def main():
  url = "https://mart.arckone.app/offerings/dsc"
  interval = 5  # Ping interval in seconds

  while True:
    if successful_response(url):
      print("Successful response received!")
      winsound.Beep(2500, 300)  # Adjust frequency (Hz) and duration (ms) as needed
      break
    else:
      print(f"Waiting for response... (checking every {interval} seconds)")
      time.sleep(interval)

if __name__ == "__main__":
  main()
