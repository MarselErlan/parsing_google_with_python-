from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path

def extract_job_description_from_url_and_html_analysis(url: str, file_index: int = 0) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)  # Wait for content to load
            html = page.content()
            browser.close()

            soup = BeautifulSoup(html, "html.parser")
            body = soup.body

            output_lines = [f"URL: {url}\n", "="*60 + "\n"]

            # 🧱 Div-by-div inspection
            output_lines.append("🔎 Div Analysis (from <body>):\n\n")
            all_visible_text = []

            for i, div in enumerate(body.find_all("div", recursive=True), start=1):
                div_class = div.get("class")
                div_id = div.get("id")
                output_lines.append(f"[Div {i}]\n")
                output_lines.append(f"  ➤ class: {div_class}\n")
                output_lines.append(f"  ➤ id: {div_id}\n")

                child_tags = {tag.name for tag in div.find_all(recursive=False)}
                output_lines.append(f"  ➤ child tags: {', '.join(child_tags)}\n")

                # Get direct visible text from <p>, <li>, etc.
                for tag in div.find_all(["p", "li", "h1", "h2", "h3", "ul", "ol"], recursive=True):
                    text = tag.get_text(strip=True)
                    if text:
                        output_lines.append(f"    • {tag.name}: {text}\n")
                        all_visible_text.append(text)

                output_lines.append("\n")

            # 🧾 Form field detection
            output_lines.append("\n🧾 Form Fields:\n")
            for input_tag in body.find_all("input"):
                label = soup.find("label", {"for": input_tag.get("id")})
                field_info = {
                    "Label": label.get_text(strip=True) if label else "N/A",
                    "Type": input_tag.get("type", "text"),
                    "ID": input_tag.get("id", "N/A"),
                    "Required": input_tag.get("aria-required", "false"),
                    "Autocomplete": input_tag.get("autocomplete", "N/A")
                }
                output_lines.append(str(field_info) + "\n")

            # Save to file
            output_dir = Path("job_div_analysis")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"job_details_{file_index}.txt"

            with open(output_file, "w", encoding="utf-8") as f:
                f.writelines(output_lines)

            # Return content block
            return "\n".join(all_visible_text).strip() if len(all_visible_text) > 5 else "No job description available."

        except Exception as e:
            browser.close()
            return "No job description available."
