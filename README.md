# Telegram Product Cataloger Bot

A Telegram bot that automatically processes product images using AI vision to extract product information and store it in Google Sheets.

## Features

- AI-powered product image analysis
- Automatic product categorization and description
- Google Sheets integration for data storage
- Image hosting with public URLs
- Admin controls and user management

## Prerequisites

Before setting up the bot, you'll need:

1. **Telegram Bot Token**: Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Google Service Account**: For Google Sheets access
4. **Domain URL**: Your public domain where the bot will be hosted

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd <your-project-directory>
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Set up the following environment variables (or add them to Replit Secrets if using Replit):

#### Required Variables:
- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `OPENAI_API_KEY`: Your OpenAI API key
- `DOMAIN_URL`: Your public domain (e.g., "https://yourapp.replit.app")
- `GOOGLE_SHEET_ID`: The ID of your Google Sheets document

#### Optional Variables:
- `OPENAI_MODEL`: AI model to use (default: "gpt-4-vision-preview")
- `STATIC_SERVER_PORT`: Port for image server (default: 8000)
- `MAX_FILE_SIZE`: Maximum file upload size in bytes (default: 10485760 = 10MB)
- `LOG_LEVEL`: Logging level (default: "INFO")
- `DEBUG`: Enable debug mode (default: "False")

### 3. Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create a Service Account and download the JSON credentials
5. Save the credentials as `credentials.json` in the project root
6. Create a Google Sheet and share it with the service account email
7. Copy the Sheet ID from the URL and set it as `GOOGLE_SHEET_ID`

### 4. Running the Bot

#### Development Mode:
```bash
python run_simple.py
```

#### Production Mode:
```bash
python start_bot.py
```

The bot will automatically:
- Start the image hosting server
- Initialize the Telegram bot
- Create necessary upload directories
- Validate configuration

### 5. Bot Commands

- `/start` - Initialize the bot and get welcome message
- Send any product image to get automatic analysis

### 6. Project Structure

```
├── bot/
│   ├── handlers/          # Telegram message handlers
│   ├── services/          # Business logic services
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration settings
│   └── main.py           # Main bot application
├── static_server/        # Image hosting server
├── deploy/              # Deployment configurations
├── credentials.json     # Google service account credentials
├── requirements.txt     # Python dependencies
├── run_simple.py       # Simple development runner
└── start_bot.py        # Production runner
```

### 7. Troubleshooting

**Bot not responding:**
- Check if BOT_TOKEN is correctly set
- Verify the bot is running without errors
- Ensure the bot is not blocked by Telegram

**Image uploads failing:**
- Check DOMAIN_URL is correctly configured
- Verify the static server is running on the correct port
- Ensure upload directory has write permissions

**Google Sheets not updating:**
- Verify credentials.json is valid and accessible
- Check if the sheet is shared with the service account
- Confirm GOOGLE_SHEET_ID is correct

**AI analysis failing:**
- Verify OPENAI_API_KEY is valid and has credits
- Check if the OpenAI model is available
- Ensure image file size is within limits

## Deployment

The bot is designed to work with various hosting platforms including Replit, Heroku, and VPS servers. Make sure to:

1. Set all required environment variables
2. Upload the Google credentials file
3. Configure the DOMAIN_URL to match your hosting platform
4. Ensure the static server port is accessible publicly

## Support

For issues and questions, check the error logs and ensure all configuration variables are properly set.