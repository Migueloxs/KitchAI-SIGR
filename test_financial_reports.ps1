#!/usr/bin/env powershell
# Test Financial Reports APIs - Issue #13
# Usage: .\test_financial_reports.ps1 -Token "your-jwt-token"

param(
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "http://localhost:8001",
    
    [Parameter(Mandatory=$true)]
    [string]$Token = "",
    
    [Parameter(Mandatory=$false)]
    [string]$StartDate = "2024-01-01",
    
    [Parameter(Mandatory=$false)]
    [string]$EndDate = "2024-12-31"
)

# Colors for output
$Green = @{ ForegroundColor = "Green" }
$Red = @{ ForegroundColor = "Red" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Cyan = @{ ForegroundColor = "Cyan" }

function Print-Header {
    param([string]$Text)
    Write-Host "`n" @Cyan
    Write-Host "=" * 60 @Cyan
    Write-Host $Text @Cyan
    Write-Host "=" * 60 @Cyan
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Headers = @{}
    )
    
    Write-Host "`nTesting: $Name" @Yellow
    Write-Host "Endpoint: $Endpoint"
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method $Method -Headers $Headers -ErrorAction Stop
        
        Write-Host "✓ Status: 200 OK" @Green
        Write-Host "Response (first 500 chars):"
        $json = $response | ConvertTo-Json
        Write-Host $json.Substring(0, [Math]::Min(500, $json.Length))
        
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "✗ Status: $statusCode" @Red
        
        try {
            $errorResponse = $_.Exception.Response.Content | ConvertFrom-Json
            Write-Host "Error: $($errorResponse.detail)" @Red
        }
        catch {
            Write-Host "Error: $($_.Exception.Message)" @Red
        }
        
        return $false
    }
}

# Main test execution
Print-Header "Financial Reports API Tests - Issue #13"

# Validate token
if ([string]::IsNullOrEmpty($Token)) {
    Write-Host "ERROR: JWT token is required!" @Red
    Write-Host "Usage: .\test_financial_reports.ps1 -Token 'your-jwt-token'" @Yellow
    exit 1
}

Write-Host "Base URL: $BaseUrl" @Cyan
Write-Host "Period: $StartDate to $EndDate" @Cyan
Write-Host "Token: ****$(($Token).Substring([Math]::Max(0, $Token.Length - 4)))" @Cyan

# Setup headers
$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type" = "application/json"
}

# Test Results
$results = @()

# ========== CA1: Sales by Period ==========
Print-Header "CA1: Sales by Period"
$endpoint = "/api/finances/reports/sales-by-period/?start_date=$StartDate&end_date=$EndDate"
$results += Test-Endpoint -Name "CA1 - Sales by Period" `
    -Endpoint $endpoint `
    -Headers $headers

# ========== CA2: Sales by Payment Method ==========
Print-Header "CA2: Sales by Payment Method"
$endpoint = "/api/finances/reports/sales-by-payment-method/?start_date=$StartDate&end_date=$EndDate&payment_method=Tarjeta"
$results += Test-Endpoint -Name "CA2 - Sales by Payment Method (Tarjeta)" `
    -Endpoint $endpoint `
    -Headers $headers

# Test with Efectivo
$endpoint = "/api/finances/reports/sales-by-payment-method/?start_date=$StartDate&end_date=$EndDate&payment_method=Efectivo"
$results += Test-Endpoint -Name "CA2 - Sales by Payment Method (Efectivo)" `
    -Endpoint $endpoint `
    -Headers $headers

# ========== CA2: Sales by Employee ==========
Print-Header "CA2: Sales by Employee"
# Note: Replace with actual employee UUID from your database
$employeeId = "uuid-employee-1"
$endpoint = "/api/finances/reports/sales-by-employee/?start_date=$StartDate&end_date=$EndDate&employee_id=$employeeId"
$results += Test-Endpoint -Name "CA2 - Sales by Employee" `
    -Endpoint $endpoint `
    -Headers $headers

# ========== CA3: Detailed Financial Report ==========
Print-Header "CA3: Detailed Financial Report"
$endpoint = "/api/finances/reports/detailed/?start_date=$StartDate&end_date=$EndDate"
$results += Test-Endpoint -Name "CA3 - Detailed Financial Report" `
    -Endpoint $endpoint `
    -Headers $headers

# ========== CA3: Financial Comparison ==========
Print-Header "CA3: Financial Comparison Report"
$currentStart = "2024-02-01"
$currentEnd = "2024-02-29"
$previousStart = "2024-01-01"
$previousEnd = "2024-01-31"

$endpoint = "/api/finances/reports/comparison/?current_start=$currentStart&current_end=$currentEnd&previous_start=$previousStart&previous_end=$previousEnd"
$results += Test-Endpoint -Name "CA3 - Financial Comparison Report" `
    -Endpoint $endpoint `
    -Headers $headers

# ========== Summary ==========
Print-Header "Test Summary"

$passed = ($results | Where-Object { $_ -eq $true } | Measure-Object).Count
$total = $results.Count

Write-Host "Passed: $passed/$total" @Green
Write-Host "Failed: $($total - $passed)/$total" @Red

if ($passed -eq $total) {
    Write-Host "`n✓ All tests passed!" @Green
    exit 0
}
else {
    Write-Host "`n✗ Some tests failed. Review the output above." @Red
    exit 1
}
