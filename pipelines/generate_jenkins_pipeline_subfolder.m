function generate_jenkins_pipeline_subfolder()
    cp = openProject(pwd);

    op = padv.pipeline.JenkinsOptions;
    % op.PipelineArchitecture = "IndependentModelParallelJobs"; # SingleJob, SerialJobs, SerialJobsGroupPerTask
    op.PipelineArchitecture = "IndependentModelParallelJobs";
    op.MatlabInstallationLocation = "D:/sb/Bslcicd_0225/matlab/bin";
    op.AgentLabel = "padv_win_agents";
    op.StopOnStageFailure = true;
    op.RunprocessCommandOptions.GenerateJUnitForProcess = true;
    op.ReportPath = "$PROJECTROOT$/PA_Results/Report/ProcessAdvisorReport";
    padv.pipeline.generatePipeline(op, "CIPipeline");
    % Copy the pipeline and dag files on the project root folder
    copyfile( fullfile(cp.RootFolder, 'derived', 'pipeline' , '*'), cp.RootFolder);
end