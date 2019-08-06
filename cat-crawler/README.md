To run cat crawler:

* Launch kafka
* Activate environment
* From this directory:
  * faust -A crawler worker -l info
  * faust -A datasaver worker -l info
  * python producer.py
