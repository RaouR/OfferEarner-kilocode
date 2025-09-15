$body = @{
    username = "testuser"
    email = "test@example.com" 
    password = "password123"
    paypal_email = "paypal@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register" -Method Post -Body $body -ContentType "application/json"