To run cat crawler:

Set your topic partitions in kafka settings or manually create topics with
desired numbers of partitions. I haven't investigated all the performance
parameters. BUT you need to have at least as many partitions as you want
workers that will work on that topic. In particular if we want 100 crawler
workers the topic 'crawl-request' needs at least 100 workers.

Apparently you need to specify the port manually. On kubernetes this won't be
an issue as each worker will be in their own pod.

* Launch kafka
* Activate environment
* From this directory launch workers. You can launch multiple for each type (esp datasaver and crawler):
  * faust -A datasaver.sqlite worker -l info -p 6066
  * faust -A producer worker -l info -p 6067
  * faust -A websocket worker -l info -p 6068
  * faust -A crawler worker -l info -p 6083
* To use simple_producer for testing:
  * faust -A simple_producer worker -l info -p 6067
  * faust -A simple_producer send simple_request '{"url": "http://somewhere-to-crawl.com"}'

* Have not yet figured out:
  * Coordinating websockets and crawlers so one websocket per crawler
  * What happens if you try and start two websockets?
