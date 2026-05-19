$ErrorActionPreference = "Stop"

$projectRoot = "D:\Projects\Optimizing-Retail-Stock-Levels-Through-AI-Powered-Demand-Prediction"
$templatePath = "C:\Users\Mohit Yadav\Downloads\CU MBA BBA PPT.pptx"
$outPath = Join-Path $projectRoot "Reports\Project_Overview_Presentation.pptx"
$figures = Join-Path $projectRoot "Reports\figures"
$tables = Join-Path $projectRoot "Reports\tables"

$msoTrue = -1
$msoFalse = 0
$ppSaveAsOpenXMLPresentation = 24

function Set-TextBox {
    param(
        [object]$Shape,
        [string]$Text,
        [int]$Size = 22,
        [bool]$Bullets = $true
    )
    $Shape.TextFrame.TextRange.Text = $Text
    $Shape.TextFrame.WordWrap = $msoTrue
    $Shape.TextFrame.AutoSize = 0
    $tr = $Shape.TextFrame.TextRange
    $tr.Font.Name = "Arial"
    $tr.Font.Size = $Size
    $tr.Font.Color.RGB = 0
    if ($Bullets) {
        $tr.ParagraphFormat.Bullet.Visible = $msoTrue
    } else {
        $tr.ParagraphFormat.Bullet.Visible = $msoFalse
    }
}

function Set-Title {
    param([object]$Slide, [string]$Title)
    Set-TextBox -Shape $Slide.Shapes.Item(1) -Text $Title -Size 28 -Bullets $false
    $Slide.Shapes.Item(1).TextFrame.TextRange.Font.Bold = $msoTrue
}

function Set-Body {
    param(
        [object]$Slide,
        [string[]]$Bullets,
        [int]$Size = 21,
        [double]$Left = 68.2,
        [double]$Top = 196,
        [double]$Width = 499.5,
        [double]$Height = 278
    )
    $body = $Slide.Shapes.Item(2)
    $body.Left = $Left
    $body.Top = $Top
    $body.Width = $Width
    $body.Height = $Height
    Set-TextBox -Shape $body -Text ($Bullets -join "`r") -Size $Size -Bullets $true
}

function Add-PictureFit {
    param(
        [object]$Slide,
        [string]$Path,
        [double]$Left,
        [double]$Top,
        [double]$Width,
        [double]$Height
    )
    if (!(Test-Path $Path)) { return }
    $pic = $Slide.Shapes.AddPicture($Path, $msoFalse, $msoTrue, $Left, $Top, -1, -1)
    $scaleW = $Width / $pic.Width
    $scaleH = $Height / $pic.Height
    $scale = [Math]::Min($scaleW, $scaleH)
    $pic.Width = $pic.Width * $scale
    $pic.Height = $pic.Height * $scale
    $pic.Left = $Left + (($Width - $pic.Width) / 2)
    $pic.Top = $Top + (($Height - $pic.Height) / 2)
}

function Add-MetricTable {
    param([object]$Slide)
    $rows = @(
        @("Model", "RMSE", "MAPE"),
        @("Linear Regression Lags", "290.328", "17.860"),
        @("Prophet", "311.009", "14.123"),
        @("Seasonal Naive", "405.221", "13.945")
    )
    $shape = $Slide.Shapes.AddTable(4, 3, 55, 205, 300, 118)
    $table = $shape.Table
    for ($r = 1; $r -le 4; $r++) {
        for ($c = 1; $c -le 3; $c++) {
            $cell = $table.Cell($r, $c)
            $cell.Shape.TextFrame.TextRange.Text = $rows[$r-1][$c-1]
            $cell.Shape.TextFrame.TextRange.Font.Name = "Arial"
            $cell.Shape.TextFrame.TextRange.Font.Size = 10
            if ($r -eq 1) {
                $cell.Shape.TextFrame.TextRange.Font.Bold = $msoTrue
                $cell.Shape.Fill.ForeColor.RGB = 12611584
            }
        }
    }
}

function Add-InventoryTable {
    param([object]$Slide)
    $rows = @(
        @("Family", "Reorder Point", "Order Qty"),
        @("BEVERAGES", "16,218.88", "30,623.65"),
        @("DAIRY", "7,017.94", "12,743.27"),
        @("GROCERY I", "21,676.35", "40,913.41")
    )
    $shape = $Slide.Shapes.AddTable(4, 3, 55, 210, 330, 125)
    $table = $shape.Table
    for ($r = 1; $r -le 4; $r++) {
        for ($c = 1; $c -le 3; $c++) {
            $cell = $table.Cell($r, $c)
            $cell.Shape.TextFrame.TextRange.Text = $rows[$r-1][$c-1]
            $cell.Shape.TextFrame.TextRange.Font.Name = "Arial"
            $cell.Shape.TextFrame.TextRange.Font.Size = 10
            if ($r -eq 1) {
                $cell.Shape.TextFrame.TextRange.Font.Bold = $msoTrue
                $cell.Shape.Fill.ForeColor.RGB = 12611584
            }
        }
    }
}

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = $msoTrue
$pres = $ppt.Presentations.Open($templatePath, $msoFalse, $msoFalse, $msoFalse)

