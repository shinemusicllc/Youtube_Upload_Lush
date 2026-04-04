param(
    [Parameter(Mandatory = $true)]
    [string]$VpsIp,
    [string]$SshUser = "root",
    [string]$Password,
    [string]$SshKeyPath,
    [string]$ManagerName = "system",
    [string]$ControlPlaneUrl,
    [string]$Branch,
    [string]$RepoUrl
)

$scriptArgs = @(
    "scripts/add_worker.py",
    "--vps-ip", $VpsIp,
    "--ssh-user", $SshUser,
    "--manager-name", $ManagerName
)

if ($Password) {
    $scriptArgs += @("--password", $Password)
}

if ($SshKeyPath) {
    $resolvedKeyPath = (Resolve-Path $SshKeyPath).Path
    $scriptArgs += @("--ssh-key-file", $resolvedKeyPath)
}

if ($ControlPlaneUrl) {
    $scriptArgs += @("--control-plane-url", $ControlPlaneUrl)
}

if ($Branch) {
    $scriptArgs += @("--branch", $Branch)
}

if ($RepoUrl) {
    $scriptArgs += @("--repo-url", $RepoUrl)
}

python @scriptArgs
exit $LASTEXITCODE
