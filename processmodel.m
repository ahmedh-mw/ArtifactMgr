function processmodel(pm)
    % Defines the project's processmodel

    arguments
        pm padv.ProcessModel
    end

    % Set default root directory for task results
    pm.DefaultOutputDirectory = fullfile('$PROJECTROOT$', 'PA_Results');
    defaultResultPath = fullfile('$DEFAULTOUTPUTDIR$','$ITERATIONARTIFACT$');
    % defaultTestResultPath = fullfile(defaultResultPath,'test_results');

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Define Shared Queries
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    findModels = padv.builtin.query.FindModels(Name="ModelsQuery");
    % findSlModels = padv.builtin.query.FindArtifacts(ArtifactType="sl_model_file");
    % findModelsWithTests = padv.builtin.query.FindModelsWithTestCases(Parent=findModels);
    % findTestsForModel = padv.builtin.query.FindTestCasesForModel(Parent=findModels);
    findRefModels = padv.builtin.query.FindRefModels(Name="RefModelsQuery");
    findTopModels = padv.builtin.query.FindTopModels(Name="TopModelsQuery");
    findProjectFile = padv.builtin.query.FindProjectFile();

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Register Tasks
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    modelGenRefTask = pm.addTask("modelGenRefTask", Title="Model Gen Task",Action=@modelGenTask,...
        IterationQuery=findRefModels,...
        InputQueries=padv.builtin.query.GetIterationArtifact);
    modelGenRefTask.OutputDirectory = fullfile(defaultResultPath, "gen");

    reportTsk = pm.addTask("reportTask", Title="Report Task",Action=@reportTask,...
        IterationQuery=findModels,...
        InputQueries=padv.builtin.query.GetIterationArtifact);
    reportTsk.OutputDirectory = fullfile(defaultResultPath, "rep");
end

function taskResult = modelGenTask(input, obj)
    taskResult = padv.TaskResult;
    counter = 1;
     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% GenerateSimulinkWebView
    slwebTask = padv.builtin.task.GenerateSimulinkWebView();
    slwebTask.RuntimeContext = obj.RuntimeContext;
    slwebTask.RuntimeContext.Task = slwebTask;
    slwebTask.ReportPath = fullfile(obj.OutputDirectory,'webview');
    slwebTask.ReportName = '$ITERATIONARTIFACT$_webview';
    for i=1:counter
        results = slwebTask.run(input);
    end
    outputPaths = [results.OutputArtifacts.ArtifactAddress.getFileAddress()];
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CollectMetrics
    % cmTask = padv.builtin.task.CollectMetrics();
    % cmTask.OutputDirectory = fullfile(obj.OutputDirectory, 'metrics');
    % cmTask.RuntimeContext = obj.RuntimeContext;
    % cmTask.RuntimeContext.Task = cmTask;
    % for i=1:counter
    %     results = cmTask.run(input);
    % end
    % outputPaths = results.OutputArtifacts.ArtifactAddress.getFileAddress();
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% DetectDesignErrors
    % dedTask = padv.builtin.task.DetectDesignErrors();
    % dedTask.ReportFilePath = fullfile(obj.OutputDirectory, 'design_error_detections','$ITERATIONARTIFACT$_DED');
    % dedTask.RuntimeContext = obj.RuntimeContext;
    % dedTask.RuntimeContext.Task = dedTask;
    % for i=1:counter
    %     results = codegenTask.run(input);
    % end
    % outputs = arrayfun(@(a) a.ArtifactAddress.getFileAddress(), results.OutputArtifacts);
    % outputPaths = [outputPaths, outputs];
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% GenerateCode
    % codegenTask = padv.builtin.task.GenerateCode();
    % codegenTask.UpdateThisModelReferenceTarget = 'IfOutOfDate';
    % codegenTask.TreatAsRefModel = true;
    % codegenTask.Title = "Reference Model Code Generation";
    % codegenTask.GenerateExternalCodeCache = true;
    % codegenTask.ExternalCodeCacheDirectory = fullfile(obj.OutputDirectory, 'external_code_cache');
    % codegenTask.RuntimeContext = obj.RuntimeContext;
    % codegenTask.RuntimeContext.Task = codegenTask;
    % for i=1:counter
    %     results = codegenTask.run(input);
    % end
    % outputs = arrayfun(@(a) a.ArtifactAddress.getFileAddress(), results.OutputArtifacts);
    % outputPaths = [outputPaths, outputs];
    
    taskResult.OutputPaths = outputPaths;
    taskResult.ResultValues.Pass = results.ResultValues.Pass;
    taskResult.Status = results.Status;
end

function reportTask(input, obj)
    taskResult = padv.TaskResult;
    counter = 1;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% GenerateSimulinkWebView
    slwebTask = padv.builtin.task.GenerateSimulinkWebView();
    slwebTask.RuntimeContext = obj.RuntimeContext;
    slwebTask.RuntimeContext.Task = slwebTask;
    slwebTask.ReportPath = fullfile(obj.OutputDirectory,'webview');
    slwebTask.ReportName = '$ITERATIONARTIFACT$_webview';
    for i=1:counter
        results = slwebTask.run(input);
    end
    outputPaths = [results.OutputArtifacts.ArtifactAddress.getFileAddress()];

    taskResult.OutputPaths = outputPaths;
    taskResult.ResultValues.Pass = results.ResultValues.Pass;
    taskResult.Status = results.Status;
end