try {
    Set-Title $pres.Slides.Item(5) "Abstract / Executive Summary"
    Set-Body $pres.Slides.Item(5) @(
        "Project forecasts short-term retail demand for store 1",
        "Scope: BEVERAGES, DAIRY and GROCERY I product families",
        "Models compared: seasonal naive, moving average, regression lags, ARIMA and Prophet",
        "Best operational model: lag-based linear regression by RMSE",
        "Forecast output is converted into safety stock, reorder point, order quantity and alerts"
    ) 19

    Set-Title $pres.Slides.Item(6) "Presentation Outline"
    Set-Body $pres.Slides.Item(6) @(
        "Introduction and project need",
        "Literature and research gap",
        "Methodology and data preparation",
        "Data analysis and model results",
        "Inventory recommendations, conclusions and future scope"
    ) 21

    Set-Title $pres.Slides.Item(7) "Chapter 1: Introduction"
    Set-Body $pres.Slides.Item(7) @(
        "Retailers face stockouts and overstock when demand is uncertain",
        "This project links demand forecasting with inventory planning",
        "Dataset: Corporacion Favorita grocery sales data",
        "Focused scope keeps the implementation explainable for MSc submission",
        "Output supports reorder decisions and category-wise stock planning"
    ) 20

    Set-Title $pres.Slides.Item(8) "Chapter 2: Literature Review"
    Set-Body $pres.Slides.Item(8) @(
        "Classical forecasting methods give explainable baselines",
        "Feature-based ML can use lag values, rolling means and calendar signals",
        "Prophet and ARIMA are useful comparison models for time-series forecasting",
        "Research gap: many forecasting projects stop at accuracy metrics",
        "This project continues from prediction to inventory action"
    ) 20

    Set-Title $pres.Slides.Item(9) "Chapter 3: Research Methodology"
    Set-Body $pres.Slides.Item(9) @(
        "Raw files merged: sales, items, stores, transactions, oil and holidays",
        "Analysis filtered to store 1 and three selected families",
        "Features created: lag sales, rolling averages and calendar variables",
        "Chronological train-test split used for realistic forecasting",
        "Metrics: MAE, RMSE and MAPE"
    ) 20

    Set-Title $pres.Slides.Item(10) "Chapter 4: Data Analysis & Interpretation"
    Set-Body $pres.Slides.Item(10) @(
        "Family-wise demand varies clearly",
        "GROCERY I has the highest volume",
        "Beverages and Dairy require separate stock rules"
    ) 14 45 185 215 115
    Add-PictureFit $pres.Slides.Item(10) (Join-Path $figures "sales_history_cropped.png") 45 295 610 190

    Set-Title $pres.Slides.Item(11) "Chapter 5: Findings / Results"
    Set-Body $pres.Slides.Item(11) @(
        "Best model by RMSE: linear_regression_lags",
        "Best RMSE: 290.328",
        "Prophet achieved lowest MAPE but higher RMSE",
        "RMSE was selected for stock-planning model choice"
    ) 16 395 205 255 160
    Add-MetricTable $pres.Slides.Item(11)

    Set-Title $pres.Slides.Item(12) "Chapter 6: Conclusions"
    Set-Body $pres.Slides.Item(12) @(
        "The project successfully connects forecasting with inventory decisions",
        "Lag-based regression gave the most suitable operational forecast in the current run",
        "Inventory outputs make the forecast useful for reorder planning",
        "The workflow is reproducible through scripts, tables, figures and dashboard output"
    ) 20

    Set-Title $pres.Slides.Item(13) "Chapter 7: Recommendations"
    Set-Body $pres.Slides.Item(13) @(
        "Use family-wise reorder points instead of one general rule",
        "Monitor reorder alerts generated during the planning horizon",
        "Review high-volume GROCERY I more frequently",
        "Use dashboard and CSV outputs for manager review"
    ) 15 55 350 315 115
    Add-InventoryTable $pres.Slides.Item(13)

    Set-Title $pres.Slides.Item(14) "Chapter 8: Limitations"
    Set-Body $pres.Slides.Item(14) @(
        "Scope limited to store 1 and three product families",
        "Inventory policy uses simplified assumptions for lead time and service level",
        "LSTM was not executed because TensorFlow/Keras was unavailable",
        "No live database, supplier constraint or warehouse-capacity logic included"
    ) 20

    Set-Title $pres.Slides.Item(15) "Chapter 9: References"
    Set-Body $pres.Slides.Item(15) @(
        "Corporacion Favorita grocery sales dataset",
        "Forecasting: Principles and Practice",
        "M5 forecasting competition literature",
        "Prophet, pandas, NumPy, Matplotlib and statsmodels documentation",
        "Inventory planning references for safety stock and reorder point"
    ) 18

    Set-Title $pres.Slides.Item(16) "Chapter 10: Appendices"
    Set-Body $pres.Slides.Item(16) @(
        "Source code structure and module descriptions",
        "Generated output files: model metrics, forecasts and inventory tables",
        "Charts: sales history, forecast vs actual, inventory simulation",
        "Dashboard HTML summary",
        "Notebook and scripts for project verification"
    ) 19

    $pres.SaveAs($outPath, $ppSaveAsOpenXMLPresentation)
}
finally {
    $pres.Close()
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}

Write-Output $outPath
