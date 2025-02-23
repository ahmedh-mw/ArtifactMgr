// Copyright 2025 The MathWorks, Inc.
node{
    env.PATH = "D:/sb/Bslcicd_0209/matlab/bin;$PATH";
    cleanWs();checkout scm;

    stage('Run MATLAB Tasks'){
        runMATLABCommand "runMatlabTasks();"
    }
}