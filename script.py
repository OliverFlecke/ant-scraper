#!/usr/bin/env python
import os
import asyncio
import smtplib
from email.message import EmailMessage
from playwright.async_api import async_playwright
from asyncio import sleep

URL = 'https://whatson.bfi.org.uk/imax/Online/default.asp'

async def main():
    while True:
        await check_if_tickets_are_on_sale()
        await sleep(10)

async def check_if_tickets_are_on_sale():
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
            print("Tickets are on sale")
            send_email(f'YES! Tickets are on sale now, go buy them immediately!\n\nYou can by them here: {URL}')
        else:
            print("Not on sale yet")
            send_email(f'No, they are still not on sale...\n\nYou can check here: {URL}')

        await browser.close()

def send_email(content: str):
    outlook_email = os.environ.get('OUTLOOK_EMAIL')
    password = os.environ.get('OUTLOOK_PASSWORD')

    msg = EmailMessage()
    msg.set_content(content)
    msg['From'] = outlook_email
    msg['To'] = [outlook_email]
    msg['Subject'] = f'Are Ant-man tickets on sale yet?'

    server = smtplib.SMTP('smtp-mail.outlook.com', port=587)
    server.ehlo()
    server.starttls()
    server.login(outlook_email, password)
    server.send_message(msg)
    server.quit()

asyncio.run(main())
