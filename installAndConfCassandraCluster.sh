source ./setNodesIps.sh -p

option=$1

for i in {1..3} 
do
    node=NODE$i
    nodeLocal=NODE${i}_LOC
    scp -i ~/.ssh/AWSCourses.pem ./setNodesIps.sh ubuntu@${!node}:~/.
    if [ "$option" != "--only-conf" ]; then
        ssh -i ~/.ssh/AWSCourses.pem ubuntu@${!node} "bash -s" -- < ./installCassandra.sh
    fi
    if [ "$option" != "--only-install" ]; then
        ssh -i ~/.ssh/AWSCourses.pem ubuntu@${!node} "bash -s" -- < ./confCassandra.sh ${!nodeLocal}
    fi
done
