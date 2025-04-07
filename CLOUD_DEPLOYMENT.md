# Cloud Deployment Guide

## Overview
This guide explains how to deploy the Network Monitor application to a cloud environment. The application consists of two main components:
1. Network Agent - Collects network metrics from devices
2. Frontend Dashboard - Displays network metrics and device status

## Prerequisites
- A cloud hosting service (e.g., AWS, Azure, GCP)
- API key from your cloud service
- Domain name (optional but recommended)

## Configuration

### 1. Environment Variables
Copy `config.env.example` to `.env` and configure the following variables:

```env
# Required cloud configuration
CLOUD_ENDPOINT=https://your-api-domain.com/api
API_KEY=your_api_key_here
VITE_API_URL=https://your-api-domain.com
```

### 2. Network Agent Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables from your `.env` file
3. Run the agent:
   ```bash
   python network_agent.py
   ```

### 3. Frontend Deployment
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Build for production:
   ```bash
   npm run build
   ```
3. Deploy the `dist` folder to your cloud hosting service

## Security Considerations
- Keep your API key secure and never commit it to version control
- Use HTTPS for all API endpoints
- Implement proper authentication for the dashboard
- Regularly rotate API keys

## Troubleshooting
- Check the `network_agent.log` file for agent errors
- Ensure firewall rules allow outbound connections to the cloud endpoint
- Verify the API key has proper permissions

## Support
For issues or questions about cloud deployment, please open an issue in the repository.