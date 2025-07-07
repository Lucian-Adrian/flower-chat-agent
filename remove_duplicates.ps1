# PowerShell script to remove duplicates from JSON file

$jsonFile = "c:\Users\user\Desktop\XOFlowers Instagram AI agent chatbot\config.json"
$backupFile = "c:\Users\user\Desktop\XOFlowers Instagram AI agent chatbot\config_backup.json"

# Create backup
Copy-Item $jsonFile $backupFile

# Read and parse JSON
$json = Get-Content $jsonFile -Raw | ConvertFrom-Json

# Remove duplicates by keeping only the first occurrence of each ID
$uniqueProducts = @{}
$cleanProducts = @()

foreach ($product in $json.products) {
    $id = $product.id
    if (-not $uniqueProducts.ContainsKey($id)) {
        $uniqueProducts[$id] = $true
        $cleanProducts += $product
    }
}

# Update the JSON object
$json.products = $cleanProducts

# Convert back to JSON and save
$json | ConvertTo-Json -Depth 10 | Out-File $jsonFile -Encoding UTF8

Write-Host "Duplicates removed. Original file backed up as config_backup.json"
Write-Host "Original product count: $($json.products.Count + ($uniqueProducts.Count - $cleanProducts.Count))"
Write-Host "Clean product count: $($cleanProducts.Count)"
