source ./setNodesIps.sh -p

for i in {1..3} 
do
    node=NODE$i
    nodeLocal=NODE${i}_LOC
    ssh -i ~/.ssh/AWSCourses.pem ubuntu@${!node} "bash -s" -- < ./installCassandra.sh
    ssh -i ~/.ssh/AWSCourses.pem ubuntu@${!node} "bash -s" -- < ./confCassandra.sh ${!nodeLocal}
done
