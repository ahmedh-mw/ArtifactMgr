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

# Linux container       
docker run --init -it \
        -v /home/ahmedh/artifactory:/home/ahmedh/artifactory \
        -v /home/ahmedh/project/derived/licenses:/opt/matlab/R2024b/licenses \
        --entrypoint /bin/bash \
        --name matlab_padv matlab_padv:R2024b

/usr/bin/docker create --name 3a44960a402f40d08e0e34aa78717c8f_localhost5000matlab_padvR2024b_aa18cf \
        --label 86052a --workdir /__w/ArtifactMgr/ArtifactMgr  \
        -e "HOME=/home/matlab" -e GITHUB_ACTIONS=true -e CI=true -v "/var/run/docker.sock":"/var/run/docker.sock" \
        -v "/home/ahmedh/project/derived/licenses":"/opt/matlab/R2024b/licenses" -v "/home/ahmedh/artifactory":"/home/ahmedh/artifactory" \
        -v "/home/ahmedh/gh/lingh1/_work":"/__w" -v "/home/ahmedh/gh/lingh1/externals":"/__e":ro -v "/home/ahmedh/gh/lingh1/_work/_temp":"/__w/_temp" \
        -v "/home/ahmedh/gh/lingh1/_work/_actions":"/__w/_actions" -v "/home/ahmedh/gh/lingh1/_work/_tool":"/__w/_tool" \
        -v "/home/ahmedh/gh/lingh1/_work/_temp/_github_home":"/github/home" -v "/home/ahmedh/gh/lingh1/_work/_temp/_github_workflow":"/github/workflow" \
        --entrypoint "tail" localhost:5000/matlab_padv:R2024b "-f" "/dev/null"

/usr/bin/docker start 049299ba0c09d2636b3dc13c5a6635ad0c0431b50f8c322cfec4a7d269a5471c
/usr/bin/docker ps --all --filter id=049299ba0c09d2636b3dc13c5a6635ad0c0431b50f8c322cfec4a7d269a5471c --filter status=running --no-trunc --format "{{.ID}} {{.Status}}"
/usr/bin/docker inspect --format "{{range .Config.Env}}{{println .}}{{end}}" 049299ba0c09d2636b3dc13c5a6635ad0c0431b50f8c322cfec4a7d269a5471c

docker exec -it 049299ba0c09d2636b3dc13c5a6635ad0c0431b50f8c322cfec4a7d269a5471c /bin/bash