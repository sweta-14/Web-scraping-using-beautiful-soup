import time
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
from tkinter import simpledialog
import webbrowser
import filecmp
import csv
import re

# Start the timer
start_time = time.time()

# Function to download a file from a given URL and save it in the specified folder
downloaded_images = []
def download_file(url, folder):
    response = requests.get(url)
    if response.status_code == 200:
        filename = url.split('/')[-1]
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filepath = os.path.join(folder, filename)
        
        # Check if the image URL has already been downloaded
        if url in downloaded_images:
            print('Image already downloaded:', filename)
        else:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print('Downloaded:', filename)
            
            # Add the downloaded image URL to the list
            downloaded_images.append(url)
    else:
        print('Failed to download:', url)


# Function to parse each person's URL
def parse_person(person_url, processed_names):
    # Send a GET request to the person's URL
    response = requests.get(person_url)

    # Check if the website response is successful (status code 200)
    if response.status_code == 200:
        # Create a BeautifulSoup object to parse the website HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the tag that contains the person's name
        name_tag = soup.find('b')

        # Check if the name tag exists and contains text
        if name_tag is not None and name_tag.text:
            # Extract the person's name from the tag
            person_name = name_tag.text.strip()

            # Remove invalid characters from the person's name
            person_name = re.sub(r'[<>:"/\\|?*]', '', person_name)

            # Check if the person's name has already been processed
            if person_name in processed_names:
                print('Skipping:', person_name)
                return

            # Add the person's name to the processed names list
            processed_names.append(person_name)

            # Create the folder using the person's name
            folder_name = person_name.replace(' ', '_')
            folder_path = os.path.join(r'C:\Users\Sweta.Goswami\Downloads\candidate details', folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Find all image tags in the website HTML
            image_tags = soup.find_all('img')

            # Download the person's image
            for image_tag in image_tags:
                image_src = image_tag.get('src')
                if image_src and 'logo' not in image_src.lower():
                   parent_tag = image_tag.find_parent(['header', 'footer'])
                   if not parent_tag:
            # Construct the absolute URL of the image
                      image_url = urljoin(person_url, image_src)
            
            # Download the image and save it in the specified folder
                      download_file(image_url, folder_path)
            # Find all anchor tags (links) in the website HTML
            anchor_tags = soup.find_all('a')

            # Download the PDF documents related to the person
            for anchor_tag in anchor_tags:
                href = anchor_tag.get('href')
                if href and href.endswith('.pdf'):
                    # Construct the absolute URL of the PDF document
                    pdf_url = urljoin(person_url, href)

                    # Download the PDF document and save it in the specified folder
                    download_file(pdf_url, folder_path)

            # Extract the text data from the website HTML (excluding header and footer)
            header_tags = ['header', 'footer']
            excluded_tags = soup.find_all(header_tags)
            for tag in excluded_tags:
                tag.extract()
            text_data = soup.get_text().strip()

            # Create and save the text file
            text_filename = folder_name + '.txt'
            text_filepath = os.path.join(folder_path, text_filename)
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(text_data)
            print('Text file saved:', text_filename)

        else:
            print('Name tag not found or does not contain text for:', person_url)

    else:
        print('Failed to retrieve website:', person_url)

# Function to navigate through multiple pages on the website
def navigate_pages(main_website_url, num_pages):
    # Track processed names
    processed_names = []

    # Store the URLs of the pages to be parsed
    page_urls = [main_website_url]

    for page in range(num_pages):
        # Check if there are more page URLs to process
        if page >= len(page_urls):
            print('All available pages have been parsed.')
            break

        # Get the URL of the current page
        page_url = page_urls[page]

        # Send a GET request to the page URL
        response = requests.get(page_url)

        # Check if the page response is successful (status code 200)
        if response.status_code == 200:
            # Create a BeautifulSoup object to parse the page HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the specific table or element that contains the list of people
            # Replace 'table_id' with the actual ID or class name of the table or element
            table = soup.find('table', id='data-tab')

            # Check if the table exists
            if table is not None:
                # Find all the person links in the table
                person_links = table.find_all('a')

                # Parse each person's URL
                for person_link in person_links:
                    person_url = urljoin(main_website_url, person_link.get('href'))
                    parse_person(person_url, processed_names)
                    print('--------------------------------------------------')

            else:
                print(f'Table not found with the specified ID or class on page {page}')

            # Find the links to other pages on the website and add them to the page URLs list
            page_links = soup.find_all('a', class_='page-link')  # Replace 'page-link' with the actual class name of the page links
            for page_link in page_links:
                page_url = urljoin(main_website_url, page_link.get('href'))
                if page_url not in page_urls:
                    page_urls.append(page_url)

        else:
            print(f'Failed to retrieve page {page}')

# Create the Tkinter root window
root = tk.Tk()

# Hide the root window
root.withdraw()

# Prompt the user to enter the website URL
website_url = simpledialog.askstring("Website URL", "Please enter the website URL:")

# Open the website URL in the Chrome web browser
webbrowser.open(website_url)

# Wait for 5 seconds to allow the user to view the webpage
time.sleep(5)

# Prompt the user to enter the number of pages to scrape
num_pages = simpledialog.askinteger("Number of Pages", "Please enter the number of pages to scrape:")

# Start navigating through pages
navigate_pages(website_url, num_pages)

# End the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the execution time
print("Execution time:", elapsed_time, "seconds")

# Destroy the root window
root.destroy()

def extract_candidate_details(file_name, text):
    # Party Name
    party_name = re.search(r'Party Name:\s*(.*)', text).group(1).strip()

    # Name
    name = os.path.splitext(file_name)[0].replace('_', ' ')

    # Assembly constituency
    assembly_constituency = re.search(r'Assembly constituency:\s*(.*)', text).group(1).strip()

    # State
    state = re.search(r'State:\s*(.*)', text).group(1).strip()

    # Father's / Husband's Name
    father_husband_name = re.search(r"(?:Father's|Husband's) Name:\s*(.*)", text).group(1).strip()

    # Address
    address = re.search(r'Address:\s*(.*)', text).group(1).strip()

    # Gender
    gender = re.search(r'Gender:\s*(.*)', text).group(1).strip()

    # Return the extracted details as a list in the desired order
    candidate_details = [name, party_name, assembly_constituency, state, father_husband_name, address, gender]
    return candidate_details

# Directory path containing the person folders
directory_path = r'C:\Users\Sweta.Goswami\Downloads\candidate details'  # Replace with the actual directory path

# Initialize an empty list to store all candidate details
all_details = []

# Iterate over each folder in the directory
for folder_name in os.listdir(directory_path):
    folder_path = os.path.join(directory_path, folder_name)
    if os.path.isdir(folder_path):
        # Search for the text file within the folder
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

                # Extract candidate details
                details = extract_candidate_details(filename, text)
                all_details.append(details)

# Check if there are candidate details available
if len(all_details) > 0:
    # Define the column names
    column_names = ['Name', 'Party Name', 'Assembly constituency', 'State', "Father's / Husband's Name", 'Address', 'Gender']

    # Save all details in a CSV file
    output_filename = 'all_candidate_details.csv'  # Replace with desired output file name
    with open(output_filename, 'w', newline='', encoding='utf-8', errors='replace') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        writer.writerows(all_details)

    print("All candidate details saved successfully in", output_filename)
else:
    print("No candidate details found.")