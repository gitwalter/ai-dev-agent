"""
Playwright Helper Script - Runs Playwright commands in a separate process.
This bypasses Jupyter's event loop issues on Windows.
"""
import sys
import json
from playwright.sync_api import sync_playwright

def run_command(command: str, args: dict) -> dict:
    """Execute a Playwright command and return results."""
    result = {"success": False, "data": None, "error": None}
    
    try:
        with sync_playwright() as p:
            # Use 'msedge' channel to use system Edge browser (bypasses Group Policy blocks)
            browser = p.chromium.launch(headless=True, channel='msedge')
            
            if command == "get_tools":
                # Return available tool names
                result["data"] = [
                    "click_element",
                    "navigate_browser", 
                    "previous_webpage",
                    "extract_text",
                    "extract_hyperlinks",
                    "get_elements",
                    "current_webpage"
                ]
                result["success"] = True
                
            elif command == "navigate":
                url = args.get("url", "https://example.com")
                page = browser.new_page()
                page.goto(url)
                result["data"] = {
                    "title": page.title(),
                    "url": page.url
                }
                page.close()
                result["success"] = True
                
            elif command == "get_page_content":
                url = args.get("url", "https://example.com")
                page = browser.new_page()
                page.goto(url)
                result["data"] = {
                    "title": page.title(),
                    "url": page.url,
                    "content": page.content()[:5000]  # Limit content size
                }
                page.close()
                result["success"] = True
                
            elif command == "screenshot":
                url = args.get("url", "https://example.com")
                path = args.get("path", "screenshot.png")
                page = browser.new_page()
                page.goto(url)
                page.screenshot(path=path)
                result["data"] = {"path": path, "title": page.title()}
                page.close()
                result["success"] = True
                
            elif command == "test":
                # Simple connectivity test
                page = browser.new_page()
                page.goto("https://playwright.dev")
                result["data"] = {"title": page.title(), "status": "OK"}
                page.close()
                result["success"] = True
            
            elif command == "navigate_and_click":
                # Navigate to URL and click an element
                url = args.get("url", "https://example.com")
                selector = args.get("selector", "a")
                wait_until = args.get("wait_until", "networkidle")
                
                page = browser.new_page()
                page.goto(url, wait_until=wait_until)
                
                initial_url = page.url
                initial_title = page.title()
                
                # Click the element
                page.click(selector)
                page.wait_for_load_state("networkidle")
                
                result["data"] = {
                    "initial_url": initial_url,
                    "initial_title": initial_title,
                    "final_url": page.url,
                    "final_title": page.title()
                }
                page.close()
                result["success"] = True
            
            elif command == "scrape_quotes":
                # Demo: Scrape quotes.toscrape.com with pagination
                page = browser.new_page()
                page.goto("https://quotes.toscrape.com/", wait_until="networkidle")
                
                pages_data = []
                
                # Get first page data
                title = page.title()
                url = page.url
                quotes = page.query_selector_all(".quote .text")
                quote_texts = [q.inner_text()[:100] for q in quotes[:3]]  # First 3 quotes
                
                pages_data.append({
                    "page": 1,
                    "url": url,
                    "quotes_preview": quote_texts
                })
                
                # Click next and get second page
                next_btn = page.query_selector("li.next > a")
                if next_btn:
                    next_btn.click()
                    page.wait_for_load_state("networkidle")
                    
                    quotes = page.query_selector_all(".quote .text")
                    quote_texts = [q.inner_text()[:100] for q in quotes[:3]]
                    
                    pages_data.append({
                        "page": 2,
                        "url": page.url,
                        "quotes_preview": quote_texts
                    })
                
                result["data"] = {
                    "title": title,
                    "pages": pages_data
                }
                page.close()
                result["success"] = True
            
            elif command == "login_demo":
                # Demo: Login to saucedemo.com and get product list
                url = args.get("url", "https://www.saucedemo.com/")
                username = args.get("username", "standard_user")
                password = args.get("password", "secret_sauce")
                
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                
                # Fill login form
                page.fill("#user-name", username)
                page.fill("#password", password)
                page.click("#login-button")
                
                # Wait for inventory page
                page.wait_for_url("**/inventory.html", timeout=10000)
                
                # Read product names
                items = page.query_selector_all(".inventory_item_name")
                item_names = [item.text_content() for item in items]
                
                result["data"] = {
                    "logged_in": True,
                    "url": page.url,
                    "products": item_names
                }
                page.close()
                result["success"] = True
            
            elif command == "fill_form":
                # Generic form filling command
                url = args.get("url", "https://example.com")
                fields = args.get("fields", {})  # {selector: value}
                submit_selector = args.get("submit", None)
                
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded")
                
                # Fill each field
                for selector, value in fields.items():
                    page.fill(selector, value)
                
                # Click submit if provided
                if submit_selector:
                    page.click(submit_selector)
                    page.wait_for_load_state("networkidle")
                
                result["data"] = {
                    "url": page.url,
                    "title": page.title()
                }
                page.close()
                result["success"] = True
                
            else:
                result["error"] = f"Unknown command: {command}"
                
            browser.close()
            
    except Exception as e:
        result["error"] = str(e)
        
    return result


if __name__ == "__main__":
    # Read command from stdin or args
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    else:
        # Read from stdin
        input_data = json.loads(sys.stdin.read())
        command = input_data.get("command", "test")
        args = input_data.get("args", {})
    
    result = run_command(command, args)
    print(json.dumps(result))

