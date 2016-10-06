apt-get -qqy update
apt-get -qqy install python-pip

# Install Git
# -----------
apt-get install -y git-core

# Install Node js
# ---------------
apt-get install -y python-software-properties python g++ make
add-apt-repository -y ppa:chris-lea/node.js
apt-get update
apt-get install -y nodejs

# Upgrade NPM
# -----------
npm update -g npm

pip install flask
pip install git+https://github.com/dawran6/yelpy.git

vagrantTip="[35m[1mThe shared directory is located at /vagrant\nTo access your shared files: cd /vagrant(B[m"
echo -e $vagrantTip > /etc/motd
