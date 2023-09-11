# HRMES
A consistency-preserving api of the HRMES storage model (Highly Reliable Mobile Edge Storage).
It offloads the mission-critical stateful applications to the edge and ensures the reliable tail latency and strong consistency guarantees.

### Installation
```
pip install hrmes-python
```

### Get started
How to create the section:
 
```Python
# import hrmes-python as hrmes
# Prepare the url and port of the server you'd like to connect to 
# And give the keys of data that you want to cache as a parameter
url = "url"
port = 1337
keys = ["a-key", "b-key"]
# id = hrmes.create_section(url, port, keys)
```
How to access to the cache:
```Python
# Read the data from the cache
key = "a-key"
# hrmes.read_data(id, key)

value = "a-new-value"
# write the data to the cache
# hrmes.write_data(id, key, value)
```
How to commit the updates to the server:
```Python
# Read the data from the cache
# hrmes.commit(id)
```