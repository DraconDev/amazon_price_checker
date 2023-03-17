import email
import json
import smtplib
import ssl
import time

import requests
import schedule
from bs4 import BeautifulSoup


def main():
    url = "https://www.amazon.co.uk/Blue-Recording-Streaming-Condenser-Adjustable/dp/B00N1YPXW2/ref=sr_1_125?content-id=amzn1.sym.222608eb-f887-4329-bb45-ef37761e5b56&pd_rd_r=d67a9db9-a376-46d1-9369-5e90693895aa&pd_rd_w=gMU8i&pd_rd_wg=01rrq&pf_rd_p=222608eb-f887-4329-bb45-ef37761e5b56&pf_rd_r=P2QBE3C7EPCN245E6YXQ&refinements=p_72%3A405434031%2Cp_36%3A-20000&rnid=405443031&s=musical-instruments&sr=1-125"

    def get_price(url):
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
            "Accept-Language": "en-US, en;q=0.5",
        }
        response = requests.get(
            url,
            headers=HEADERS,
        )
        soup = BeautifulSoup(
            response.content,
            "html.parser",
        )
        with open("test.html", "w", encoding="utf-8") as file:
            file.write(str(soup))

        item_price = float(soup.find("span", "a-offscreen").text[1:])
        # title = soup.find("h1", id="title")
        title = " ".join(soup.find("h1", id="title").text.strip().split(" ")[:3])

        check_deal(item_price, title, 60)

    def tracking(get_price):
        get_price(url)
        schedule.every().hour.do(get_price)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def check_deal(price, title, deal):
        if price < deal:
            with open("../../_login/email/cred_json.json", "r") as file:
                email, _, password = json.load(file).values()
            send_email(
                email,
                password,
                email,
                f"Price alert for {title}",
                f"{title} is {price}",
            )

    def send_email(sender_email, password, recipient_email, subject, body):
        smtp_server = "smtp.gmail.com"
        port = 465  # SSL
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as smtp:
            smtp.login(sender_email, password)

            message = email.message.EmailMessage()
            message["To"] = recipient_email
            message["From"] = sender_email
            message["Subject"] = subject
            message.set_content(body)

            smtp.send_message(message)

            smtp.quit()

    tracking(get_price)


if __name__ == "__main__":
    main()
