import base64
import os

# Create the directory if it doesn't exist
os.makedirs('shopify/static/shopify/images', exist_ok=True)

# Read the base64 data
base64_data = "AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AGZmZv9mZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv////8A////AP///wD///8A////AP///wBmZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/////AP///wD///8A////AP///wD///8AZmZm/2ZmZv////8A////AP///wD///8A////AP///wBmZmb/ZmZm/////wD///8A////AP///wD///8A////AGZmZv9mZmb/////AP///wD///8A////AP///wD///8AZmZm/2ZmZv////8A////AP///wD///8A////AP///wBmZmb/ZmZm/////wD///8A////AP///wD///8A////AGZmZv9mZmb/////AP///wD///8A////AP///wD///8AZmZm/2ZmZv////8A////AP///wD///8A////AP///wBmZmb/ZmZm/////wD///8A////AP///wD///8A////AGZmZv9mZmb/////AP///wD///8A////AP///wD///8AZmZm/2ZmZv////8A////AP///wD///8A////AP///wBmZmb/ZmZm/////wD///8A////AP///wD///8A////AGZmZv9mZmb/////AP///wD///8A////AP///wD///8AZmZm/2ZmZv////8A////AP///wD///8A////AP///wBmZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/////AP///wD///8A////AP///wD///8AZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/ZmZm/2ZmZv9mZmb/ZmZm/////wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wA="

# Convert base64 to binary
binary_data = base64.b64decode(base64_data)

# Write to favicon.ico file
with open('shopify/static/shopify/images/favicon.ico', 'wb') as f:
    f.write(binary_data)

print("Favicon created successfully!") 