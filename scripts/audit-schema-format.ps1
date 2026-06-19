param()
$dir = 'c:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\pipelines\schemas'

Write-Host "FILE FORMAT AUDIT" -ForegroundColor Cyan
Write-Host ("-" * 70)

Get-ChildItem $dir -Filter "*.json" | ForEach-Object {
    $raw = Get-Content $_.FullName -Raw
    $safe = $raw -replace '"[$]schema"', '"xschema"'
    $obj = try { $safe | ConvertFrom-Json } catch { $null }

    $format = if ($obj.name -and $obj.objectId -and $obj.properties.activities) {
        "FABRIC-NATIVE  [OK]"
    } elseif ($null -ne $obj.resources) {
        "ARM-TEMPLATE   [DELETE]"
    } elseif ($obj.name -and $obj.type -eq "Pipeline") {
        "MANIFEST       [KEEP]"
    } else {
        "OTHER          [?]"
    }

    $color = if ($format -like "*OK*") { "Green" }
             elseif ($format -like "*DELETE*") { "Red" }
             else { "Yellow" }

    Write-Host ("  {0,-50} {1}" -f $_.Name, $format) -ForegroundColor $color
}
