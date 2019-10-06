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

    sudo apt install -y git default-jdk tmux xvfb libdbus-glib-1-2
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
    UNBRANDED_FF69_RELEASE_LINUX_BUILD="https://queue.taskcluster.net/v1/task/TSw-9H80SrqYLYJIYTXGVg/runs/0/artifacts/public/build/target.tar.bz2"
    wget "$UNBRANDED_FF69_RELEASE_LINUX_BUILD"
    tar jxf target.tar.bz2
    rm -rf firefox-bin
    mv firefox firefox-bin
    rm target.tar.bz2
    gsutil cp <location-of-xpi> .
    xvfb :99 &
    supervisord -c ...






---

## ToDo

* When unbranded firefox is available on conda-forge, use it
* Package
* Add a check on start-up for critical parameters and fail out early
* Add retries to crawl request and retry on crawl fail
* Examine failures that do not result in a result being set. 
  See parallel-16 crawl - is it unhandled exception from setting up driver?


---

## Orig instructions from inside crawler (needs cleaning up)

To run crawler:

Set your topic partitions in kafka settings or manually create topics with
desired numbers of partitions. I haven't investigated all the performance
parameters. BUT you need to have at least as many partitions as you want
workers that will work on that topic. In particular if we want 100 crawler
workers the topic 'crawl-request' needs at least 100 partitions.

Also need to make sure the kafka max message size is sufficiently large for the
messages that come up via openwpm. Examples of kafka producer settings are in
parent kafka-properties directory.

* Activate faust-selenium conda environment:
  * conda activate faust-selenium

* Use supervisord (installed via conda) to launch all processes:
  * supervisord -c crawler.conf

* To use simple_producer for testing:
  * faust -A simple_producer send simple_request '{"url": "http://somewhere-to-crawl.com"}'

* Have not yet figured out:
  * Dataloss will occur if websocket server fails / goes down / errors
    * Should co-ordinate websockets and crawlers so one websocket per crawler
  * DB migrations:
    * Delete between changes
  * All the ins-and-outs of db performance and writing:
    * Batches help a lot. For now only starting 1 datasaver worker.

Manager params contain important setup values. The crawl_name parameter
provides a namespace to kafka/faust allowing parallelization of crawls e.g.
ensuring that windows requests picked up by windows crawl while linux requests
are picked up by linux crawl.

To setup a crawl all that should be necessary is to configure a manager_params
and supervisord conf file.

Windows instructions:
* Use seperate windows environment.yaml
* Set firefox_binary_path to something like `"C:\\Users\\Bird\\firefox-bin\\firefox.exe"`
* So far only tested with kafka launched on linux, along with some workers and windows launching websocket, geckodriver, and crawler workers.
* When working with kafka on remote setup need to make sure kafka is accessible from outside IP addresses by setting advertised.host.name and host.name in config/server.properties. And in manager_params, update kafka_broker to the remote ip address.
* Supervisor is not available for windows so crawler processes need to be
    started manually. Make sure the params file matches.

Notes
* Kafka - Can only parallelize for as many partitions as you have, so if you want to have 100 crawlers, make sure the crawl_request topic has 100 partitions.
* Content storage - must also have http instrumentation set to true
* Saving content causes instability - causes websocket to error on large files
