from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from cdk_fck_nat import FckNatInstanceProvider
from constructs import Construct

class CdkPynatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Public elastic IPs for the NAT Instance
        nat_eip = ec2.CfnEIP(self, "NatElasticIP", domain="vpc")
        nat_eip.apply_removal_policy(RemovalPolicy.RETAIN)

        nat_gateway_provider = FckNatInstanceProvider(
            instance_type=ec2.InstanceType("t4g.nano"),
            eip_pool=[nat_eip.attr_allocation_id]
        )

        vpc = ec2.Vpc(
            self,
            "Vpc",
            nat_gateway_provider=nat_gateway_provider,
            nat_gateways=1,
        )
        nat_gateway_provider.security_group.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.all_traffic()
        )

        # Prints the public IP of the nat after the deployment
        CfnOutput(self, "NatPublicIP", value=nat_eip.attr_public_ip)
