"""Defines a launcher for running jobs on AWS EC2.

Steps
-----

1. Stages the environment to a new working directory
2. Writes a user data script which runs the job, then shuts down the instance
3. Starts an EC2 instance with the user data script, copying the staged
   environment
4. Writes information about the running job to the working directory

This allows for repeatability by just scheduling the same job again. The
job can be debugged by SSHing into the instance and viewing the log file.

Requirements
------------

Since this launcher runs on EC2, it should be possible to install all
dependencies using ``pip install .`` from the root directory of the reposito

EC2 Instance Types
------------------

Below are some EC2 instances which can be used for training models. Prices are
quoted either for on-demand GPUs of August 16th, 2023, although spot instances
and reserved instances can be significantly cheaper.

This list is non-exhaustive, since there are additional differences between
instances based on network bandwidth, local storage, and other considerations.

- ``V100`` - 32 GB GPU memory, SM70
    - ``p3.2xlarge``: 1 GPU, 8 vCPUs, 61 GB RAM, $3.06/hour/GPU
    - ``p3.8xlarge``: 4 GPUs, 32 vCPUs, 244 GB RAM, $3.06/hour/GPU
    - ``p3.16xlarge``: 8 GPUs, 64 vCPUs, 488 GB RAM, $3.06/hour/GPU
    - ``p3dn.24xlarge``: 8 GPUs, 96 vCPUs, 768 GB RAM, $3.90/hour/GPU
- ``A100`` - 40 GB (P4d) or 80 GB (P4de) GPU memory, SM80
    - ``p4d.24xlarge``: 8 GPUs, 96 vCPUs, 1152 GB RAM, $4.10/hour/GPU
    - ``p4de.24xlarge``: 8 GPUs, 96 vCPUs, 1152 GB RAM, $5.12/hour/GPU
- ``M60`` - 8 GB GPU memory, SM50
    - ``g3s.xlarge``: 1 GPU, 4 vCPUs, 30 GB RAM, $0.75/hour/GPU
    - ``g3.4xlarge``: 1 GPU, 16 vCPUs, 122 GB RAM, $1.14/hour/GPU
    - ``g3.8xlarge``: 2 GPUs, 32 vCPUs, 244 GB RAM, $1.14/hour/GPU
    - ``g3.16xlarge``: 4 GPUs, 64 vCPUs, 488 GB RAM, $1.14/hour/GPU
- ``T4`` - 16 GB GPU memory, SM75
    - ``g4dn.xlarge``: 1 GPU, 4 vCPUs, 16 GB RAM, $0.526/hour/GPU
    - ``g4dn.2xlarge``: 1 GPU, 8 vCPUs, 32 GB RAM, $0.752/hour/GPU
    - ``g4dn.4xlarge``: 1 GPU, 16 vCPUs, 64 GB RAM, $1.204/hour/GPU
    - ``g4dn.8xlarge``: 1 GPU, 32 vCPUs, 128 GB RAM, $2.176/hour/GPU
    - ``g4dn.12xlarge``: 4 GPUs, 48 vCPUs, 192 GB RAM, $0.978/hour/GPU
    - ``g4dn.16xlarge``: 1 GPUs, 64 vCPUs, 256 GB RAM, $4.352/hour/GPU
    - ``g4dn.metal``: 8 GPUs, 96 vCPUs, 384 GB RAM, $0.978/hour/GPU
- ``T4G`` - 16 GB GPU memory, SM75
    - ``g5g.xlarge``: 1 GPU, 4 vCPUs, 8 GB RAM, $0.42/hour/GPU
    - ``g5g.2xlarge``: 1 GPU, 8 vCPUs, 16 GB RAM, $0.556/hour/GPU
    - ``g5g.4xlarge``: 1 GPU, 16 vCPUs, 32 GB RAM, $0.828/hour/GPU
    - ``g5g.8xlarge``: 1 GPU, 32 vCPUs, 64 GB RAM, $1.372/hour/GPU
    - ``g5g.16xlarge``: 2 GPU, 64 vCPUs, 128 GB RAM, $1.372/hour/GPU
    - ``g5g.metal``: 2 GPU, 64 vCPUs, 128 GB RAM, $1.372/hour/GPU
- ``A10G`` - 24 GB GPU memory, SM86
    - ``g5.xlarge``: 1 GPU, 4 vCPUs, 16 GB RAM, $1.006/hour/GPU
    - ``g5.2xlarge``: 1 GPU, 8 vCPUs, 32 GB RAM, $1.212/hour/GPU
    - ``g5.4xlarge``: 1 GPU, 16 vCPUs, 64 GB RAM, $1.624/hour/GPU
    - ``g5.8xlarge``: 1 GPU, 32 vCPUs, 128 GB RAM, $2.448/hour/GPU
    - ``g5.12xlarge``: 4 GPUs, 48 vCPUs, 192 GB RAM, $1.418/hour/GPU
    - ``g5.16xlarge``: 1 GPUs, 64 vCPUs, 256 GB RAM, $4.096/hour/GPU
    - ``g5.24xlarge``: 4 GPUs, 96 vCPUs, 384 GB RAM, $2.036/hour/GPU
    - ``g5.48xlarge``: 8 GPUs, 192 vCPUs, 768 GB RAM, $2.036/hour/GPU
- ``Trainium`` - 32 GB Accelerator memory (Amazon-specific training chip)
    - ``trn1.2xlarge``: 1 accelerator, 8 vCPUs, 32 GB RAM, 1.34/hour/accelerator
    - ``trn1.32xlarge``: 16 accelerators, 128 vCPUs, 512 GB RAM, 1.34/hour/accelerator
    - ``trn1n.32xlarge``: Same as ``trn1.32xlarge`` but with double network bandwidth
"""
