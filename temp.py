from common.browser import launch_browser

playwright, browser, context, page = launch_browser()

page.pause()