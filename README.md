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

### Detailed instructions for GCE 

On a fresh node

    sudo apt install -y git default-jdk tmux
    git clone https://github.com/birdsarah/faust-selenium.git
    wget https://www-us.apache.org/dist/kafka/2.3.0/kafka_2.12-2.3.0.tgz
    tar xzvf kafka_2.12-2.3.0.tgz
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    ./miniconda/bin/conda init
    source ~/.bashrc
    cd faust-selenium
    conda env create -f environment.yaml

Install monitoring agent if needed: [https://app.google.stackdriver.com/settings/accounts/agent]

Zookeeper and kafka (update supervisord conf files depending on cluster config)

    tmux  # so we can disconnect (could also use supervisor as a daemon)
    conda activate faust-selenium
    cd kafka
    supervisord -c kafka.conf (or as appropriate)

Crawler

    tmux
    conda activate faust-selenium
    cd crawler






---

## ToDo

* When unbranded firefox is available on conda-forge, use it
* Package

