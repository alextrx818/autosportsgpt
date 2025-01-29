# Deploy script for AutoSportsGPT

# Add all changes
git add .

# Commit with message from command line or default
$commit_message = if ($args[0]) { $args[0] } else { "Update application" }
git commit -m $commit_message

# Push to main branch
git push origin main

Write-Host "Changes pushed to GitHub. Digital Ocean will automatically redeploy the application."
Write-Host "You can check the deployment status at: https://cloud.digitalocean.com/apps"
