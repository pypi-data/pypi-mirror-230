# Mobius-python

# Table of contents

 - [Description](#descr)
 - [Installation](#install)
 
# <a name="descr"></a>Description
The Mobius API is a Python library that simplifies the native cloud interfaces for various clouds such as FABRIC, 
Chameleon and adds many additional capabilities that are commonly used to create experiments.

The easiest way to get started using Mobius API is to use the example shown below.

```
    # Create a controller obect
    # Default slice name is picked up from the config file
    controller = Controller(config_file_location="./config.yml")
    # User specified slice name is used to identify the resources
    #controller = Controller(config_file_location="./config.yml", slice_name="test-slice")
    # Provision the resources as specified in the configuration file
    controller.create()
    # Get the provisioned resources
    resources = controller.get_resources()
    # Print the resources provisioned
    for r in resources:
        print(r)
        print(r.list_nodes())
```

User is expected to provide a config file `config.yml` containing their credentials and resource parameters. Template
`mobius/config/config_template.yml` can be used to create a `config.yml`. Please find below the list of the parameters 
that must be updated.

- Update the SSH public and private key files to be used for the provisioned VMs/Bare Metals
```
runtime:
  slice-private-key-location: /Users/kthare10/.ssh/id_rsa
  slice-public-key-location: /Users/kthare10/.ssh/id_rsa.pub
```
- Update FABRIC credentials
  - Location of the user's FABRIC tokens
  - User's Bastion User name
  - User's Fabric Bastion Private Key
  - User's Project Id
```
fabric:
  token-location: /Users/kthare10/renci/code/fabric/notebooks/tokens.json
  bastion-user-name: kthare10_0011904101
  bastion-key-location: /Users/kthare10/.ssh/fabric-bastion
  project_id: b9847fa1-13ef-49f9-9e07-ae6ad06cda3f
```

- Update Chameleon credentials
  - UserName
  - Password
  - Key Pair
  - Project Name
  - Project Id
```
chameleon:
  user: kthare10
  password: 
  key_pair: kthare10
  project_name: CH-822154
  project_id:
    tacc: a400724e818d40cbba1a5c6b5e714462
    uc: ae76673270164b048b59d3bd30676721
    kvm: a400724e818d40cbba1a5c6b5e714462
    edge:
```
- Update the resource counts
  - Set count to 0 or more depending on where the resources should be provisioned.
  - Copy and add more resource blocks if resources are needed at additional sites
  - Change other parameters as needed
```
resources:
    - resource:
        type: VM
        site: RENC # use FABRIC.RANDOM to choose a random site instead
        count: 1
        image: default_rocky_8
        nic_model: NIC_Basic # NIC_Basic(SRIOV), NIC_ConnectX_5 => 25GB, NIC_ConnectX_6 => 100GB
        name_prefix: node
        network:
          type: IPv6 # Allowed values IPv4 or IPv6
        flavor:
          cores: 2
          ram: 8
          disk: 10

    - resource:
        type: Baremetal
        site: KVM@TACC
        count: 1
        image: CC-CentOS8
        network:
          type: sharednet1
        name_prefix: node
        flavor:
          name: m1.large
```

# <a name="install"></a>Installation
You can install using the following command
```
pip install mobius-py
```

## Requirements:
Requires python 3.9 or above version