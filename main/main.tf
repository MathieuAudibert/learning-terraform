provider "aws"{
    region = "eu-west-3"
}

resource "ec2" "instance1" {
    ami           = "ami-055fc45692cb976ff"
    instance_type = "t2.micro" 
}