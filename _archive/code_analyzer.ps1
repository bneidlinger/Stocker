#
# Miami Vice Code Analyzer - Simple Edition
# A PowerShell script to analyze code projects with a Miami Vice-inspired theme
#

# Basic configuration
$CONFIG = @{
    ExcludeDirs = @('node_modules', 'bin', 'obj', '.git', '.vs', 'packages')
    CodeExtensions = @('.cs', '.js', '.ts', '.py', '.ps1', '.html', '.css', '.java', '.cpp', '.c', '.h', '.rb', '.php')
    MaxFileSizeMB = 10
}

# Color theme (Miami Vice inspired)
$COLORS = @{
    Pink = 'DarkMagenta' 
    Blue = 'Cyan'
    Text = 'White'
    Warning = 'Yellow'
    Error = 'Red'
    Success = 'Green'
}

# Show colorful header
function Show-Header {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor $COLORS.Blue
    Write-Host "  🌴  MIAMI VICE CODE ANALYZER - SIMPLE  🌴  " -ForegroundColor $COLORS.Pink
    Write-Host "===============================================" -ForegroundColor $COLORS.Blue
    Write-Host ""
}

# Simple function to check if a file is binary
function Test-Binary {
    param([string]$FilePath)
    
    # Common binary extensions
    $BinaryExtensions = @('.exe', '.dll', '.zip', '.pdf', '.jpg', '.png', '.gif')
    $Extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
    
    if ($BinaryExtensions -contains $Extension) {
        return $true
    }
    
    # Check for null bytes in first 4KB (basic heuristic for binary files)
    try {
        $FileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $CheckLength = [Math]::Min(4096, $FileBytes.Length)
        
        for ($i = 0; $i -lt $CheckLength; $i++) {
            if ($FileBytes[$i] -eq 0) {
                return $true
            }
        }
        return $false
    }
    catch {
        Write-Host "Error reading file: $FilePath" -ForegroundColor $COLORS.Error
        return $true # Assume binary on error
    }
}

# Count lines in a file
function Get-FileStats {
    param([string]$FilePath)
    
    $Stats = @{
        TotalLines = 0
        CodeLines = 0
        CommentLines = 0
        BlankLines = 0
        TODOCount = 0
        FIXMECount = 0
    }
    
    # Skip binary files
    if (Test-Binary -FilePath $FilePath) {
        return $Stats
    }
    
    # Set default comment character based on file extension
    $Extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
    $CommentChar = switch -Wildcard ($Extension) {
        '.py' { '#' }
        '.rb' { '#' }
        '.ps1' { '#' }
        '.js' { '//' }
        '.ts' { '//' }
        '.cs' { '//' }
        '.java' { '//' }
        '.cpp' { '//' }
        '.c' { '//' }
        '.h' { '//' }
        '.php' { '//' }
        default { $null }
    }
    
    $InMultilineComment = $false
    
    try {
        foreach ($Line in [System.IO.File]::ReadAllLines($FilePath)) {
            $Stats.TotalLines++
            $TrimmedLine = $Line.Trim()
            
            # Check for blank lines
            if ([string]::IsNullOrWhiteSpace($TrimmedLine)) {
                $Stats.BlankLines++
                continue
            }
            
            # Check for comments
            $IsComment = $false
            
            # Handle multiline comments (simplistic)
            if ($InMultilineComment) {
                $Stats.CommentLines++
                $IsComment = $true
                if ($TrimmedLine -match '\*/$' -or $TrimmedLine -match '"""$' -or $TrimmedLine -match "'''$") {
                    $InMultilineComment = $false
                }
                continue
            }
            elseif ($TrimmedLine -match '^/\*' -or $TrimmedLine -match '^"""' -or $TrimmedLine -match "^'''") {
                $Stats.CommentLines++
                $IsComment = $true
                # Check if the comment ends on the same line
                if (-not ($TrimmedLine -match '\*/$' -or $TrimmedLine -match '"""$' -or $TrimmedLine -match "'''$")) {
                    $InMultilineComment = $true
                }
                continue
            }
            
            # Handle single-line comments
            if ($CommentChar -and $TrimmedLine.StartsWith($CommentChar)) {
                $Stats.CommentLines++
                $IsComment = $true
            }
            elseif ($TrimmedLine -match '^\<\!\-\-' -and $TrimmedLine -match '\-\-\>$') {
                # HTML comments
                $Stats.CommentLines++
                $IsComment = $true
            }
            
            # Count code lines
            if (-not $IsComment) {
                $Stats.CodeLines++
            }
            
            # Check for TODOs and FIXMEs
            if ($Line -match 'TODO') {
                $Stats.TODOCount++
            }
            if ($Line -match 'FIXME') {
                $Stats.FIXMECount++
            }
        }
    }
    catch {
        Write-Host "Error analyzing file: $FilePath" -ForegroundColor $COLORS.Error
    }
    
    return $Stats
}

