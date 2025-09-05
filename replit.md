# Overview

The Telegram Product Cataloger Bot is now fully built and deployed! This AI-powered automation tool analyzes product photos sent via Telegram and creates structured catalog entries. Users send product images to the bot, which uses OpenAI's Vision API to extract product details like type, color, brand, and description. The analyzed data is then stored in Google Sheets for inventory management. The bot includes a static file server for hosting uploaded images and provides admin commands for configuration management.

**Current Status**: ✅ **DEPLOYED AND RUNNING**

## Recent Changes

- **2025-09-05**: Complete bot implementation finished
  - All core services implemented (AI Vision, Image Handler, Google Sheets)
  - Bot handlers created for start commands, photo processing, and admin functions
  - Static file server set up for image hosting
  - Environment configuration completed with API keys
  - Bot successfully deployed and running

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Aiogram 3.x**: Modern asynchronous Telegram bot framework with built-in FSM (Finite State Machine) support for managing conversation flows
- **Handler-based routing**: Organized into separate modules for start commands, photo processing, and admin functions
- **Memory storage**: Uses in-memory storage for conversation states, suitable for single-instance deployments

## AI Integration
- **OpenAI Vision API**: Primary service for analyzing product images using GPT-4 Vision model
- **Structured prompts**: Uses controlled vocabulary lists for product types and colors to ensure consistent categorization
- **Fallback handling**: Graceful degradation when AI services are unavailable

## Image Management
- **Multi-stage processing**: Downloads highest quality images from Telegram, validates file size/format, stores locally
- **PIL integration**: Image validation and potential format conversion using Python Imaging Library
- **Static file serving**: FastAPI-based server hosts uploaded images with public URLs for AI analysis

## Data Storage
- **Google Sheets API**: Primary data store using service account authentication for automated access
- **Async operations**: Non-blocking spreadsheet operations using gspread-asyncio
- **Structured headers**: Predefined column structure for consistent data organization

## Configuration Management
- **Environment-based**: All sensitive data (API keys, tokens) managed through environment variables
- **Controlled vocabularies**: Hardcoded lists for product types and colors to maintain data consistency
- **Flexible deployment**: Supports both development and production configurations

## Service Architecture
- **Modular design**: Separate services for image handling, AI analysis, and sheets management
- **Error isolation**: Individual service failures don't crash the entire bot
- **Async/await pattern**: Non-blocking operations throughout the application stack

# External Dependencies

## Required APIs
- **Telegram Bot API**: Core bot functionality and message handling
- **OpenAI API**: GPT-4 Vision for product image analysis
- **Google Sheets API**: Data storage and retrieval operations
- **Google Drive API**: File access permissions for sheets integration

## Infrastructure Services
- **FastAPI**: Static file server for image hosting
- **Uvicorn**: ASGI server for the static file application

## Authentication Requirements
- **Telegram Bot Token**: Obtained from @BotFather
- **OpenAI API Key**: For Vision API access
- **Google Service Account**: JSON credentials file for Sheets API access

## Optional Integrations
- **Google OAuth2**: Alternative authentication method for Sheets access
- **PIL/Pillow**: Image processing and validation capabilities