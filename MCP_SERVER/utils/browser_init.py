from core.browser_controller import MockBrowserController, PlaywrightBrowserController, BrowserControllerInterface
from core.config import settings
import asyncio


async def get_browser_controller() -> BrowserControllerInterface:
    """
    A factory function that returns the appropriate browser controller.

    This function checks if the PlaywrightBrowserController is available and, if so,
    initializes and returns it. Otherwise, it returns a MockBrowserController.

    Returns:
        BrowserControllerInterface: An instance of a browser controller.
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
    Initializes the browser controller with the proper settings.

    Returns:
        BrowserControllerInterface: An instance of an initialized browser controller.
    """
    controller = await get_browser_controller()
    return controller