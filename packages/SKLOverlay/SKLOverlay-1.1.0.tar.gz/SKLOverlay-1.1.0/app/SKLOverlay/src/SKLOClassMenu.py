from SKLOCMainOps import *
from SKLOCRun import Algorithm_Testing


def Classification_Menu():
    sessionActive = True
    sessionClassifiers = []
    sessionDatasets = []
    activeClassifier = None
    activeDataset = None

    while sessionActive:
        if activeClassifier is None:
            print(f'| Active Classifier: {activeClassifier}')
        else:
            print(f'| Active Classifier: {sessionClassifiers[activeClassifier][0]} ({activeClassifier + 1})')

        if activeDataset is None:
            print(f'| Active Dataset: {activeDataset}')
        else:
            print(f'| Active Dataset: {sessionDatasets[activeDataset][0]} ({activeDataset + 1})')

        print('|                   Choose what you want to do!                   |')
        print('|  When you are done configuring, select nine or ten to move on   |')
        print('|                              -----                              |')
        print('|  0. Exit                                                        |')
        print('|  1. Edit Current Algorithms                                     |')
        print('|  2. Create New Algorithm                                        |')
        print('|  3. Select Active Algorithm                                     |')
        print('|  4. Remove Algorithm                                            |')
        print('|  5. Edit Current Datasets                                       |')
        print('|  6. Create New Dataset                                          |')
        print('|  7. Select Active Dataset                                       |')
        print('|  8. Remove Dataset                                              |')
        print('|  9. Algorithm Fitting and Testing                               |')
        print('| 10. Automated Batch Testing                                     |')
        print('-------------------------------------------------------------------')
        try:
            choice = int(input('|                          Enter here: '))
            if choice == 0:
                sessionActive = False
            elif choice == 1:
                Edit_Classifiers(sessionClassifiers)
            elif choice == 2:
                nickname, newClassifier, newMods, classifierNum = Make_New_Classifier()
                sessionClassifiers.append([nickname, newClassifier, newMods, classifierNum])
                # [nickname, newClassifier, newMods, classifierNum]
            elif choice == 3:
                print('-------------------------------------------------------------------')
                print('|    Please enter the number of the classifier you wish to use:   |')
                print('|                              -----                              |')
                classifiersExist = List_Classifiers(sessionClassifiers)
                if classifiersExist:
                    choiceNum = int(input('|           Enter here or 0 if you changed your mind: '))
                    if 0 < choiceNum <= len(sessionClassifiers):
                        activeClassifier = choiceNum - 1
                        print(f'| Active Classifier: {sessionClassifiers[activeClassifier][0]}')
                        print('-------------------------------------------------------------------')
                    else:
                        print('|          Unrecognized option chosen. Please try again.          |')
                        print('-------------------------------------------------------------------')
            elif choice == 4:
                print('-------------------------------------------------------------------')
                print('|  Please enter the number of the classifier you wish to delete:  |')
                print('|                              -----                              |')
                classifiersExist = List_Classifiers(sessionClassifiers)
                if classifiersExist:
                    choiceNum = int(input('|           Enter here or 0 if you changed your mind: '))
                    if 0 < choiceNum <= len(sessionClassifiers):
                        indexToDel = choiceNum - 1
                        print(f'| Deleting {sessionClassifiers[indexToDel][0]}...')
                        sessionClassifiers.pop(indexToDel)

                        print('|                              Done                               |')
                        if activeClassifier == indexToDel:
                            print('|             Please choose a new active classifier.              |')
                            activeClassifier = None
                        print('-------------------------------------------------------------------')
                    else:
                        print('|          Unrecognized option chosen. Please try again.          |')
                        print('-------------------------------------------------------------------')
            elif choice == 5:
                Edit_Dataset(sessionDatasets)
            elif choice == 6:
                newDataset = Make_New_Dataset()  # [nickname, newDataset, newDMods]
                if newDataset != 0:
                    newDMods = newDataset[2]
                    if DMods_Check(newDMods):
                        sessionDatasets.append(newDataset)
            elif choice == 7:
                print('-------------------------------------------------------------------')
                print('| Please enter the number of the dataset config you wish to use:  |')
                print('|                              -----                              |')
                datasetExists = List_Datasets(sessionDatasets)
                if datasetExists:
                    choiceNum = int(input('|           Enter here or 0 if you changed your mind: '))
                    if 0 < choiceNum <= len(sessionDatasets):
                        activeDataset = choiceNum - 1
                        print(f'| Active Dataset: {sessionDatasets[activeDataset][0]}')
                        print('-------------------------------------------------------------------')
                    else:
                        print('|          Unrecognized option chosen. Please try again.          |')
                        print('-------------------------------------------------------------------')
            elif choice == 8:
                print('-------------------------------------------------------------------')
                print('|  Please enter the number of the dataset you wish to delete:  |')
                print('|                              -----                              |')
                datasetExists = List_Datasets(sessionDatasets)
                if datasetExists:
                    choiceNum = int(input('|           Enter here or 0 if you changed your mind: '))
                    if 0 < choiceNum <= len(sessionDatasets):
                        indexToDel = choiceNum - 1
                        print(f'| Deleting {sessionDatasets[indexToDel][0]}...')
                        sessionDatasets.pop(indexToDel)

                        print('|                              Done                               |')
                        if activeDataset == indexToDel:
                            print('|             Please choose a new active classifier.              |')
                            activeDataset = None
                        print('-------------------------------------------------------------------')
                    else:
                        print('|          Unrecognized option chosen. Please try again.          |')
                        print('-------------------------------------------------------------------')
            elif choice == 9:
                if activeClassifier is not None and activeDataset is not None:
                    actClassInfo = sessionClassifiers[activeClassifier]
                    actDataInfo = sessionDatasets[activeDataset]
                    Algorithm_Testing(actClassInfo, actDataInfo)
            elif choice == 10:
                if activeClassifier is not None and activeDataset is not None:
                    Batch_Testing(activeClassifier, activeDataset, sessionClassifiers, sessionDatasets)
            else:
                print('|          Unrecognized option chosen. Please try again.          |')
                print('-------------------------------------------------------------------')
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')
