// Copyright 2025 The MathWorks, Inc.
node{
    env.PATH = "<MATLAB executable path>;$PATH";
    cleanWs();checkout scm;

    stage('Run MATLAB Tasks'){
        runMATLABCommand "runMatlabTasks();"
    }
}