#!/usr/bin/env bash

apt-get update
apt-get install git
apt install default-jre

wget -q https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
chmod +x miniconda.sh
./miniconda.sh -b -p /home/vagrant/miniconda
# ensures conda loaded in shell
echo "source /home/vagrant/miniconda/etc/profile.d/conda.sh" >> /home/vagrant/.bashrc
source /home/vagrant/miniconda/etc/profile.d/conda.sh
chown -R vagrant:vagrant /home/vagrant/miniconda

cd /vagrant
conda env create -f environment.yml

source /home/vagrant/miniconda/etc/profile.d/conda.sh
conda activate topicmodel

python setup.py install
pytest topic_model_to_Shiny_app/tests/

