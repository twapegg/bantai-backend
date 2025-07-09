# PowerShell Test Script for AI Content Moderation API
# Usage: .\test_api.ps1

$baseUrl = "http://127.0.0.1:8000"

Write-Host "🧪 AI Content Moderation API Test Script" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health Check: " -ForegroundColor Green -NoNewline
    Write-Host "$($healthResponse.status)" -ForegroundColor White
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Text Moderation - Safe Content
Write-Host "`n2. Testing Text Moderation (Safe Content)..." -ForegroundColor Yellow
try {
    $textRequest = @{
        text = "Hello world, this is a normal message"
    } | ConvertTo-Json
    
    $textResponse = Invoke-RestMethod -Uri "$baseUrl/moderate/text" -Method POST -Body $textRequest -ContentType "application/json"
    Write-Host "✅ Text Moderation (Safe): " -ForegroundColor Green -NoNewline
    Write-Host "$($textResponse.label) (confidence: $($textResponse.confidence.ToString('F2')))" -ForegroundColor White
    Write-Host "   Reason: $($textResponse.reason)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Text Moderation (Safe) Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Text Moderation - Potentially Harmful Content
Write-Host "`n3. Testing Text Moderation (Potentially Harmful Content)..." -ForegroundColor Yellow
try {
    $textRequest = @{
        text = "This message contains hate and violence"
    } | ConvertTo-Json
    
    $textResponse = Invoke-RestMethod -Uri "$baseUrl/moderate/text" -Method POST -Body $textRequest -ContentType "application/json"
    Write-Host "✅ Text Moderation (Harmful): " -ForegroundColor Green -NoNewline
    Write-Host "$($textResponse.label) (confidence: $($textResponse.confidence.ToString('F2')))" -ForegroundColor White
    Write-Host "   Reason: $($textResponse.reason)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Text Moderation (Harmful) Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Image Moderation Health
Write-Host "`n4. Testing Image Moderation Health..." -ForegroundColor Yellow
try {
    $imageHealthResponse = Invoke-RestMethod -Uri "$baseUrl/moderate/image/health" -Method GET
    Write-Host "✅ Image Moderation Health: " -ForegroundColor Green -NoNewline
    Write-Host "$($imageHealthResponse.status)" -ForegroundColor White
    Write-Host "   Supported formats: $($imageHealthResponse.supported_formats -join ', ')" -ForegroundColor Gray
    Write-Host "   Max file size: $($imageHealthResponse.max_file_size_mb)MB" -ForegroundColor Gray
} catch {
    Write-Host "❌ Image Moderation Health Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Audio Moderation Health
Write-Host "`n5. Testing Audio Moderation Health..." -ForegroundColor Yellow
try {
    $audioHealthResponse = Invoke-RestMethod -Uri "$baseUrl/moderate/audio/health" -Method GET
    Write-Host "✅ Audio Moderation Health: " -ForegroundColor Green -NoNewline
    Write-Host "$($audioHealthResponse.status)" -ForegroundColor White
    Write-Host "   Supported formats: $($audioHealthResponse.supported_formats -join ', ')" -ForegroundColor Gray
    Write-Host "   Max file size: $($audioHealthResponse.max_file_size_mb)MB" -ForegroundColor Gray
} catch {
    Write-Host "❌ Audio Moderation Health Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: API Information
Write-Host "`n6. Testing API Information..." -ForegroundColor Yellow
try {
    $apiInfo = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    Write-Host "✅ API Information:" -ForegroundColor Green
    Write-Host "   Name: $($apiInfo.name)" -ForegroundColor White
    Write-Host "   Version: $($apiInfo.version)" -ForegroundColor White
    Write-Host "   Documentation: $baseUrl$($apiInfo.docs_url)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API Information Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Test completed! Check the results above." -ForegroundColor Green
Write-Host "📚 Full API documentation: $baseUrl/docs" -ForegroundColor Cyan
