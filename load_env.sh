#!/bin/bash

# Read each line in the .env file
while IFS== read -r key value; do
  # Skip blank lines and comments starting with #
  if [[ -n "$key" && ! "$key" =~ ^[[:space:]]*# ]]; then
    # Export the variable (makes it available to the script)
    echo "export $key=$value"
    export "$key=$value"
  fi
done < ".env"