# faust-selenium
Selenium runs via faust

## Installation

Kafka and rocksdb-devel are dependencies of faust.

Kafka example setup (source https://kafka.apache.org/quickstart):

    wget kafka
    tar -xzvf kafka_2.12-2.3.0.tgz
    sudo mkdir /opt/kafka
    sudo chown bird:bird /opt/kafka
    mv kafka_2.12-2.3.0 /opt/kafka
    cd /opt/kafka/kafka_2.12-2.3.0
    ./bin/zookeeper-server-start.sh config/zookeeper.properties
    ./bin/kafka-server-start.sh config/server.properties

RocksDB dependency on fedora:

    sudo dnf install rocksdb-devel

Setup environment:

    conda env create -f environment.yaml
    conda activate faust-selenium

Install firefox and get openwpm extension - need unbranded Firefox in a 
firefox-bin directory under crawler and openwpm.xpi in the same place for
loading into the browser. (See OpenWPM repo for info on installation)


ToDo:
* RocksDB dependency should be optional - investigate
* When unbranded firefox is available on conda-forge, use it
* Package
* Ability to have multiple websocket workers so crawlers can talk to their own
