# Pre-commit hook for PowerShell: Validate code quality before committing
# Install: Copy this script to .git/hooks/pre-commit and ensure it's executable

param()

# Get staged files
$stagedFiles = & git diff --cached --name-only
$pyFiles = $stagedFiles | Where-Object { $_ -match '\.py$' -and $_ -notmatch '__pycache__' -and $_ -notmatch '^tests/' -and $_ -notmatch '^\.github[\\|/]scripts/' }

if (-not $pyFiles) {
    exit 0
}

Write-Host "Pre-commit validation..."
$pyFileCount = if ($pyFiles -is [array]) { $pyFiles.Count } else { 1 }
Write-Host "Python files to commit: $pyFileCount"

# Check for missing test files
$missingTests = @()

foreach ($pyFile in $pyFiles) {
    $filename = Split-Path -Leaf $pyFile
    
    # Skip infrastructure scripts and test files
    if ($filename -match '^test_' -or $filename -match '_test\.py$' -or $filename -match '^validate_' -or $filename -match '^run_') {
        continue
    }
    
    # Skip package __init__.py files (they don't need direct tests)
    if ($filename -eq "__init__.py") {
        continue
    }
    
    # Extract module name without .py extension
    $moduleName = [System.IO.Path]::GetFileNameWithoutExtension($filename)
    
    # Build potential test name patterns
    $pathNormalized = $pyFile -replace '[\\|/]', '_' -replace '\.py$', ''
    $pathParts = @($pyFile -split '[\\|/]')
    $pathReverse = $pathParts[-1..0] -join '_' -replace '\.py$', ''
    
    # Strategy 1: Check common test file locations (exact filename match)
    $testPaths = @(
        "tests/test_$filename",
        "__tests__/$moduleName.test.py",
        "$(Split-Path -Parent $pyFile)/test_$filename",
        "$(Split-Path -Parent $pyFile)/$moduleName`_test.py"
    )
    
    # Normalize paths for Windows
    $testPathsNormalized = $testPaths | ForEach-Object { $_ -replace '/', '\' }
    $found = $false
    
    foreach ($testPath in $testPathsNormalized) {
        if (Test-Path $testPath) {
            $found = $true
            break
        }
    }
    
    if ($found) {
        continue
    }
    
    # Strategy 1b: Check for tests with path-based naming patterns
    $pathBasedTests = @(
        "tests/test_$pathNormalized.py",
        "tests/test_$pathReverse.py"
    ) | ForEach-Object { $_ -replace '/', '\' }
    
    foreach ($testPath in $pathBasedTests) {
        if (Test-Path $testPath) {
            $found = $true
            break
        }
    }
    
    if ($found) {
        continue
    }
    
    # Strategy 2a: Search for the module name in ANY test file
    # This catches cases like app/routes/health.py covered by test_health_routes.py
    if (Test-Path "tests") {
        $testFiles = @(Get-ChildItem -Path "tests" -Name "*.py" -Recurse -ErrorAction SilentlyContinue)
        
        foreach ($testFile in $testFiles) {
            $content = Get-Content "tests/$testFile" -Raw -ErrorAction SilentlyContinue
            
            # Check if test file imports the module by any part of the filename
            # e.g., for "health.py", check if test imports "health"
            # e.g., for "reports.py", check if test imports "reports"
            if ($content -match "\b$moduleName\b" -or `
                $content -match "from\s+.*\b$moduleName\b" -or `
                $content -match "import\s+.*\b$moduleName\b") {
                $found = $true
                break
            }
        }
    }
    
    if ($found) {
        continue
    }
    
    # Strategy 3: Check for tests in sibling tests/ directory
    $moduleDir = Split-Path -Parent $pyFile
    if (Test-Path "$moduleDir/tests") {
        $siblingTests = @(Get-ChildItem -Path "$moduleDir/tests" -Name "test_*.py", "*_test.py" -ErrorAction SilentlyContinue)
        if ($siblingTests.Count -gt 0) {
            continue
        }
    }
    
    # Strategy 4: For package __init__.py files, check if any test imports the package
    if ($filename -eq "__init__.py") {
        $packagePath = (Split-Path -Parent $pyFile) -replace '\\', '.' -replace '^\\.', ''
        
        if (Test-Path "tests") {
            $testFiles = @(Get-ChildItem -Path "tests" -Name "*.py" -Recurse -ErrorAction SilentlyContinue)
            
            foreach ($testFile in $testFiles) {
                $content = Get-Content "tests/$testFile" -Raw -ErrorAction SilentlyContinue
                if ($content -match "from\s+$packagePath" -or $content -match "import\s+$packagePath") {
                    $found = $true
                    break
                }
            }
        }
        
        if ($found) {
            continue
        }
    }
    
    $missingTests += $pyFile
}

if ($missingTests.Count -gt 0) {
    Write-Host ""
    Write-Host "WARNING: No test files found for:"
    foreach ($file in $missingTests) {
        Write-Host "  - $file"
    }
    Write-Host ""
    Write-Host "It's recommended to create tests before committing."
    Write-Host "Continue? (y/n)" -NoNewline
    Write-Host " " -NoNewline
    
    $response = Read-Host
    if ($response -notmatch '^[Yy]$') {
        Write-Host "Commit aborted."
        exit 1
    }
}

exit 0
