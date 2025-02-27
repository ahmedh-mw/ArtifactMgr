// Copyright 2025 The MathWorks, Inc.
node{
    env.PATH = "D:/sb/Bslcicd_0227/matlab/bin;$PATH";
    cleanWs();dir("scm"){checkout scm;};

    stage('Run MATLAB Tasks'){
        runMATLABCommand "runMatlabTasks();"
    }
}