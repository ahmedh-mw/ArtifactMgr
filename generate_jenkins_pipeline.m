% Copyright 2025 The MathWorks, Inc.

function generate_jenkins_pipeline()
    cp = openProject(pwd);

    op = padv.pipeline.JenkinsOptions;
    op.PipelineArchitecture = "IndependentModelParallelJobs";
    op.GeneratedPipelineDirectory = fullfile(cp.RootFolder, "pipelines", "derived");
    op.MatlabInstallationLocation = "D:/sb/Bslcicd_0225/matlab/bin";
    op.GeneratedPipelineDirectory = "scm";
    op.AgentLabel = "padv_win_agents";
    op.StopOnStageFailure = true;
    op.RunprocessCommandOptions.GenerateJUnitForProcess = true;
    op.ReportPath = "$PROJECTROOT$/PA_Results/Report/ProcessAdvisorReport";
    padv.pipeline.generatePipeline(op, "CIPipeline");
end