# Main analysis function
function Analyze-Project {
    param([string]$ProjectPath)
    
    if (-not (Test-Path $ProjectPath -PathType Container)) {
        Write-Host "Error: Project path does not exist or is not a directory." -ForegroundColor $COLORS.Error
        return
    }
    
    $StartTime = Get-Date
    $Results = @{
        ProjectName = [System.IO.Path]::GetFileName($ProjectPath)
        TotalFiles = 0
        AnalyzedFiles = 0
        TotalLines = 0
        CodeLines = 0
        CommentLines = 0
        BlankLines = 0
        TODOCount = 0
        FIXMECount = 0
        FilesByType = @{}
        LargestFiles = @()
    }
    
    Write-Host "Analyzing project: $($Results.ProjectName)" -ForegroundColor $COLORS.Blue
    Write-Host "Searching for code files..." -ForegroundColor $COLORS.Text
    
    # Find code files
    $AllFiles = Get-ChildItem -Path $ProjectPath -Include $CONFIG.CodeExtensions -Recurse -File -ErrorAction SilentlyContinue | 
                Where-Object {
                    # Filter out excluded directories and large files
                    $IncludeFile = $true
                    
                    # Check path against excluded directories
                    foreach ($ExcludeDir in $CONFIG.ExcludeDirs) {
                        if ($_.FullName -like "*\$ExcludeDir\*") {
                            $IncludeFile = $false
                            break
                        }
                    }
                    
                    # Check file size
                    if ($_.Length -gt ($CONFIG.MaxFileSizeMB * 1MB)) {
                        $IncludeFile = $false
                    }
                    
                    $IncludeFile
                }
    
    $Results.TotalFiles = $AllFiles.Count
    Write-Host "Found $($Results.TotalFiles) code files." -ForegroundColor $COLORS.Blue
    
    # Process each file
    $FileCounter = 0
    $TotalFilesToAnalyze = $AllFiles.Count
    
    foreach ($File in $AllFiles) {
        $FileCounter++
        
        # Show progress every 10 files
        if ($FileCounter % 10 -eq 0 -or $FileCounter -eq 1) {
            $PercentComplete = [math]::Round(($FileCounter / $TotalFilesToAnalyze) * 100)
            Write-Host "Analyzing files: $FileCounter of $TotalFilesToAnalyze ($PercentComplete%)" -ForegroundColor $COLORS.Text
        }
        
        # Skip very large files
        if ($File.Length -gt ($CONFIG.MaxFileSizeMB * 1MB)) {
            continue
        }
        
        # Analyze file
        $FileStats = Get-FileStats -FilePath $File.FullName
        
        # Update project totals
        $Results.AnalyzedFiles++
        $Results.TotalLines += $FileStats.TotalLines
        $Results.CodeLines += $FileStats.CodeLines
        $Results.CommentLines += $FileStats.CommentLines
        $Results.BlankLines += $FileStats.BlankLines
        $Results.TODOCount += $FileStats.TODOCount
        $Results.FIXMECount += $FileStats.FIXMECount
        
        # Update by file type
        $Extension = $File.Extension.ToLower()
        if (-not $Results.FilesByType.ContainsKey($Extension)) {
            $Results.FilesByType[$Extension] = @{
                Count = 0
                TotalLines = 0
                CodeLines = 0
                CommentLines = 0
                BlankLines = 0
            }
        }
        
        $Results.FilesByType[$Extension].Count++
        $Results.FilesByType[$Extension].TotalLines += $FileStats.TotalLines
        $Results.FilesByType[$Extension].CodeLines += $FileStats.CodeLines
        $Results.FilesByType[$Extension].CommentLines += $FileStats.CommentLines
        $Results.FilesByType[$Extension].BlankLines += $FileStats.BlankLines
        
        # Track large files
        if ($Results.LargestFiles.Count -lt 10 -or $File.Length -gt $Results.LargestFiles[-1].Size) {
            $FileInfo = @{
                Path = $File.FullName
                Size = $File.Length
                Lines = $FileStats.TotalLines
            }
            $Results.LargestFiles += $FileInfo
            # Keep only the 10 largest files
            $Results.LargestFiles = $Results.LargestFiles | Sort-Object -Property Size -Descending | Select-Object -First 10
        }
    }
    
    $EndTime = Get-Date
    $Duration = ($EndTime - $StartTime).TotalSeconds
    
    # Display results
    Show-Results -Results $Results -Duration $Duration
    
    # Offer to generate HTML report
    $GenerateReport = Read-Host "Would you like to generate an HTML report? (Y/N)"
    if ($GenerateReport -eq 'Y' -or $GenerateReport -eq 'y') {
        $ReportPath = "$env:USERPROFILE\Desktop\$($Results.ProjectName)_Report.html"
        Write-Host "Generating HTML report at: $ReportPath" -ForegroundColor $COLORS.Blue
        Generate-HtmlReport -Results $Results -Duration $Duration -OutputPath $ReportPath
        Write-Host "Report generated successfully!" -ForegroundColor $COLORS.Success
    }
}

