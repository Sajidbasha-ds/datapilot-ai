param(
    [int]$Port = 8080
)

$ip = [System.Net.IPAddress]::Any
$listener = New-Object System.Net.Sockets.TcpListener($ip, $Port)

$mimeTypes = @{
    '.html' = 'text/html; charset=utf-8';
    '.htm'  = 'text/html; charset=utf-8';
    '.css'  = 'text/css; charset=utf-8';
    '.js'   = 'application/javascript; charset=utf-8';
    '.json' = 'application/json; charset=utf-8';
    '.png'  = 'image/png';
    '.jpg'  = 'image/jpeg';
    '.jpeg' = 'image/jpeg';
    '.gif'  = 'image/gif';
    '.svg'  = 'image/svg+xml';
    '.ico'  = 'image/x-icon';
    '.csv'  = 'text/csv';
    '.txt'  = 'text/plain; charset=utf-8';
    '.woff' = 'font/woff';
    '.woff2'= 'font/woff2';
    '.ttf'  = 'font/ttf'
}

try {
    $listener.Start()
} catch {
    Write-Error "Failed to start listener on port $Port"
    exit 1
}

Write-Host "=========================================================="
Write-Host "Server is running on port $Port"
Write-Host "Local URL:   http://localhost:$Port"
Write-Host "Network URL: http://192.168.29.242:$Port"
Write-Host "=========================================================="

$root = (Get-Location).Path
$crlf = [System.Text.Encoding]::ASCII.GetString(@(13, 10))

while ($true) {
    try {
        $client = $listener.AcceptTcpClient()
        $stream = $client.GetStream()
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
        
        $requestLine = $reader.ReadLine()
        if (-not $requestLine) {
            $client.Close()
            continue
        }
        
        while ($line = $reader.ReadLine()) {
            if ($line.Trim().Length -eq 0) {
                break
            }
        }
        
        $tokens = $requestLine -split ' '
        $rawUrl = if ($tokens.Length -gt 1) { $tokens[1] } else { '/' }
        
        $urlPath = $rawUrl.Split('?')[0].TrimStart('/')
        if ([string]::IsNullOrWhiteSpace($urlPath)) {
            $urlPath = 'index.html'
        }
        
        $decodedPath = [System.Uri]::UnescapeDataString($urlPath)
        $relPath = $decodedPath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
        $filePath = [System.IO.Path]::Combine($root, $relPath)
        
        if (Test-Path -Path $filePath -PathType Container) {
            $filePath = [System.IO.Path]::Combine($filePath, 'index.html')
        }
        
        $writer = New-Object System.IO.BinaryWriter($stream)
        
        if (Test-Path -Path $filePath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $mime = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { 'application/octet-stream' }
            
            $fileBytes = [System.IO.File]::ReadAllBytes($filePath)
            $headerStr = 'HTTP/1.1 200 OK' + $crlf +
                         'Content-Type: ' + $mime + $crlf +
                         'Content-Length: ' + $fileBytes.Length + $crlf +
                         'Access-Control-Allow-Origin: *' + $crlf +
                         'Connection: close' + $crlf + $crlf
            
            $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($headerStr)
            $writer.Write($headerBytes)
            $writer.Write($fileBytes)
        } else {
            $body = '<!DOCTYPE html><html><body><h2>404 Not Found</h2></body></html>'
            $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
            $headerStr = 'HTTP/1.1 404 Not Found' + $crlf +
                         'Content-Type: text/html; charset=utf-8' + $crlf +
                         'Content-Length: ' + $bodyBytes.Length + $crlf +
                         'Connection: close' + $crlf + $crlf
            
            $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($headerStr)
            $writer.Write($headerBytes)
            $writer.Write($bodyBytes)
        }
        
        $writer.Flush()
        $client.Close()
    } catch {
    }
}
