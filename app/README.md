To run app:

* Launch kafka
* faust -A crawler worker -l info
* faust -A datasaver worker -l info
* python producer.py
