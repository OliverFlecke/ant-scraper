use thirtyfour::prelude::*;
use tokio::time::{sleep, Duration};

use lettre::{
    transport::smtp::{
        authentication::{Credentials, Mechanism},
        extension::ClientId,
    },
    Message, SmtpTransport, Transport,
};

const URL: &str = "https://whatson.bfi.org.uk/imax/Online/default.asp";

#[tokio::main]
async fn main() -> WebDriverResult<()> {
    let email_options = EmailOptions::create_from_environment();
    match email_options {
        Ok(opts) => {
            if check_if_tickets_are_on_sale().await? {
                println!("Tickets ARE on sale");
                send_email(&opts);
            } else {
                println!("Tickts not on sale :(");
                send_email(&opts);
            }
        }
        Err(e) => {
            panic!("Email options missing: {:?}", e);
        }
    }
    Ok(())
}

#[derive(Debug)]
struct EmailOptions {
    email: String,
    password: String,
    server: String,
}

impl EmailOptions {
    pub fn create_from_environment() -> Result<Self, std::env::VarError> {
        use std::env;
        let email = env::var("EMAIL")?;
        let password = env::var("EMAIL_PASSWORD")?;
        let server = env::var("EMAIL_SERVER")?;

        Ok(Self {
            email,
            password,
            server,
        })
    }
}

fn send_email(options: &EmailOptions) {
    let message = Message::builder()
        .from(format!("Me <{}>", options.email).parse().unwrap())
        .reply_to(format!("Yuin <{}>", options.email).parse().unwrap())
        .to(format!("Hei <{}>", options.email).parse().unwrap())
        .subject("Happy new year")
        .body(String::from("Be happy!"))
        .unwrap();

    let creds = Credentials::new(options.email.to_string(), options.password.to_string());

    let mailer = SmtpTransport::starttls_relay(options.server.as_str())
        .unwrap()
        .hello_name(ClientId::Domain("localhost".to_string()))
        .credentials(creds)
        .authentication(vec![Mechanism::Login])
        .build();

    // Send the email
    match mailer.send(&message) {
        Ok(_) => println!("Email sent successfully!"),
        Err(e) => println!("Could not send email: {:?}", e),
    }
}

/// Visit BFI's website to check if tickets are on sale yet.
async fn check_if_tickets_are_on_sale() -> WebDriverResult<bool> {
    let mut caps = DesiredCapabilities::chrome();
    caps.set_headless()?;
    let driver = WebDriver::new("http://localhost:9515", caps).await?;

    driver.goto(URL).await?;
    // Wait until iframe is also loaded.
    sleep(Duration::from_millis(1000)).await;

    let frame = driver.find(By::Id("calendar-widget-frame")).await?;
    frame.enter_frame().await?;

    let day = driver.find(By::Id("ww3d5")).await?;

    // assert_eq!(day.text().await?, "24");
    let is_on_sale = day.class_name().await?.is_some();

    // Always explicitly close the browser.
    driver.quit().await?;

    Ok(is_on_sale)
}
