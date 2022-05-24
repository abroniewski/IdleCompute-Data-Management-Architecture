# Partition dataset or assign chunks based on schedule (ADAM)
#   INPUT:
#       pandas.dataframe -> current_job_schedule
#       analysis job dataset
#   OUTPUT:
#       pandas.dataframe -> current_job_schedule updated
#       EITHER updated dataset stored in /../data/processed/YYYY/MM/scheduled/IdleHostID
#       OR return the parameters/variables needed to distributed Hadoop chunks
#   SCOPE:
#       For all jobs that are not started, check to see if the required hosts (VMs) are available. If all VMs are
#       available:
#       EITHER add key to each row of data based on number of nodes that will be used. Store dataset in scheduled
#       OR see if we can set which location Hadoop sends its chunks to? Output would be a hadoop call/function
#       update scheduled current_job_schedule[status == "scheduled"]

# Note: The Name Node will replicate blocks to data nodes based upon rack configuration, replication factor and node
# availability, so even if you do managed to get a block on two particular data nodes, if one of those nodes goes
# down, the name node will replicate the block to another node. Your requirement is also assuming a replication
# factor of 1, which doesn't give you any data redundancy (which is a bad thing if you lose a data node). Let the
# namenode manage block assignments and use the balancer periodically if you want to keep your cluster evenly
# distributed


import pyarrow.parquet as pq

#TODO: iterate through folder structure to find file
dataset = pq.read_table('../data/processed/2022/03/VKY001-001-AB12')
parquet_file = pq.ParquetFile('../data/processed/2022/03/VKY001-001-AB12')
print(parquet_file.metadata)
workload = [[20, 30, 50]]

