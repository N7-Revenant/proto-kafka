#!/usr/bin/env bash
set -o errexit
set -o nounset

typeset -r VM_IP_ADDRESS=${1}
if [[ -z "${VM_IP_ADDRESS}" ]]; then
  echo "ERROR: IP address is required"
  exit 1
fi

apt-get update -y
apt-get upgrade -y

apt install default-jdk -y

curl https://archive.apache.org/dist/kafka/2.8.1/kafka_2.13-2.8.1.tgz -o /tmp/kafka.tgz

mkdir /home/vagrant/kafka1 && cd /home/vagrant/kafka1
tar -xvzf /tmp/kafka.tgz --strip 1

mkdir /home/vagrant/kafka1/logs
chown vagrant:vagrant -R /home/vagrant/kafka1

sed -i \
  's/broker.id=0/broker.id=1/g' \
  /home/vagrant/kafka1/config/server.properties

sed -i \
  's/log.dirs=\/tmp\/kafka-logs/log.dirs=\/home\/vagrant\/kafka1\/logs/g' \
  /home/vagrant/kafka1/config/server.properties

sed -i \
  's/#listeners=PLAINTEXT:\/\/:9092/listeners=PLAINTEXT:\/\/0.0.0.0:19092/g' \
  /home/vagrant/kafka1/config/server.properties

sed -i \
  's/#advertised.listeners=PLAINTEXT:\/\/your.host.name:9092/advertised.listeners=PLAINTEXT:\/\/'"${VM_IP_ADDRESS}"':19092/g' \
  /home/vagrant/kafka1/config/server.properties

sed -i \
  's/offsets.topic.replication.factor=1/auto.create.topics.enable=false\noffsets.topic.replication.factor=3/g' \
  /home/vagrant/kafka1/config/server.properties

mkdir /home/vagrant/kafka2 && cd /home/vagrant/kafka2
tar -xvzf /tmp/kafka.tgz --strip 1

mkdir /home/vagrant/kafka2/logs
chown vagrant:vagrant -R /home/vagrant/

sed -i \
  's/broker.id=0/broker.id=2/g' \
  /home/vagrant/kafka2/config/server.properties

sed -i \
  's/log.dirs=\/tmp\/kafka-logs/log.dirs=\/home\/vagrant\/kafka2\/logs/g' \
  /home/vagrant/kafka2/config/server.properties

sed -i \
  's/#listeners=PLAINTEXT:\/\/:9092/listeners=PLAINTEXT:\/\/0.0.0.0:29092/g' \
  /home/vagrant/kafka2/config/server.properties

sed -i \
  's/#advertised.listeners=PLAINTEXT:\/\/your.host.name:9092/advertised.listeners=PLAINTEXT:\/\/'"${VM_IP_ADDRESS}"':29092/g' \
  /home/vagrant/kafka2/config/server.properties

sed -i \
  's/offsets.topic.replication.factor=1/auto.create.topics.enable=false\noffsets.topic.replication.factor=3/g' \
  /home/vagrant/kafka2/config/server.properties

mkdir /home/vagrant/kafka3 && cd /home/vagrant/kafka3
tar -xvzf /tmp/kafka.tgz --strip 1

mkdir /home/vagrant/kafka3/logs
chown vagrant:vagrant -R /home/vagrant/kafka3

sed -i \
  's/broker.id=0/broker.id=3/g' \
  /home/vagrant/kafka3/config/server.properties

sed -i \
  's/log.dirs=\/tmp\/kafka-logs/log.dirs=\/home\/vagrant\/kafka3\/logs/g' \
  /home/vagrant/kafka3/config/server.properties

sed -i \
  's/#listeners=PLAINTEXT:\/\/:9092/listeners=PLAINTEXT:\/\/0.0.0.0:39092/g' \
  /home/vagrant/kafka3/config/server.properties

sed -i \
  's/#advertised.listeners=PLAINTEXT:\/\/your.host.name:9092/advertised.listeners=PLAINTEXT:\/\/'"${VM_IP_ADDRESS}"':39092/g' \
  /home/vagrant/kafka3/config/server.properties

sed -i \
  's/offsets.topic.replication.factor=1/auto.create.topics.enable=false\noffsets.topic.replication.factor=3/g' \
  /home/vagrant/kafka3/config/server.properties

cat <<EOF >/etc/systemd/system/zookeeper.service
[Unit]
Requires=network.target remote-fs.target
After=network.target remote-fs.target

[Service]
Type=simple
User=vagrant
ExecStart=/home/vagrant/kafka1/bin/zookeeper-server-start.sh /home/vagrant/kafka1/config/zookeeper.properties
ExecStop=/home/vagrant/kafka1/bin/zookeeper-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

systemctl enable zookeeper

cat <<EOF >/etc/systemd/system/kafka1.service
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=vagrant
ExecStart=/bin/sh -c '/home/vagrant/kafka1/bin/kafka-server-start.sh /home/vagrant/kafka1/config/server.properties > /home/vagrant/kafka1/logs/kafka.log 2>&1'
ExecStop=/home/vagrant/kafka1/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

systemctl enable kafka1
systemctl start kafka1

cat <<EOF >/etc/systemd/system/kafka2.service
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=vagrant
ExecStart=/bin/sh -c '/home/vagrant/kafka2/bin/kafka-server-start.sh /home/vagrant/kafka2/config/server.properties > /home/vagrant/kafka2/logs/kafka.log 2>&1'
ExecStop=/home/vagrant/kafka2/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

systemctl enable kafka2
systemctl start kafka2

cat <<EOF >/etc/systemd/system/kafka3.service
[Unit]
Requires=zookeeper.service
After=zookeeper.service

[Service]
Type=simple
User=vagrant
ExecStart=/bin/sh -c '/home/vagrant/kafka3/bin/kafka-server-start.sh /home/vagrant/kafka3/config/server.properties > /home/vagrant/kafka3/logs/kafka.log 2>&1'
ExecStop=/home/vagrant/kafka3/bin/kafka-server-stop.sh
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
EOF

systemctl enable kafka3
systemctl start kafka3
