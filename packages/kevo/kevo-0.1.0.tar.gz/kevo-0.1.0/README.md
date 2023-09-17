[![Tests](https://github.com/delftdata/stateflow-kevo/actions/workflows/run_tests.yml/badge.svg)](https://github.com/delftdata/stateflow-kevo/actions/workflows/run_tests.yml)

# Kevo

Kevo is a purpose-built key-value store, specifically designed to serve as a state-backend for transactional dataflow systems.

It supports incremental (efficient) snapshots, rollbacks, and it offers a selection of three backend engines:

1. `LSMTree` with size-tiered compaction, like Apache's [Cassandra](https://cassandra.apache.org/_/index.html).
2. `HybridLog`, based on Microsoft's [FASTER](https://microsoft.github.io/FASTER/docs/td-research-papers/).
3. `AppendLog`, similar to Riak's [Bitcask](https://riak.com/assets/bitcask-intro.pdf).

It was developed as part of [this](https://github.com/NikosGavalas/tud-thesis) thesis.

#### Requirements
See [setup.py](./setup.py).

#### Usage
To install run `pip install .`

To try the CLI: `kevo`

Simple example with LSMTree and PathRemote:

```python
from kevo import LSMTree, PathRemote

remote = PathRemote('/tmp/my-snapshot-store')

db = LSMTree(remote=remote)
# by default the db creates the directory "./data" to store the data and indices
db[b'a'] = b'1'
db[b'b'] = b'2'
# since we're using a Remote, we can create a snapshot to save the state we
# have so far (the key-value pairs) in another directory (which can be mounted)
# elsewhere
db.snapshot(id=0)

db[b'a'] = b'3'
db[b'b'] = b'4'
db.snapshot(id=1)

db.close()

# you can remove the local directory "./data" here, the data will be restored
# via the PathRemote we're using

db = LSMTree(remote=remote)
print(db[b'a'])  # b'3'
print(db[b'b'])  # b'4'

db.restore(version=0)
print(db[b'a'])  # b'1'
print(db[b'b'])  # b'2'

db.close()
```

#### Tests
To run all tests: `python -m unittest discover -s tests`

#### Documentation

Full documentation is not available yet.
