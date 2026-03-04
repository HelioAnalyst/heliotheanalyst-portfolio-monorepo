"""Browser management with anti-detection features."""

import random
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class BrowserManager:
    """Manage browser instances with anti-detection."""

    def __init__(
        self,
        headless: bool = True,
        user_agent_rotation: bool = True,
        delay_min: float = 1.0,
        delay_max: float = 3.0,
        timeout: int = 30,
    ) -> None:
        """Initialize browser manager.

        Args:
            headless: Run browser in headless mode.
            user_agent_rotation: Rotate user agents.
            delay_min: Minimum delay between requests.
            delay_max: Maximum delay between requests.
            timeout: Page load timeout in seconds.
        """
        self.headless = headless
        self.user_agent_rotation = user_agent_rotation
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout
        self._driver: Optional[WebDriver] = None

    def _get_random_user_agent(self) -> str:
        """Get random user agent.

        Returns:
            User agent string.
        """
        return random.choice(USER_AGENTS)

    def _create_options(self) -> Options:
        """Create Chrome options with anti-detection.

        Returns:
            Configured Chrome options.
        """
        options = Options()

        if self.headless:
            options.add_argument("--headless=new")

        # Anti-detection options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")

        # Window size
        options.add_argument("--window-size=1920,1080")

        # User agent
        if self.user_agent_rotation:
            options.add_argument(f"--user-agent={self._get_random_user_agent()}")

        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def start(self) -> WebDriver:
        """Start browser instance.

        Returns:
            WebDriver instance.
        """
        options = self._create_options()

        # Try to use chromedriver from PATH
        try:
            self._driver = webdriver.Chrome(options=options)
        except Exception:
            # Fallback to webdriver-manager
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=options)

        # Execute CDP commands to prevent detection
        self._driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            },
        )

        self._driver.set_page_load_timeout(self.timeout)
        return self._driver

    def stop(self) -> None:
        """Stop browser instance."""
        if self._driver:
            self._driver.quit()
            self._driver = None

    def random_delay(self) -> None:
        """Wait for random delay."""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)

    def get_driver(self) -> WebDriver:
        """Get current driver or start new one.

        Returns:
            WebDriver instance.
        """
        if not self._driver:
            return self.start()
        return self._driver

    def wait_for_element(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        timeout: Optional[int] = None,
    ) -> Optional:
        """Wait for element to be present.

        Args:
            selector: Element selector.
            by: Selector type.
            timeout: Wait timeout.

        Returns:
            WebElement or None.
        """
        driver = self.get_driver()
        wait = WebDriverWait(driver, timeout or self.timeout)

        try:
            return wait.until(EC.presence_of_element_located((by, selector)))
        except Exception:
            return None

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""
        driver = self.get_driver()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)


class MockBrowserManager:
    """Mock browser manager for testing without Chrome."""

    def __init__(
        self,
        headless: bool = True,
        user_agent_rotation: bool = True,
        delay_min: float = 0.1,
        delay_max: float = 0.3,
        timeout: int = 30,
    ) -> None:
        """Initialize mock browser manager."""
        self.headless = headless
        self.user_agent_rotation = user_agent_rotation
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout
        self._pages_visited: list[str] = []
        self._current_page: int = 0

    def start(self) -> "MockBrowserManager":
        """Start mock browser."""
        return self

    def stop(self) -> None:
        """Stop mock browser."""
        pass

    def random_delay(self) -> None:
        """Minimal delay for mock."""
        time.sleep(0.01)

    def get_driver(self) -> "MockBrowserManager":
        """Get mock driver."""
        return self

    def get(self, url: str) -> None:
        """Mock navigate to URL."""
        self._pages_visited.append(url)
        self._current_page += 1

    def find_elements(self, *args, **kwargs) -> list:
        """Mock find elements."""
        return []

    def find_element(self, *args, **kwargs):
        """Mock find element."""
        return None

    @property
    def page_source(self) -> str:
        """Mock page source."""
        return "<html><body>Mock page</body></html>"

    @property
    def current_url(self) -> str:
        """Mock current URL."""
        return self._pages_visited[-1] if self._pages_visited else ""
