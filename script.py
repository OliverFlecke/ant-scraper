#!/usr/bin/env python
import asyncio
from playwright.async_api import async_playwright
from asyncio import sleep

URL = 'https://whatson.bfi.org.uk/imax/Online/default.asp'

async def main():
    async with async_playwright() as p:
        browser_type = p.firefox
        browser = await browser_type.launch()
        page = await browser.new_page()
        await page.goto(URL)
        frame = page.frame_locator('#calendar-widget-frame')
        month = frame.get_by_text('February 2023')
        while not await month.is_visible():
            button = frame.get_by_title('Next month')
            await button.click()
            await sleep(1)
            frame = page.frame_locator('#calendar-widget-frame')
            month = frame.get_by_text('February 2023')

        day = frame.get_by_text('24')
        isAvailable = await day.get_attribute('class') != None
        if isAvailable:
            print("tickets are on sale")
        else:
            print("Not on sale yet")

        await page.screenshot(path=f'example-{browser_type.name}.png')
        await browser.close()

asyncio.run(main())