import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the input file
input_file = "input.txt"
id_output_file = "ids.txt"

# API details
post_url = "https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts"
likes_url = "https://instagram-scraper-api2.p.rapidapi.com/v1/likes"
headers = {
    "x-rapidapi-key": "f349c95649msh6fe4c1d68efd0e2p1413b8jsn157c200f23f3",
    "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
}

try:
    # Read the file and extract usernames
    with open(input_file, "r") as file:
        lines = file.readlines()
        usernames = [line.strip().split("/")[-2] for line in lines if line.strip()]
    
    logging.info(f"Extracted usernames: {usernames}")

    # Open the ID output file for writing
    with open(id_output_file, "w") as id_file:
        # Iterate through each username and make the API call
        for username in usernames:
            logging.info(f"Processing username: {username}")

            # First API call to get posts for the username
            querystring = {"username_or_id_or_url": username}
            response = requests.get(post_url, headers=headers, params=querystring)

            if response.status_code == 200:
                logging.info(f"Successfully fetched data for username: {username}")
                try:
                    data = response.json()
                    posts = data['data']['items']  # Use .get to avoid KeyError

                    for post in posts:
                        code = post.get('code')  # Ensure the 'code' key is accessed safely
                        post_id = post.get('id')  # Similarly for 'id'

                        if code and post_id:
                            logging.info(f"Found shortcode: {code} for username: {username}")
                            
                            # Fetch likes data for the shortcode
                            likes_querystring = {"code_or_id_or_url": code}
                            likes_response = requests.get(likes_url, headers=headers, params=likes_querystring)

                            if likes_response.status_code == 200:
                                likes_data = likes_response.json()
                                
                                # Extract and save each like's ID from the likes response
                                like_items = likes_data.get('data', {}).get('items', [])
                                if like_items:
                                    for like in like_items:
                                        like_id = like.get('id')
                                        if like_id:
                                            # Save the like ID (you can save these to a file or handle as needed)
                                            id_file.write(f"{like_id}\n")
                                            logging.info(f"Saved Like ID: {like_id} for code: {code} and username: {username}")
                                        else:
                                            logging.warning(f"Like item missing ID for code: {code} and username: {username}")
                            else:
                                logging.warning(f"Failed to fetch likes for code {code}: {likes_response.status_code}")
                            
                            # Save the post ID
                            id_file.write(f"{post_id}\n")
                            logging.info(f"Saved Post ID: {post_id} for username: {username}")

                except Exception as e:
                    logging.error(f"Error parsing response for username {username}: {e}")
            else:
                logging.warning(f"Failed to fetch data for username {username}: {response.status_code}")

    logging.info("Processing complete. Collected IDs saved.")

except FileNotFoundError:
    logging.error("The input file was not found.")
except Exception as e:
    logging.error(f"An error occurred: {e}")
