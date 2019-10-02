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

Windows instructions:
* Use seperate windows environment.yaml
* Set firefox_binary_path to something like `"C:\\Users\\Bird\\firefox-bin\\firefox.exe"`
* So far only tested with kafka launched on linux, along with some workers and windows launching websocket, geckodriver, and crawler workers.
* When working with kafka on remote setup need to make sure kafka is accessible from outside IP addresses by setting advertised.host.name and host.name in config/server.properties. And in manager_params, update kafka_broker to the remote ip address.

Notes
* Kafka - Can only parallelize for as many partitions as you have, so if you want to have 100 crawlers, make sure the crawl_request topic has 100 partitions.
* Content storage - must also have http instrumentation set to true
* Saving content causes instability - causes websocket to error on large files
