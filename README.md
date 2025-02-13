# Instagram Post Downloader

An application that allows downloading Instagram posts from public or private (if you follow them) profiles using a very shitty graphical user interface.

## Features
- Download photos and videos from Instagram posts
- Simple and intuitive GUI
- Two-factor authentication support
- Configurable number of posts to download
- Progress tracking (ish) 

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### NOTE: 📝 You will most likely be rate-limited to 12 posts. This is attached to the individual device and will present itself as the error 
```
JSON Query to graphql/query: 401 Unauthorized - "fail" status, message "Please wait a few minutes before you try again." when accessing https://www.instagram.com/graphql/query
```

1. Run the application:
```bash
python instagram_downloader.py
```

2. Enter your Instagram credentials
3. Enter the target username whose posts you want to download
4. Optionally specify the number of posts to download
5. Click "Download Posts"

## Safety Considerations

This tool should be used responsibly and in accordance with Instagram's terms of service. Be aware that:
- Excessive usage may lead to temporary blocks or permanent bans
- Using the tool with a dedicated account is recommended
- Take breaks between large downloads
- Respect content creators' rights

## Dependencies
- Python 3.6+
- tkinter
- instaloader

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This tool is for educational purposes only. Users are responsible for how they use this software and should comply with Instagram's terms of service.
