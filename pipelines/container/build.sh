########################################
#    Gitlab server
########################################
$MATLAB_HOME="$pwd\\derived"

docker pull gitlab/gitlab-ce
docker run --detach `
    --publish 443:443 --publish 80:80 --publish 22:22 `
    --name gitlab `
    --restart always `
    --volume $MATLAB_HOME/gitlab/config:/etc/gitlab `
    --volume $MATLAB_HOME/gitlab/logs:/var/log/gitlab `
    --volume $MATLAB_HOME/gitlab/data:/var/opt/gitlab `
    --name gitlab01 gitlab/gitlab-ce:latest

docker exec -it gitlab01 grep Password: /etc/gitlab/initial_root_password
########################################
#    Build matlab image
########################################
scp -r . ahmedh@lab02:/home/ahmedh/project
scp -r pipelines ahmedh@lab01:/home/ahmedh/project
scp -r derived ahmedh@lab01:/home/ahmedh/project
scp -r id_ed* ahmedh@lab02:/home/ahmedh/.ssh
scp -r id_ed*.* ahmedh@lab02:/home/ahmedh/.ssh

sudo docker build -f Matlab.R2024b.Dockerfile \
        --build-arg MATLAB_RELEASE=R2024b \
        --build-arg MATLAB_PRODUCT_LIST='MATLAB Simulink Simulink_Check Simulink_Design_Verifier Simulink_Report_Generator Simulink_Coder Simulink_Compiler Simulink_Test Embedded_Coder Polyspace_Code_Prover Polyspace_Bug_Finder Simulink_Coverage CI/CD_Automation_for_Simulink_Check' \
        -t matlab_padv:R2024b .

docker tag matlab_padv:R2024b localhost:5000/matlab_padv:R2024b
docker push localhost:5000/matlab_padv:R2024b
########################################
#    Create matlab container
########################################
$MATLAB_RELEASE="R2024b"

# mkdir $MATLAB_HOME\\licenses -force | out-null
# mkdir -p $MATLAB_HOME/data -force | out-null
# cp license.dat $MATLAB_HOME\\licenses\ -force | out-null
# cp -r ProcessAdvisorExample /home/matlab/data/ProcessAdvisorExample 

docker run --init -it `
        -v $MATLAB_HOME\\data:/home/matlab/data `
        -v $MATLAB_HOME\\licenses:/opt/matlab/${MATLAB_RELEASE}/licenses `
        --entrypoint /bin/bash `
        --name matlab_padv matlab_padv:R2024b

docker exec -it matlab_padv /bin/bash

########################################
#    Run containers
########################################
sudo docker exec -it matlab_demo matlab -batch ver
sudo docker exec -it matlab_demo matlab -nojvm -nodisplay -nodesktop -batch ver


docker run --init -it --entrypoint /bin/bash --name matlab_padv11 matlab_padv:R2024b


sudo docker run --init -it --entrypoint /bin/bash \
        -v /home/ahmedh/data:/home/matlab/data \
        --name matlab_padv2 matlab_padv:R2024b
opt