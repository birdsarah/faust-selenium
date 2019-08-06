To run cat crawler:

* Launch kafka
* Activate environment
* From this directory:
  * faust -A crawler worker -l info -p 6066
  * faust -A datasaver worker -l info -p 6067
  * faust -A producer worker -l info -p 6068
