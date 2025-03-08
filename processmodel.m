function processmodel(pm)
    % Defines the project's processmodel

    arguments
        pm padv.ProcessModel
    end

    pm.DefaultOutputDirectory = fullfile('$PROJECTROOT$', 'PA_Results');    
    findModels = padv.builtin.query.FindModels(Name="ModelsQuery");
    task1Obj=pm.addTask("Task1",...
        'IterationQuery', findModels,...
        'InputQueries', padv.builtin.query.GetIterationArtifact,...
        'Action',@Task1);
    task1Obj.OutputDirectory=string(fullfile('$DEFAULTOUTPUTDIR$', '$ITERATIONARTIFACT$'));
end

function taskResult = Task1(inputs)
    taskName = 'Task1';
    disp(['@@@ Running'  taskName ' @@@']); %#ok<testStandardsViolation.disp>
    cp = currentProject;

    [~,name,~] = fileparts(inputs{1}.Alias);
    outfileName = name + ".txt";
    outdirectory = fullfile("PA_Results", name, taskName);
    if ~exist(fullfile(cp.RootFolder,outdirectory),'dir')
        mkdir(fullfile(cp.RootFolder,outdirectory))
    end

    fid = fopen(fullfile(cp.RootFolder,outdirectory, outfileName),'a+');
    fclose(fid);

    taskResult = padv.TaskResult;
    taskResult.OutputPaths = fullfile(cp.RootFolder,outdirectory, outfileName);
end