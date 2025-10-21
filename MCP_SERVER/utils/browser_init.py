from core.browser_controller import MockBrowserController, PlaywrightBrowserController, BrowserControllerInterface
from core.config import settings
import asyncio


async def get_browser_controller() -> BrowserControllerInterface:
    """
    Factory function to get the appropriate browser controller
    """
    # Use Playwright controller if available, otherwise use mock
    if PlaywrightBrowserController is not None:
        controller = PlaywrightBrowserController()
        await controller.initialize()
        return controller
    else:
        return MockBrowserController()


async def initialize_browser():
    """
    Initialize the browser controller with proper settings
    """
    controller = await get_browser_controller()
    return controller