import sys
sys.path.append("src")
import jjjxutils

def generate_png():
    selenium = jjjxutils.web.browser_client.get_selenium()
    browser_client = jjjxutils.web.browser_client.ChromeClient(selenium)
    html_renderer = jjjxutils.rendering.html.HtmlRenderer(browser_client)
    html_renderer.save_as_png("https://google.com", "test.png")


if __name__ == "__main__":
    generate_png()
