# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |backend|
    backend.customize ["modifyvm", :id, "--groups", "/Kafka (prototype)"]
    backend.memory = 4096
    backend.cpus = 2
  end

  config.vm.define "kafka" do |instance|
    instance.vm.provider :virtualbox do |backend|
      backend.name = "kafka"
    end
    instance.vm.hostname = "kafka"
    instance.vm.box = "ubuntu/focal64"
    instance.vm.network "private_network", ip: "192.168.56.71"
    instance.vm.provision "shell", path: "bootstrap.sh", :args => ["192.168.56.71"]
  end
end