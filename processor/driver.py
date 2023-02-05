import os
import argparse

def main():
  parser = argparse.ArgumentParser(description="Feed privacy notice to audit")
  parser.add_argument(
        "--url", "-u", action="store", help="URL of privacy notice", required=True
  )
  args = parser.parse_args()

  url = args.url
  
  os.system(f"python3 preprocessor.py --url {url}")
  os.system(f"node headless.js {url}")
  os.system(f"python3 build.py --url {url}")
  
if __name__ == "__main__":
  main()