# Display results in console
function Show-Results {
    param(
        [hashtable]$Results,
        [double]$Duration
    )
    
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor $COLORS.Blue
    Write-Host "  ANALYSIS RESULTS: $($Results.ProjectName)" -ForegroundColor $COLORS.Pink
    Write-Host "===============================================" -ForegroundColor $COLORS.Blue
    Write-Host ""
    Write-Host "Analysis completed in $([math]::Round($Duration, 2)) seconds." -ForegroundColor $COLORS.Success
    Write-Host ""
    
    # Overall statistics
    Write-Host "OVERALL STATISTICS:" -ForegroundColor $COLORS.Pink
    Write-Host "Files analyzed:  $($Results.AnalyzedFiles) / $($Results.TotalFiles)" -ForegroundColor $COLORS.Text
    Write-Host "Total lines:     $($Results.TotalLines)" -ForegroundColor $COLORS.Text
    Write-Host "Code lines:      $($Results.CodeLines) ($(GetPercentage $Results.CodeLines $Results.TotalLines)%)" -ForegroundColor $COLORS.Text
    Write-Host "Comment lines:   $($Results.CommentLines) ($(GetPercentage $Results.CommentLines $Results.TotalLines)%)" -ForegroundColor $COLORS.Text
    Write-Host "Blank lines:     $($Results.BlankLines) ($(GetPercentage $Results.BlankLines $Results.TotalLines)%)" -ForegroundColor $COLORS.Text
    Write-Host "TODOs found:     $($Results.TODOCount)" -ForegroundColor $COLORS.Text
    Write-Host "FIXMEs found:    $($Results.FIXMECount)" -ForegroundColor $COLORS.Text
    Write-Host ""
    
    # Language breakdown
    Write-Host "LANGUAGE BREAKDOWN:" -ForegroundColor $COLORS.Pink
    $Results.FilesByType.GetEnumerator() | Sort-Object { $_.Value.CodeLines } -Descending | ForEach-Object {
        $Ext = $_.Key
        $Data = $_.Value
        Write-Host "$Ext`t$($Data.Count) files`t$($Data.TotalLines) lines`t$(GetPercentage $Data.CommentLines $Data.TotalLines)% comments" -ForegroundColor $COLORS.Text
    }
    Write-Host ""
    
    # Largest files
    Write-Host "LARGEST FILES:" -ForegroundColor $COLORS.Pink
    $Counter = 1
    foreach ($File in $Results.LargestFiles) {
        $RelativePath = $File.Path -replace [regex]::Escape($ProjectPath), ""
        $SizeKB = [math]::Round($File.Size / 1KB, 2)
        Write-Host "$Counter. $RelativePath ($SizeKB KB, $($File.Lines) lines)" -ForegroundColor $COLORS.Text
        $Counter++
    }
    Write-Host ""
}

# Calculate percentage
function GetPercentage {
    param($Part, $Total)
    if ($Total -eq 0) { return 0 }
    return [math]::Round(($Part / $Total) * 100, 1)
}

