# TradingBot

Experiments with trading bot and API calls to Bitunix.

## Docker setup in WSL

Run the following commands in order.

```bash
sudo apt update && sudo apt upgrade
sudo apt install --no-install-recommends apt-transport-https ca-certificates curl gnupg2
```

```bash
. /etc/os-release
curl -fsSL https://download.docker.com/linux/${ID}/gpg | sudo tee /etc/apt/trusted.gpg.d/docker.asc
echo "deb [arch=amd64] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
```

```bash
sudo apt install docker-ce docker-ce-cli containerd.io
```

### Confirm installation and permissions

```bash
sudo usermod -aG docker $USER
groups
```