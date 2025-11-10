# TradingBot
Experiments with trading bot and api calls to bitunix


#Docker setup in wsl
sudo apt update && sudo apt upgrade
sudo apt install --no-install-recommends apt-transport-https ca-certificates curl gnupg2

. /etc/os-release
curl -fsSL https://download.docker.com/linux/${ID}/gpg | sudo tee /etc/apt/trusted.gpg.d/docker.asc
echo "deb [arch=amd64] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io

#Confirm with this
sudo usermod -aG docker $USER
groups