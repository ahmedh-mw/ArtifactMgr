########################################
#    ssh server
########################################
sudo apt install openssh-server -y
arp -a | grep 00-15

ssh ahmedh@192.168.1.50
ssh ahmedh@192.168.1.78
ssh ahmedh@172.21.74.99

sudo chown -R ahmedh:ahmedh /home/ahmedh/artifactory
sudo chown -R ahmedh:ahmedh /home/ahmedh/project
sudo chown -R nobody:nogroup /home/ahmedh/shared
##########################################
#       Setup static ip
#########################################
ip addr show
sudo nano /etc/netplan/01-netcfg.yaml

network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 172.21.74.99/24
      routes:
        - to: default
          via: 172.21.74.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4

sudo netplan apply
##########################################
#       Install Docker
#########################################
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# Grant access
sudo chown $USER /var/run/docker.sock
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
########################################
#    Install portainer
########################################
sudo docker volume create portainer_data
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest

https://192.168.1.78:9443
https://lab01:9443

https://172.21.74.99:9443
https://lab02.99:9443


########################################
#    Jenkins agent
########################################
sudo apt update
sudo apt install fontconfig openjdk-21-jre
java -version

curl -sO http://172.21.74.223:8080/jnlpJars/agent.jar
echo 'java -jar agent.jar -url http://172.21.74.223:8080/ -secret 1fd4b829f01732d0ae24bac882e72e90c566de31aec14b60818597430e3f1f56 -name lab02 -workDir "/home/ahmedh/jenkins/lab02"' > 'start.sh'

echo 'https://github.mathworks.com/ahmedh/ArtifactsManagement.git' > data.txt

########################################
#    samba
########################################
sudo apt update
sudo apt install samba -y
sudo nano /etc/samba/smb.conf

[shared]
path = /home/ahmedh/shared
browseable = yes
read only = no

sudo systemctl daemon-reload
sudo chown -R ahmedh:ahmedh /home/ahmedh/shared

sudo systemctl start smbd
sudo systemctl start nmbd
sudo systemctl enable smbd
sudo systemctl enable nmbd

sudo systemctl restart smbd
sudo systemctl restart nmbd
sudo smbpasswd -a ahmedh
sudo smbpasswd -e ahmedh


########################################
#    Grant access to MATLAB
########################################
sudo chmod -R 0777 /opt/matlab
sudo chown -R ahmedh:ahmedh /opt/matlab


sudo apt-get update \
    && apt-get install --no-install-recommends --yes \
    wget \
    xvfb \
    unzip \
    ca-certificates \
    python3 3.12\
    python3-pip \
    && apt-get clean \
    && apt-get autoremove

# Ubunutu 24 : https://github.com/mathworks-ref-arch/container-images/blob/main/matlab-deps/r2024b/ubuntu24.04/base-dependencies.txt
sudo apt-get update -y && sudo apt-get install -y gcc g++ gfortran && sudo apt-get clean && sudo apt-get -y autoremove && sudo rm -rf /var/lib/apt/lists/*

sudo apt-get install  --no-install-recommends -y \
  ca-certificates debianutils libasound2t64 libatomic1 libc6 libcairo-gobject2 libcairo2 libcap2 libcrypt1 libcups2t64 libdrm2 libfontconfig1 \
  libfribidi0 libgbm1 libgdk-pixbuf-2.0-0 libgl1 libglib2.0-0t64 libgstreamer-plugins-base1.0-0 libgstreamer1.0-0 libgtk-3-0t64 libice6 \
  libltdl7 libmd0 libnettle8t64 libnspr4 libnss3 libpam0g libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 libsndfile1 \
  libtirpc3t64 libudev1 libuuid1 libwayland-client0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxfont2 libxft2 libxinerama1 libxrandr2 \
  libxt6t64 libxtst6 libxxf86vm1 locales locales-all make net-tools procps sudo unzip zlib1g

MATLAB_RELEASE=R2024b
MATLAB_INSTALL_LOCATION=/opt/matlab/R2024b
MATLAB_PRODUCT_LIST='MATLAB, Simulink, Simulink_Check, Simulink_Design_Verifier, Simulink_Report_Generator, Simulink_Coder, Simulink_Compiler, Simulink_Test, Embedded_Coder, Polyspace_Code_Prover, Polyspace_Bug_Finder, Simulink_Coverage, CI/CD_Automation_for_Simulink_Check'
sudo ./mpm install --release=$MATLAB_RELEASE --destination=$MATLAB_INSTALL_LOCATION --products=$MATLAB_PRODUCT_LIST

sudo ln -s /opt/matlab/R2024b/bin/matlab /usr/local/bin/matlab


# MATLAB Simulink
# Embedded_Coder
# Simulink_Check Simulink_Coder Simulink_Compiler Simulink_Coverage
# Simulink_Design_Verifier Simulink_Report_Generator Simulink_Test
# CI/CD_Automation_for_Simulink_Check

########################################
#    Setup local registery
########################################
docker run -d -p 5000:5000 --name registry registry:2