use thirtyfour::prelude::*;
use tokio::time::{sleep, Duration};

const URL: &str = "https://whatson.bfi.org.uk/imax/Online/default.asp";

#[tokio::main]
async fn main() -> WebDriverResult<()> {
    Ok(())
}

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