# Generate HTML report
function Generate-HtmlReport {
    param(
        [hashtable]$Results,
        [double]$Duration,
        [string]$OutputPath
    )
    
    $HtmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Code Analysis: $($Results.ProjectName)</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            line-height: 1.6;
            color: #e0e0e0;
            background-color: #1a1a2e;
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: #20294a;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 200, 255, 0.3);
            border: 1px solid #00b8ff;
        }
        
        h1, h2, h3 {
            color: #ff69b4;
            border-bottom: 2px solid #00b8ff;
            padding-bottom: 10px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background-color: #2a3a5a;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #ff69b4;
        }
        
        .card h3 {
            margin-top: 0;
            border-bottom: none;
        }
        
        .value {
            font-size: 2em;
            margin: 10px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            padding: 10px 15px;
            text-align: left;
            border-bottom: 1px solid #2a3a5a;
        }
        
        th {
            background-color: #2a3a5a;
            color: #00b8ff;
        }
        
        tr:hover {
            background-color: rgba(255, 105, 180, 0.1);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌴 Code Analysis: $($Results.ProjectName) 🌴</h1>
        <p>Analysis completed in $([math]::Round($Duration, 2)) seconds.</p>
        
        <h2>Project Summary</h2>
        <div class="summary-grid">
            <div class="card">
                <h3>Files Analyzed</h3>
                <div class="value">$($Results.AnalyzedFiles)</div>
                <div>of $($Results.TotalFiles) files</div>
            </div>
            <div class="card">
                <h3>Total Lines</h3>
                <div class="value">$($Results.TotalLines)</div>
            </div>
            <div class="card">
                <h3>Code Lines</h3>
                <div class="value">$($Results.CodeLines)</div>
                <div>$(GetPercentage $Results.CodeLines $Results.TotalLines)% of total</div>
            </div>
            <div class="card">
                <h3>Comment Lines</h3>
                <div class="value">$($Results.CommentLines)</div>
                <div>$(GetPercentage $Results.CommentLines $Results.TotalLines)% of total</div>
            </div>
            <div class="card">
                <h3>Blank Lines</h3>
                <div class="value">$($Results.BlankLines)</div>
                <div>$(GetPercentage $Results.BlankLines $Results.TotalLines)% of total</div>
            </div>
            <div class="card">
                <h3>TODOs & FIXMEs</h3>
                <div class="value">$($Results.TODOCount + $Results.FIXMECount)</div>
                <div>$($Results.TODOCount) TODOs, $($Results.FIXMECount) FIXMEs</div>
            </div>
        </div>
        
        <h2>Language Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Extension</th>
                    <th>Files</th>
                    <th>Total Lines</th>
                    <th>Code Lines</th>
                    <th>Comment %</th>
                </tr>
            </thead>
            <tbody>
"@

    # Add language breakdown rows
    $Results.FilesByType.GetEnumerator() | Sort-Object { $_.Value.CodeLines } -Descending | ForEach-Object {
        $Ext = $_.Key
        $Data = $_.Value
        $CommentPercentage = GetPercentage $Data.CommentLines $Data.TotalLines
        
        $HtmlContent += @"
                <tr>
                    <td>$Ext</td>
                    <td>$($Data.Count)</td>
                    <td>$($Data.TotalLines)</td>
                    <td>$($Data.CodeLines)</td>
                    <td>$CommentPercentage%</td>
                </tr>
"@
    }

    $HtmlContent += @"
            </tbody>
        </table>
        
        <h2>Largest Files</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>File</th>
                    <th>Size (KB)</th>
                    <th>Lines</th>
                </tr>
            </thead>
            <tbody>
"@

    # Add largest files rows
    $Counter = 1
    foreach ($File in $Results.LargestFiles) {
        $RelativePath = $File.Path -replace [regex]::Escape($ProjectPath), ""
        $SizeKB = [math]::Round($File.Size / 1KB, 2)
        
        $HtmlContent += @"
                <tr>
                    <td>$Counter</td>
                    <td>$RelativePath</td>
                    <td>$SizeKB</td>
                    <td>$($File.Lines)</td>
                </tr>
"@
        $Counter++
    }

    $HtmlContent += @"
            </tbody>
        </table>
        
        <div class="footer">
            Generated by Miami Vice Code Analyzer - Simple Edition
        </div>
    </div>
</body>
</html>
"@

    # Write the HTML content to file
    $HtmlContent | Out-File -FilePath $OutputPath -Encoding UTF8
}

# Main execution
Show-Header

# Get project path from user
$ProjectPath = Read-Host "Enter the path to the code project to analyze"

# Validate path
if (-not (Test-Path $ProjectPath -PathType Container)) {
    Write-Host "Error: The specified path does not exist or is not a directory." -ForegroundColor $COLORS.Error
    exit
}

# Run the analysis
Analyze-Project -ProjectPath $ProjectPath
