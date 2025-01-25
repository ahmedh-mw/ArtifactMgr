function generate_jenkins_pipeline()
    cp = openProject('scm');

    op = padv.pipeline.JenkinsOptions;
    % op.PipelineArchitecture = "IndependentModelParallelJobs"; # SingleJob, SerialJobs, SerialJobsGroupPerTask
    op.PipelineArchitecture = "SerialJobsGroupPerTask";
    op.GeneratedPipelineDirectory = fullfile(cp.RootFolder, "pipelines", "derived");
    op.MatlabInstallationLocation = "D:/sb/Bslcicd_1217/matlab/bin";
    op.AgentLabel = "padv_win_agents";
    op.StopOnStageFailure = true;
    op.RunprocessCommandOptions.GenerateJUnitForProcess = true;
    op.ReportPath = "$PROJECTROOT$/PA_Results/Report/ProcessAdvisorReport";
    padv.pipeline.generatePipeline(op, "CIPipeline");
end