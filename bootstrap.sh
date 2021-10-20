#!/usr/bin/env bash
set -o errexit
set -o nounset

apt-get update -y
apt-get upgrade -y

apt install default-jdk -y

curl https://archive.apache.org/dist/kafka/2.8.1/kafka_2.13-2.8.1.tgz -o /tmp/kafka.tgz
mkdir /home/vagrant/kafka && cd /home/vagrant/kafka
tar -xvzf /tmp/kafka.tgz --strip 1

mkdir /home/vagrant/kafka/logs
chown vagrant:vagrant -R /home/vagrant/kafka

sed -i \
  's/log.dirs=\/tmp\/kafka-logs/log.dirs=\/home\/vagrant\/kafka\/logs/g' \
  /home/vagrant/kafka/config/server.properties

sed -i \
  's/#listeners=PLAINTEXT:\/\/:9092/listeners=PLAINTEXT:\/\/0.0.0.0:9092/g' \
  /home/vagrant/kafka/config/server.properties

sed -i \
  's/#advertised.listeners=PLAINTEXT:\/\/your.host.name:9092/advertised.listeners=PLAINTEXT:\/\/192.168.50.71:9092/g' \
  /home/vagrant/kafka/config/server.properties

cat <<EOF >/etc/systemd/system/zookeeper.service
[Unit]
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=vagrant
ExecStart=/home/vagrant/kafka/bin/zookeeper-server-start.sh /home/vagrant/kafka/config/zookeeper.properties
ExecStop=/home/vagrant/kafka/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

systemctl enable zookeeper

#listeners=PLAINTEXT://0.0.0.0:9092

cat <<EOF >/etc/systemd/system/kafka.service
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=vagrant
ExecStart=/bin/sh -c '/home/vagrant/kafka/bin/kafka-server-start.sh /home/vagrant/kafka/config/server.properties > /home/vagrant/kafka/logs/kafka.log 2>&1'
ExecStop=/home/vagrant/kafka/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

systemctl enable kafka
systemctl start kafka
