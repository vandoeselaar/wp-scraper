import requests
import pandas as pd
from datetime import datetime
import time
import argparse

def scrape_wordpress(base_url, per_page=100):
    """
    Scrape WordPress posts using the REST API
    
    Args:
        base_url (str): Base URL of the WordPress site (e.g., 'https://example.com')
        per_page (int): Number of posts to retrieve per request
    
    Returns:
        list: List of dictionaries containing post data
    """
    
    # Zorg ervoor dat de URL correct geformatteerd is
    if not base_url.endswith('/'):
        base_url += '/'
    
    api_url = f"{base_url}wp-json/wp/v2"
    all_posts = []
    page = 1
    
    while True:
        # Maak de API request
        response = requests.get(
            f"{api_url}/posts",
            params={
                'page': page,
                'per_page': per_page,
                'context': 'view',
                '_embed': 1  # Include embedded information (authors, categories, tags)
            }
        )
        
        # Check of we aan het einde zijn
        if response.status_code == 400:
            break
            
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            break
            
        posts = response.json()
        if not posts:
            break
            
        # Verwerk elke post
        for post in posts:
            # Haal de benodigde informatie op
            post_data = {
                'post_id': post['id'],
                'title': post['title']['rendered'],
                'content': post['content']['rendered'],
                'modified_date': post['modified'],
                'publication_date': post['date'],
                'author': post['_embedded']['author'][0]['name'] if 'author' in post['_embedded'] else '',
                'tags': ', '.join([tag['name'] for tag in post['_embedded']['wp:term'][1]]) if 'wp:term' in post['_embedded'] and len(post['_embedded']['wp:term']) > 1 else '',
                'categories': ', '.join([cat['name'] for cat in post['_embedded']['wp:term'][0]]) if 'wp:term' in post['_embedded'] else ''
            }
            all_posts.append(post_data)
        
        print(f"Verwerkte pagina {page}, {len(all_posts)} posts tot nu toe")
        page += 1
        time.sleep(1)  # Wacht 1 seconde tussen requests om de server niet te overbelasten
    
    return all_posts

def save_to_csv(posts, output_file='wordpress_posts.csv'):
    """
    Sla de verzamelde posts op in een CSV bestand
    
    Args:
        posts (list): Lijst met post dictionaries
        output_file (str): Naam van het output bestand
    """
    df = pd.DataFrame(posts)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data opgeslagen in {output_file}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape WordPress posts via de REST API')
    parser.add_argument('url', help='De URL van de WordPress website (bijv. https://example.com)')
    parser.add_argument('--output', '-o', default='wordpress_posts.csv',
                      help='Output bestandsnaam (default: wordpress_posts.csv)')
    parser.add_argument('--posts-per-page', '-p', type=int, default=100,
                      help='Aantal posts per pagina (default: 100)')
    
    args = parser.parse_args()
    
    # Scrape de posts
    print(f"Begin met scrapen van {args.url}...")
    posts = scrape_wordpress(args.url, args.posts_per_page)
    
    # Sla op als CSV
    print(f"Gevonden posts: {len(posts)}")
    save_to_csv(posts, args.output)

if __name__ == "__main__":
    main()
