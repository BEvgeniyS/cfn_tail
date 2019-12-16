# cfn_tail

Tails cloudformation events and returns on complete.  
AWS authentication is currently limited to default chain (environment/profile/ec2 metadata etc)

## Arguments

* '-s', '--stack-name' - name of CFN stack
* '-n', '--initial-events-count' Number of initial events. Since this is primarily intended to be used with deployments, the default is 0.
* '-c', '--no-stop-on-complete'  Don't stop after CREATE_COMPLETE or UPDATE_COMPLETE has reached. Only exit on user request (Ctrl+c)
