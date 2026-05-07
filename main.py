import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Union

def scraper(
    url: str,
    scale: int = 1,
    include_links: bool = False
) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    """
    Scrape news articles from any website at a specified scale, with optional link scraping.

    Args:
        url (str): The URL of the news website to scrape.
        scale (int): The depth of scraping:
            1: Only headlines (h1)
            2: Headlines and first paragraph (h1 + first p)
            3: Headlines, all paragraphs, and article body divs (h1 + all p + relevant divs)
        include_links (bool): If True, include all hyperlinks (text and href) in the output.

    Returns:
        List[Dict[str, Union[str, List[Dict[str, str]]]]]:
            A list of dictionaries, each containing 'source', 'title', 'content', and optionally 'links'.
    """
    articles = []
    try:
        print(f"Scraping {url}...")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all article links (adjust selector as needed)
        article_links = []
        for link in soup.select('a[href]'):
            href = link.get('href')
            if href and href.startswith('http') and ('article' in href or 'news' in href):
                article_links.append(href)

        for link in list(set(article_links))[:5]:  # Limit to 5 unique articles for demo
            try:
                article_response = requests.get(link, timeout=10)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                title = article_soup.find('h1').get_text(strip=True) if article_soup.find('h1') else "No title"

                if scale == 1:
                    content = ""
                elif scale == 2:
                    first_p = article_soup.find('p')
                    content = first_p.get_text(strip=True) if first_p else ""
                elif scale == 3:
                    paragraphs = article_soup.find_all('p')
                    divs = article_soup.find_all('div', class_=lambda x: x and 'article' in x.lower())
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs] +
                                      [d.get_text(strip=True) for d in divs])
                else:
                    raise ValueError("Scale must be 1, 2, or 3.")

                article = {
                    "source": link,
                    "title": title,
                    "content": content,
                }

                if include_links:
                    links = []
                    for a in article_soup.find_all('a', href=True):
                        links.append({
                            "text": a.get_text(strip=True),
                            "href": a['href']
                        })
                    article["links"] = links

                articles.append(article)
            except Exception as e:
                print(f"Error scraping {link}: {e}")
                continue

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return articles

# Example usage:
if __name__ == "__main__":
    # Scrape headlines only, no links
    headlines = scraper("https://www.nzherald.co.nz/", 1, False)
    for article in headlines:
        print(f"Source: {article['source']}")
        print(f"Title: {article['title']}\n")

    # Scrape full articles with links
    full_articles = scraper("https://www.stuff.co.nz/", 3, True)
    for article in full_articles:
        print(f"Source: {article['source']}")
        print(f"Title: {article['title']}")
        print(f"Content: {article['content'][:200]}...")
        if 'links' in article:
            print("Links found:")
            for link in article['links'][:3]:  # Print first 3 links for demo
                print(f"  - {link['text']}: {link['href']}")
        print()