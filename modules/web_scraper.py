import os
import re
import time
import json
from typing import List, Dict, Optional
from datetime import datetime

class JobPortalScraper:
    def __init__(self, download_dir: str = "", config: dict = None):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.config = config or {}
        if not download_dir:
            self.download_dir = os.path.join(os.path.dirname(__file__), "..", "data", "scraped_cvs")
        else:
            self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def _init_browser(self):
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context(
            accept_downloads=True,
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        self.page = self.context.new_page()

    def _save_screenshot(self, name: str):
        try:
            path = os.path.join(self.download_dir, f"debug_{name}_{int(time.time())}.png")
            self.page.screenshot(path=path)
            print(f"[SCRAPER] Screenshot saved: {path}")
        except Exception as e:
            print(f"[SCRAPER] Screenshot failed: {e}")

    def _close_browser(self):
        try:
            if self.context:
                self.context.close()
        except: pass
        try:
            if self.browser:
                self.browser.close()
        except: pass
        try:
            if self.playwright:
                self.playwright.stop()
        except: pass

    def _save_cv_text(self, filename: str, content: str, source: str, url: str, keyword: str, candidate_name: str = ""):
        cv_path = os.path.join(self.download_dir, filename)
        with open(cv_path, "w", encoding="utf-8") as f:
            f.write(f"Source: {source}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Keyword: {keyword}\n")
            f.write(f"Candidate: {candidate_name}\n")
            f.write(f"Scraped: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n")
            f.write(content)
        return cv_path

    def _save_cv_json(self, candidate_data: dict, source: str, keyword: str):
        safe_name = re.sub(r'[^\w\s]', '', candidate_data.get("name", "unknown"))[:30]
        safe_name = re.sub(r'\s+', '_', safe_name.strip())
        filename = f"{source}_{safe_name}_{int(time.time())}.json"
        path = os.path.join(self.download_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "source": source,
                "keyword": keyword,
                "scraped_at": datetime.now().isoformat(),
                "candidate": candidate_data,
            }, f, indent=2, ensure_ascii=False)
        return path

    def scrape_jobstreet(self, keyword: str, max_cvs: int = 5) -> List[str]:
        downloaded = []
        email = self.config.get("jobstreet_email", "")
        password = self.config.get("jobstreet_password", "")
        if not email or not password:
            print("[SCRAPER] Jobstreet employer credentials not set in Settings!")
            return downloaded
        try:
            self._init_browser()
            print(f"[SCRAPER] Jobstreet RPA: Login as {email}")
            self.page.goto("https://www.jobstreet.co.id/", timeout=60000)
            time.sleep(2)
            self._save_screenshot("js_homepage")

            login_btn = self.page.locator('a:has-text("Untuk Perusahaan"), a:has-text("Employer"), a[href*="employer"]')
            if login_btn.count() > 0:
                login_btn.first.click()
                time.sleep(2)
                self._save_screenshot("js_employer_page")
            else:
                self.page.goto("https://employer.jobstreet.co.id/login", timeout=60000)
                time.sleep(2)

            self.page.fill('input[type="email"], input[name="email"], input[placeholder*="email"]', email)
            time.sleep(1)
            next_btn = self.page.locator('button:has-text("Next"), button:has-text("Lanjut"), button[type="submit"]')
            if next_btn.count() > 0:
                next_btn.first.click()
                time.sleep(2)

            self.page.fill('input[type="password"], input[name="password"], input[placeholder*="kata sandi"]', password)
            time.sleep(1)
            login_submit = self.page.locator('button:has-text("Login"), button:has-text("Masuk"), button[type="submit"]')
            if login_submit.count() > 0:
                login_submit.first.click()
            else:
                self.page.keyboard.press("Enter")
            time.sleep(5)
            self._save_screenshot("js_logged_in")

            self.page.goto("https://employer.jobstreet.co.id/candidate/search", timeout=60000)
            time.sleep(3)
            self._save_screenshot("js_candidate_search")

            search_input = self.page.locator('input[type="text"], input[placeholder*="Cari"], input[placeholder*="Search"], input[placeholder*="kandidat"]')
            if search_input.count() > 0:
                search_input.first.fill(keyword)
                self.page.keyboard.press("Enter")
                time.sleep(3)
                self._save_screenshot("js_search_results")
                print(f"[SCRAPER] Searching candidates for '{keyword}'")

            candidate_cards = self.page.locator('div[class*="candidate"], div[class*="card"], a[class*="candidate"], li[class*="candidate"]').first
            card_count = 0
            for attempt in range(3):
                cards = self.page.locator('div[class*="candidate"], div[class*="card"]')
                card_count = cards.count()
                if card_count > 0:
                    break
                time.sleep(2)

            count = min(card_count, max_cvs)
            print(f"[SCRAPER] Found {card_count} candidates for '{keyword}', processing {count}")

            for i in range(count):
                try:
                    cards = self.page.locator('div[class*="candidate"], div[class*="card"]')
                    card = cards.nth(i)
                    card.click()
                    time.sleep(3)
                    self._save_screenshot(f"js_candidate_{i+1}")

                    candidate_name = ""
                    name_el = self.page.locator('h1, h2, h3, h4, [class*="name"], [class*="title"]').first
                    if name_el.count() > 0:
                        candidate_name = name_el.inner_text()[:50]

                    page_text = self.page.inner_text("body")

                    cv_filename = f"jobstreet_{keyword.replace(' ', '_')}_{i+1}.txt"
                    cv_path = self._save_cv_text(
                        filename=cv_filename,
                        content=page_text,
                        source="Jobstreet",
                        url=self.page.url,
                        keyword=keyword,
                        candidate_name=candidate_name,
                    )
                    downloaded.append(cv_path)
                    print(f"[SCRAPER] Saved CV #{i+1}: {candidate_name or 'Unknown'}")

                    cv_download_btn = self.page.locator(
                        'a:has-text("Download"), button:has-text("Download"), a[href*="download"], a[href*="cv"], a[href*="resume"]'
                    )
                    if cv_download_btn.count() > 0:
                        try:
                            with self.page.expect_download(timeout=10000) as dl_info:
                                cv_download_btn.first.click()
                            dl = dl_info.value
                            dl_path = os.path.join(self.download_dir, f"jobstreet_{keyword.replace(' ', '_')}_{i+1}_cv.pdf")
                            dl.save_as(dl_path)
                            print(f"[SCRAPER] CV PDF downloaded: {dl_path}")
                        except Exception as e:
                            print(f"[SCRAPER] CV download link not available: {e}")

                    back_btn = self.page.locator('button:has-text("Back"), button:has-text("Kembali"), a:has-text("Back")')
                    if back_btn.count() > 0:
                        back_btn.first.click()
                    else:
                        self.page.goto("https://employer.jobstreet.co.id/candidate/search", timeout=60000)
                    time.sleep(2)

                except Exception as e:
                    print(f"[SCRAPER] Error on candidate #{i+1}: {e}")
                    self._save_screenshot(f"js_error_{i+1}")
                    continue

        except Exception as e:
            print(f"[SCRAPER] Error scraping Jobstreet: {e}")
            self._save_screenshot("js_fatal_error")
        finally:
            self._close_browser()

        print(f"[SCRAPER] Downloaded {len(downloaded)} CVs from Jobstreet")
        return downloaded

    def scrape_glints(self, keyword: str, max_cvs: int = 5) -> List[str]:
        downloaded = []
        email = self.config.get("glints_email", "")
        password = self.config.get("glints_password", "")
        if not email or not password:
            print("[SCRAPER] Glints employer credentials not set in Settings!")
            return downloaded
        try:
            self._init_browser()
            print(f"[SCRAPER] Glints RPA: Login as {email}")
            self.page.goto("https://glints.com/id/employer/login", timeout=60000)
            time.sleep(3)
            self._save_screenshot("gl_login")

            self.page.fill('input[type="email"], input[name="email"]', email)
            time.sleep(1)
            self.page.fill('input[type="password"], input[name="password"]', password)
            time.sleep(1)
            login_btn = self.page.locator('button:has-text("Login"), button:has-text("Masuk"), button[type="submit"]')
            if login_btn.count() > 0:
                login_btn.first.click()
            else:
                self.page.keyboard.press("Enter")
            time.sleep(5)
            self._save_screenshot("gl_logged_in")

            self.page.goto("https://glints.com/id/employer/talent-search", timeout=60000)
            time.sleep(3)
            self._save_screenshot("gl_talent_search")

            search_input = self.page.locator('input[type="text"], input[placeholder*="Cari"], input[placeholder*="Search"], input[placeholder*="talent"]')
            if search_input.count() > 0:
                search_input.first.fill(keyword)
                self.page.keyboard.press("Enter")
                time.sleep(3)
                self._save_screenshot("gl_search_results")
                print(f"[SCRAPER] Searching talent for '{keyword}'")

            talent_count = 0
            for attempt in range(3):
                talent_cards = self.page.locator('div[class*="talent"], div[class*="card"], a[class*="talent"]')
                talent_count = talent_cards.count()
                if talent_count > 0:
                    break
                time.sleep(2)

            count = min(talent_count, max_cvs)
            print(f"[SCRAPER] Found {talent_count} talents for '{keyword}', processing {count}")

            for i in range(count):
                try:
                    cards = self.page.locator('div[class*="talent"], div[class*="card"]')
                    card = cards.nth(i)
                    card.click()
                    time.sleep(3)
                    self._save_screenshot(f"gl_talent_{i+1}")

                    candidate_name = ""
                    name_el = self.page.locator('h1, h2, h3, [class*="name"]').first
                    if name_el.count() > 0:
                        candidate_name = name_el.inner_text()[:50]

                    page_text = self.page.inner_text("body")

                    cv_filename = f"glints_{keyword.replace(' ', '_')}_{i+1}.txt"
                    cv_path = self._save_cv_text(
                        filename=cv_filename,
                        content=page_text,
                        source="Glints",
                        url=self.page.url,
                        keyword=keyword,
                        candidate_name=candidate_name,
                    )
                    downloaded.append(cv_path)
                    print(f"[SCRAPER] Saved talent #{i+1}: {candidate_name or 'Unknown'}")

                    dl_btn = self.page.locator(
                        'a:has-text("Download"), button:has-text("Download"), a[href*="resume"], a[href*="cv"]'
                    )
                    if dl_btn.count() > 0:
                        try:
                            with self.page.expect_download(timeout=10000) as dl_info:
                                dl_btn.first.click()
                            dl = dl_info.value
                            dl_path = os.path.join(self.download_dir, f"glints_{keyword.replace(' ', '_')}_{i+1}_cv.pdf")
                            dl.save_as(dl_path)
                            print(f"[SCRAPER] CV PDF downloaded: {dl_path}")
                        except Exception as e:
                            print(f"[SCRAPER] CV download failed: {e}")

                    back_btn = self.page.locator('button:has-text("Back"), button:has-text("Kembali")')
                    if back_btn.count() > 0:
                        back_btn.first.click()
                    else:
                        self.page.go_back()
                    time.sleep(2)

                except Exception as e:
                    print(f"[SCRAPER] Error on talent #{i+1}: {e}")
                    self._save_screenshot(f"gl_error_{i+1}")
                    continue

        except Exception as e:
            print(f"[SCRAPER] Error scraping Glints: {e}")
            self._save_screenshot("gl_fatal_error")
        finally:
            self._close_browser()

        print(f"[SCRAPER] Downloaded {len(downloaded)} CVs from Glints")
        return downloaded

    def scrape_all(self, keyword: str, max_cvs: int = 3) -> Dict[str, List[str]]:
        result = {}
        js_email = self.config.get("jobstreet_email", "")
        gl_email = self.config.get("glints_email", "")
        if js_email:
            result["jobstreet"] = self.scrape_jobstreet(keyword, max_cvs)
        if gl_email:
            result["glints"] = self.scrape_glints(keyword, max_cvs)
        if not js_email and not gl_email:
            print("[SCRAPER] No employer credentials configured. Set in Settings > Scraper.")
        return result

    def get_downloaded_files(self) -> List[str]:
        return [os.path.join(self.download_dir, f)
                for f in os.listdir(self.download_dir)
                if os.path.isfile(os.path.join(self.download_dir, f))]
