# Accessing DigitalOcean Build Logs

This guide explains how to access build logs directly from DigitalOcean's API when `doctl` commands don't work as expected.

## Prerequisites

1. Your DigitalOcean API Token
2. Your App ID
3. Your Deployment ID

## Direct API Access Method

### PowerShell Command

```powershell
# Set up headers with your API token
$headers = @{ 
    "Authorization" = "Bearer YOUR_DO_API_TOKEN" 
}

# Make the API request
$url = "https://api.digitalocean.com/v2/apps/{APP_ID}/deployments/{DEPLOYMENT_ID}/components/{COMPONENT_NAME}/logs?type=BUILD"
Invoke-WebRequest -Uri $url -Headers $headers | Select-Object -ExpandProperty Content
```

### Example with Real Values

```powershell
$headers = @{ 
    "Authorization" = "Bearer dop_v1_YOUR_TOKEN" 
}

Invoke-WebRequest -Uri "https://api.digitalocean.com/v2/apps/5137f955-d71d-41a0-9774-fb35149ea21b/deployments/1da3eeab-f7ae-497a-a55f-b17f510fe799/components/autosportsgpt/logs?type=BUILD" -Headers $headers | Select-Object -ExpandProperty Content
```

## Understanding the URL Structure

The URL is composed of several parts:
- Base URL: `https://api.digitalocean.com/v2/apps`
- App ID: Your unique app identifier
- Deployment ID: The specific deployment you want to check
- Component Name: Usually matches your service name in app.yaml
- Type: `BUILD` for build logs

## Common Issues and Solutions

1. If you get a 404 error:
   - Verify your App ID and Deployment ID are correct
   - Make sure the component name matches your service name in app.yaml

2. If you get an authentication error:
   - Check that your API token is valid and has the correct permissions
   - Ensure the token is properly formatted in the Authorization header

3. If the logs URL expires:
   - The logs URLs are temporary and expire after a short time
   - Simply make the API request again to get a fresh URL

## Best Practices

1. Always use environment variables or secure storage for your API token
2. Don't hardcode sensitive information in your scripts
3. Keep track of deployment IDs for debugging purposes

## Related Documentation

- [DigitalOcean API Documentation](https://docs.digitalocean.com/reference/api/)
- [Apps Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
