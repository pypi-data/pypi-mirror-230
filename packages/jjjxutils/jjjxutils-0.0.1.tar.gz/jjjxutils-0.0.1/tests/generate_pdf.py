import sys
sys.path.append("src")
import jjjxutils

def generate_pdf():
    selenium = jjjxutils.web.browser_client.get_selenium()
    browser_client = jjjxutils.web.browser_client.ChromeClient(selenium)
    html_renderer = jjjxutils.rendering.html.HtmlRenderer(browser_client)
    html_renderer.save_as_pdf("https://google.com", "test.pdf")


if __name__ == "__main__":
    generate_pdf()
