FROM ubuntu:22.10 AS base

RUN apt-get update
RUN apt-get install gnupg2 wget -y

RUN apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libcurl3-gnutls \
    libcurl3-nss \
    libcurl4

# RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb
RUN wget -q https://dl.google.com/linux/deb/pool/main/g/google-chrome-beta/google-chrome-beta_110.0.5481.77-1_amd64.deb -O chrome.deb
RUN dpkg -i chrome.deb 
RUN apt -f install -y
RUN rm chrome.deb

WORKDIR /deps
RUN wget -q https://chromedriver.storage.googleapis.com/110.0.5481.30/chromedriver_linux64.zip
# RUN wget -q https://chromedriver.storage.googleapis.com/109.0.5414.25/chromedriver_linux64.zip
RUN apt-get install -y unzip
RUN unzip chromedriver_linux64.zip

# Install and build Rust app
FROM rustlang/rust:nightly AS build

WORKDIR /app
COPY Cargo.lock .
COPY Cargo.toml .
RUN mkdir src && echo "// Dummy file" > src/lib.rs
RUN cargo build --release -Z sparse-registry

RUN rm src/*.rs
COPY ./src/ ./src
RUN cargo build --release -Z sparse-registry

# Final image to contain the application, with chrome and chromedriver installed.
FROM base AS final

WORKDIR /app
COPY --from=build /app/target/release/antscraper .
COPY start.sh .

ENV EMAIL=''
ENV EMAIL_PASSWORD=''
ENV EMAIL_SERVER=''

CMD ["/app/start.sh"]
