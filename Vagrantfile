# -*- mode: ruby -*-
Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/bionic64"
  config.vm.hostname = "ubuntu-test"
  config.vm.provision :shell, path: "bootstrap.sh"
end
