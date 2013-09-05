Rendering connectivity.

Full write-up here: http://richstoner.github.com/blog/2013/03/29/rendering-connectivity/

### Porting from AWS to UCSD's Triton Compute resource

	it takes an m3.2xlarge 15 minutes to render a single frame

	an m3.2xlarge has 8 virtual cores @ 26 compute units (equiv) with 30gigs of ram

	the m3.2xlarge costs $1.00/hour

	the TSCC cost is $0.025/SU, with most compute nodes in Hotel having 64GB/ram

	For the cost of running an m3.2xlarge for 1 hour, I could purchase 40 SU

	I could max out a single Hotel node (16 cores, 64GB ram) for 2.5 hours

	...or, I could run a smaller job: 8 cores w/ 32 GB ram for 5 hours

	So effectively, tscc is 5x cheaper than running the equivalent on ec2.
