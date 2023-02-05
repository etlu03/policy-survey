import argparse

def main():
  parser = argparse.ArgumentParser(description="Feed privacy notice to audit")
  parser.add_argument(
        "--url", "-u", action="store", help="URL of privacy notice", required=True
  )
  args = parser.parse_args()

  url = args.url
    
if __name__ == "__main__":
  main()