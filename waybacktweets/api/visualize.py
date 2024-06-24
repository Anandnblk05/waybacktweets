# flake8: noqa: E501
"""
Generates an HTML file to visualize the parsed data.
"""

import json
import os
from typing import Any, Dict, List, Union

from waybacktweets.utils import timestamp_parser


class HTMLTweetsVisualizer:
    """
    Class responsible for generating an HTML file to visualize the parsed data.

    Args:
        username (str): The username associated with the tweets.
        json_path (Union[str, List[str]]): The path of the JSON file or the JSON data itself.
        html_file_path (str, optional): The path where the HTML file will be saved.
    """

    def __init__(
        self,
        username: str,
        json_path: Union[str, List[str]],
        html_file_path: str = None,
    ):
        self.username = username
        self.json_path = self._json_loader(json_path)
        self.html_file_path = html_file_path

    @staticmethod
    def _json_loader(json_path: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Reads and loads JSON data from a specified file path or JSON string.

        Args:
            json_path (Union[str, List[str]]): The path of the JSON file or the JSON data itself.

        Returns:
            The content of the JSON file or data.
        """
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)

        return json.loads(json_path)

    def generate(self) -> str:
        """
        Generates an HTML string that represents the parsed data.

        Returns:
            The generated HTML string.
        """
        tweets_per_page = 24
        total_pages = (len(self.json_path) + tweets_per_page - 1) // tweets_per_page

        html = "<!DOCTYPE html>\n"
        html += '<html lang="en">\n'
        html += "<!-- This document was generated by Wayback Tweets. Visit: https://claromes.github.io/waybacktweets -->\n"

        html += "<head>"
        html += '<meta charset="UTF-8">\n'
        html += (
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        )
        html += f"<title>@{self.username}'s archived tweets</title>\n"

        # Adds styling
        html += "<style>\n"
        html += "body { font-family: monospace; background-color: whitesmoke; color: #1c1e21; margin: 0; padding: 20px; }\n"
        html += ".container { display: flex; flex-wrap: wrap; gap: 20px; }\n"
        html += ".tweet { flex: 0 1 calc(33.33% - 20px); background-color: #ffffff; border: 1px solid #e2e2e2; border-radius: 10px; padding: 15px; overflow-wrap: break-word; margin: auto; width: 600px; }\n"
        html += ".tweet strong { font-weight: bold; }\n"
        html += ".tweet a { color: #000000; text-decoration: none; }\n"
        html += ".content { color: #000000; }\n"
        html += ".source { font-size: 12px; text-align: center; }\n"
        html += ".tweet a:hover { text-decoration: underline; }\n"
        html += "h1, h3 { text-align: center; }\n"
        html += "iframe { width: 600px; height: 600px; }\n"
        html += "input { position: absolute; opacity: 0; z-index: -1; }\n"
        html += ".accordion { margin: 10px; border-radius: 5px; overflow: hidden; box-shadow: 0 4px 4px -2px rgba(0, 0, 0, 0.4); }\n"
        html += ".accordion-label { display: flex; justify-content: space-between; padding: 1em; font-weight: bold; cursor: pointer; background: #000000; color: #ffffff; }\n"
        html += ".accordion-content { max-height: 0; padding: 0 1em; background: white; transition: all 0.35s; }\n"
        html += (
            "input:checked ~ .accordion-content { max-height: 100vh; padding: 1em; }\n"
        )
        html += ".pagination { text-align: center; margin-top: 20px; }\n"
        html += ".pagination a { margin: 0 5px; text-decoration: none; color: #000000; padding: 1px 2px; border-radius: 5px; }\n"
        html += ".pagination a:hover { background-color: #e2e2e2; }\n"
        html += ".pagination a.selected { background-color: #e2e2e2; color: #000000; font-weight: bold; }\n"
        html += "</style>\n"

        html += "</head>\n<body>\n"

        html += f"<h1>@{self.username}'s archived tweets</h1>\n"

        html += (
            '<p id="loading_first_page">Building pagination with JavaScript...</p>\n'
        )

        for page in range(1, total_pages + 1):
            html += (
                f'<div id="page_{page}" style="display:none;">\n'  # Starts a new page
            )
            html += '<div class="container">\n'

            start_index = (page - 1) * tweets_per_page
            end_index = min(start_index + tweets_per_page, len(self.json_path))

            for index in range(start_index, end_index):
                tweet = self.json_path[index]
                html += '<div class="tweet">\n'

                if not tweet["available_tweet_text"]:
                    iframe_src = {
                        "Archived Tweet": tweet["archived_tweet_url"],
                        "Parsed Archived Tweet": tweet["parsed_archived_tweet_url"],
                        "Original Tweet": tweet["original_tweet_url"],
                        "Parsed Tweet": tweet["parsed_tweet_url"],
                    }

                    for key, value in iframe_src.items():
                        key_cleaned = key.replace(" ", "_")

                        html += '<div class="accordion">\n'
                        html += f'<input type="checkbox" id="tab_{index}_{key_cleaned}" />\n'
                        html += f'<label class="accordion-label" for="tab_{index}_{key_cleaned}">Click to load the iframe from {key}</label>\n'
                        html += '<div class="accordion-content">\n'

                        html += f'<div id="loading_{index}_{key_cleaned}" class="loading">Loading...</div>\n'
                        html += f'<iframe id="iframe_{index}_{key_cleaned}" frameborder="0" scrolling="auto" loading="lazy" style="display: none;" onload="document.getElementById(\'loading_{index}_{key_cleaned}\').style.display=\'none\'; this.style.display=\'block\';"></iframe>\n'
                        html += "</div>\n"
                        html += "</div>\n"

                        html += """
                        <script>
                        // Loads the src attribute of the iframe tag
                        document.getElementById('tab_{index}_{key_cleaned}').addEventListener('change', function() {{
                            if (this.checked) {{
                                document.getElementById('loading_{index}_{key_cleaned}').style.display = 'block';
                                document.getElementById('iframe_{index}_{key_cleaned}').src = '{url}';
                            }}
                        }});
                        </script>
                        """.format(
                            index=index, url=value, key_cleaned=key_cleaned
                        )

                if tweet["available_tweet_text"]:
                    html += "<br>\n"
                    html += f'<p><strong class="content">Available Tweet Content:</strong> {tweet["available_tweet_text"]}</p>\n'
                    html += f'<p><strong class="content">Available Tweet Is Retweet:</strong> {tweet["available_tweet_is_RT"]}</p>\n'
                    html += f'<p><strong class="content">Available Tweet Username:</strong> {tweet["available_tweet_info"]}</p>\n'

                html += "<br>\n"
                html += f'<p><strong>Archived Tweet:</strong> <a href="{tweet["archived_tweet_url"]}" target="_blank">{tweet["archived_tweet_url"]}</a></p>\n'
                html += f'<p><strong>Parsed Archived Tweet:</strong> <a href="{tweet["parsed_archived_tweet_url"]}" target="_blank">{tweet["parsed_archived_tweet_url"]}</a></p>\n'
                html += f'<p><strong>Original Tweet:</strong> <a href="{tweet["original_tweet_url"]}" target="_blank">{tweet["original_tweet_url"]}</a></p>\n'
                html += f'<p><strong>Parsed Tweet:</strong> <a href="{tweet["parsed_tweet_url"]}" target="_blank">{tweet["parsed_tweet_url"]}</a></p>\n'
                html += f'<p><strong>Archived URL Key:</strong> {tweet["archived_urlkey"]}</p>\n'
                html += f'<p><strong>Archived Timestamp:</strong> {timestamp_parser(tweet["archived_timestamp"])} ({tweet["archived_timestamp"]})</p>\n'
                html += f'<p><strong>Archived mimetype:</strong> {tweet["archived_mimetype"]}</p>\n'
                html += f'<p><strong>Archived Statuscode:</strong> {tweet["archived_statuscode"]}</p>\n'
                html += (
                    f'<p><strong>Archived Digest:</strong> {tweet["archived_digest"]}\n'
                )
                html += f'<p><strong>Archived Length:</strong> {tweet["archived_length"]}</p>\n'
                html += "</div>\n"

            html += "</div>\n</div>\n"  # Closes the page div and the container

        html += "<br>\n"

        # Adds navigation for the pages
        html += '<div class="pagination">\n'
        for page in range(1, total_pages + 1):
            html += f'<a href="#" id="page_link_{page}" onclick="showPage({page})">{page}</a>\n'
        html += "</div>\n"

        html += '<br><p class="source">generated by <a href="https://claromes.github.io/waybacktweets/" target="_blank">Wayback Tweets↗</a></p>\n'

        html += """
        <script>
        // Function to show the selected page and hide the others
        function showPage(page) {{
            for (let i = 1; i <= {total_pages}; i++) {{
                document.getElementById('page_' + i).style.display = 'none';
                document.getElementById('page_link_' + i).classList.remove('selected');
            }}

            document.getElementById('page_' + page).style.display = 'block';
            document.getElementById('page_link_' + page).classList.add('selected');
        }}

        // Initializes the page to show only the first page
        document.addEventListener('DOMContentLoaded', (event) => {{
            showPage(1); // Shows only the first page on load
            document.getElementById('loading_first_page').style.display = 'none';
        }});
        </script>
        """.format(
            total_pages=total_pages
        )

        html += "</body>\n"
        html += "</html>"

        return html

    def save(self, html_content: str) -> None:
        """
        Saves the generated HTML string to a file.

        Args:
            html_content (str): The HTML string to be saved.
        """
        with open(self.html_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
