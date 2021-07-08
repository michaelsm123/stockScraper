clear, clc

%Import Results and put data in variables
[nums,text,all] = xlsread('masterResultsFile.xlsx');
openResult = text(:,8);
openResult = char(openResult);
openChange = nums(:,7)*100;
closeResult = all(:,11);
closeResult = char(closeResult);
closeChange = nums(:,10)*100;

openResultFilter = [];
openChangeFilter = [];
closeResultFilter = [];
closeChangeFilter = [];
openCorrect = 0;
openIncorrect = 0;
openOverallPercent = 0;
closeCorrect = 0;
closeIncorrect = 0;
closeOverallPercent = 0;


%Filter out all n/a results from table
for i = 2:size(openResult)
    if isempty(find(openResult(i,:)=='a')) && isempty(find(closeResult(i,:)=='a'))
        
        %gets open result
        emptyInds = find(openResult(i,:)==' ');
        firstEmptyInd = emptyInds(1);
        openResultNoWhitespace = openResult(i,1:firstEmptyInd-1);
        openResultFilter = [openResultFilter openResultNoWhitespace];
        
        %counts correct and incorrect at open
        if strcmp(openResultNoWhitespace,'Correct')
            openCorrect = openCorrect + 1;
        else
            openIncorrect = openIncorrect + 1;
        end
        
        %gets open percent change
        openChangeFilter = [openChangeFilter openChange(i,1)];
        openOverallPercent = openOverallPercent + openChange(i,1);
        
        %gets close result
        emptyInds = find(closeResult(i,:)==' ');
        firstEmptyInd = emptyInds(1);
        closeResultNoWhitespace = closeResult(i,1:firstEmptyInd-1);
        closeResultFilter = [closeResultFilter closeResultNoWhitespace]; 
        
        %counts correct and incorrect at close
        if strcmp(closeResultNoWhitespace,'Correct')
            closeCorrect = closeCorrect + 1;
        else
            closeIncorrect = closeIncorrect + 1;
        end
        
        %gets close percent change
        closeChangeFilter = [closeChangeFilter closeChange(i,1)];
        closeOverallPercent = closeOverallPercent + closeChange(i,1);
    end
end

openCorrectPercent  = openCorrect / (openCorrect + openIncorrect) * 100
openOverallPercent

closeCorrectPercent = closeCorrect / (closeCorrect + closeIncorrect) * 100
closeOverallPercent