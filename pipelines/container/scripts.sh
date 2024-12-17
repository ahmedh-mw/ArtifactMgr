

-v /mathworks/devel/jobarchive/Bslcicd/current/build/matlab/licenses/license.dat:/usr/share/matlab/licenses/license.dat \

########################################
#    Create matlab container
########################################
$MATLAB_HOME="d:\\containers\m1"
$MATLAB_RELEASE="r2024a"



docker run --init -it --name matlab_padv matlab_padv:r2024a `
    -v "$MATLAB_HOME/licenses":"/opt/matlab/${MATLAB_RELEASE}/licenses" `
    -v "$MATLAB_HOME/home":/home/matlab `
    matlab -batch ver

mkdir $MATLAB_HOME\\licenses -force | out-null
mkdir -p $MATLAB_HOME/data -force | out-null
cp license.dat $MATLAB_HOME\\licenses\ -force | out-null

########################################
########################################
########################################
########################################
########################################
sudo docker build -f regent.Dockerfile -t regent_2024_11_14:r2023b .
docker run --init -it `
        --env MLM_LICENSE_TOKEN="ahmedh@mathworks.com|LocalCI|AAARbRdGSfLLrpUkqaT8MFKxtAQh4mpta7T+x+43JBM3bslQcZWSNXQf+tq25mQ9/p6HTN8douwFlzjJq1EnJJtR8WKtUB95zsL70dmTIzGJGJmjBmRBKwkAMEgWEPbFb6dmxKG1JifXj2sHrlTRIEWaHby7V5OFy/FvoCpWJStToNxv6R6V3Ak" `
        --entrypoint /bin/bash `
        --name regent1 regent_2024_11_14:r2023b

docker run --init -it `
        --entrypoint /bin/bash `
        --name regent1 regent_2024_11_14v2:r2023b

# -licenseToken 
matlab-batch  -nodesktop  "ver"


docker build -f matlab.Dockerfile -t matlab_2024_12_06:r2023b .


docker run --init -it `
        --env MLM_LICENSE_TOKEN="ahmedh@mathworks.com|LocalCI|AAARbRdGSfLLrpUkqaT8MFKxtAQh4mpta7T+x+43JBM3bslQcZWSNXQf+tq25mQ9/p6HTN8douwFlzjJq1EnJJtR8WKtUB95zsL70dmTIzGJGJmjBmRBKwkAMEgWEPbFb6dmxKG1JifXj2sHrlTRIEWaHby7V5OFy/FvoCpWJStToNxv6R6V3Ak" `
        --entrypoint /bin/bash `
        -v "$(pwd)/licenses:/opt/matlab/licenses" `
        -v "$(pwd)/padv23bParallelExample:/home/matlab_user/project" `
        --name matlab1 matlab_2024_12_06:r2023b

matlab.Dockerfile


docker attach matlab1

sudo xvfb-run matlab-batch "openProject(pwd);rptObj=padv.ProcessAdvisorReportGenerator;generateReport(rptObj)"


sudo xvfb-run matlab-batch "matlabshared.supportpkg.getInstalled"





docker run --init -it --name mypython python:latest bash


matlab_2024_12_06:r2023b