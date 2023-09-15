from os.path import isdir
from textwrap import wrap
from SKLOCDatasets import Dataset_Setup_Local, Dataset_Setup_Sample
from SKLOCDataMods import Dataset_Config
from SKLOCRun import Auto_Alg_Testing
from SKLOCCustom.SKLOCCMain import Customize_Classifier, Customize_Classifier_Batch


def List_Classifiers(sessionClassifiers):
    if sessionClassifiers:
        # Autogenerate
        lengthFormat = len('-------------------------------------------------------------------')  # 67 hyphens
        formatSpace = 7
        for i in range(len(sessionClassifiers)):
            nickname = sessionClassifiers[i][0]
            mods = sessionClassifiers[i][2]
            leftoverSpace = lengthFormat - formatSpace - len(nickname)
            # First bit of format
            print('| ', end='')
            if i < 10:
                print(' ', end='')
            print(f'{i + 1}. {nickname}', end='')

            # Leftover half of format
            for j in range(leftoverSpace):
                print(' ', end='')
            print('|')

            # mod text wrapping - 64 per line
            maxModLength = 60
            modWrapped = wrap(str(mods), maxModLength)
            for line in modWrapped:
                print("|      " + line)

        print('-------------------------------------------------------------------')
        return True
    else:
        print('-------------------------------------------------------------------')
        print('| No Classifiers created at this time. Please Create one for use. |')
        print('-------------------------------------------------------------------')
        return False


def List_Datasets(sessionDatasets):
    if sessionDatasets:
        # Autogenerate
        lengthFormat = len('-------------------------------------------------------------------')  # 67 hyphens
        formatSpace = 7
        for i in range(len(sessionDatasets)):
            nickname = sessionDatasets[i][0]
            mods = sessionDatasets[i][2]
            leftoverSpace = lengthFormat - formatSpace - len(nickname)
            # First bit of format
            print('| ', end='')
            if i < 10:
                print(' ', end='')
            print(f'{i + 1}. {nickname}', end='')

            # Leftover half of format
            for j in range(leftoverSpace):
                print(' ', end='')
            print('|')

            # mod text wrapping - 64 per line
            maxModLength = 60
            modWrapped = wrap(str(mods), maxModLength)
            for line in modWrapped:
                print("|      " + line)

        print('-------------------------------------------------------------------')
        return True
    else:
        print('-------------------------------------------------------------------')
        print('|   No Datasets created at this time. Please Create one for use.  |')
        print('-------------------------------------------------------------------')
        return False


def Edit_Classifiers(sessionClassifiers):
    print('|             Select the algorithm you wish to edit!              |')
    print('|                              -----                              |')
    classifiersExist = List_Classifiers(sessionClassifiers)

    if classifiersExist:
        choiceNum = int(input('|           Enter here or 0 if you changed your mind: '))
    else:
        choiceNum = 0

    if choiceNum != 0:
        classifierIndex = choiceNum - 1
        print(sessionClassifiers[classifierIndex])

        classifierNickname = sessionClassifiers[classifierIndex][0]
        classifierType = sessionClassifiers[classifierIndex][3]

        nickname, classifier = Customize_Classifier(classifierType, classifierNickname)

        sessionClassifiers[classifierIndex][1] = classifier[0]
        sessionClassifiers[classifierIndex][2] = classifier[1]


def Make_New_Classifier():
    # Rest of turn
    print('|                     Choose your algorithm!                      |')
    print('|                              -----                              |')
    print('|  1. Random Forest                                               |')
    print('|  2. K-Neighbors                                                 |')
    print('|  3. Support Vector Machine                                      |')
    print('|  4. Linear Support Vector Machine                               |')
    print('|  5. Multi-layer Perceptron                                      |')
    print('-------------------------------------------------------------------')

    # Selection & Customization
    classifierNum = int(input('|                Enter here or 0 if you are done: '))
    nickname, classifier = Customize_Classifier(classifierNum)

    print('-------------------------------------------------------------------')
    return nickname, classifier[0], classifier[1], classifierNum


def Make_New_Dataset():
    print('-------------------------------------------------------------------')
    print('|          Choose your dataset! Where is it coming from?          |')
    print('|                              -----                              |')
    print('|  1. Sample                                                      |')
    print('|  2. Local Machine                                               |')
    print('-------------------------------------------------------------------')
    choice = int(input('|           Enter here or 0 if you changed your mind: '))
    if choice == 0:
        return 0
    elif choice == 1:
        nickname = input('| Nickname your sample dataset: ')
        datasetInfo = Dataset_Setup_Sample(nickname)

        if datasetInfo != 0:
            newDataset = datasetInfo[0]
            newDMods = datasetInfo[1]
            return [nickname, newDataset, newDMods]
        else:
            return 0
    elif choice == 2:
        print('|        Copy in the filepath or link of your dataset file.       |')
        filePath = input('| Enter in the filepath or link here: ')
        nickname = input('| Nickname your local dataset: ')
        datasetInfo = Dataset_Setup_Local(nickname, filePath)
        print(datasetInfo)

        if datasetInfo != 0:
            newDataset = datasetInfo[0]
            newDMods = datasetInfo[1]
            return [nickname, newDataset, newDMods]
        else:
            return 0
    else:
        print('|          Unrecognized option chosen. Please try again.          |')
        print('-------------------------------------------------------------------')
        return 0


def DMods_Check(newDMods):
    YColumn = newDMods['Y_column']
    TTOption = newDMods['Train_test_option']

    if YColumn is None or TTOption is None:
        return False
    else:
        print('|                           Success!                              |')
        print('-------------------------------------------------------------------')
        return True


def Edit_Dataset(sessionDatasets):
    print('|             Select the algorithm you wish to edit!              |')
    print('|                              -----                              |')
    dataSetsExist = List_Datasets(sessionDatasets)

    if dataSetsExist:
        choiceNum = int(input('|           Enter here or 0 if you changed your mind: '))
    else:
        choiceNum = 0

    if choiceNum != 0:
        classifierIndex = choiceNum - 1
        print(sessionDatasets[classifierIndex])

        datasetNickname = sessionDatasets[classifierIndex][0]
        dataset = sessionDatasets[classifierIndex][1]
        datasetMods = sessionDatasets[classifierIndex][2]

        datasetInfo = Dataset_Config(datasetNickname, dataset, datasetMods)
        newDMods = datasetInfo[1]

        sessionDatasets[classifierIndex][2] = newDMods


def Batch_Testing(activeClassifier, activeDataset, sessionClassifiers, sessionDatasets):
    actDataInfo = sessionDatasets[activeDataset]

    # Create folder
    print('|     Type or copy in your absolute filepath here for results.    |')
    print('|    Make sure the folder existed before running this program.    |')
    print('|     Include the slash at the end to specify it is a folder.     |')
    folder = input('| Enter here: ')

    # Being kind to the user
    if folder.startswith('"'):
        folder = folder[1:]

    if folder.endswith('"'):
        folder = folder[:-1]

    if folder[-1] != "\\":
        folder = folder + "\\"

    # Booleans
    folderExists = isdir(folder)
    if not folderExists:
        folder = 'Default'

    #list of classifiers
    print('|                          Do you wish to:                        |')
    print('|                              -----                              |')
    print('|  1. Batch test different algorithms                             |')
    print('|  2. Batch test one algorithm multiple times                     |')
    try:
        choice = int(input('|           Enter here or 0 if you changed your mind: '))
        if choice == 1 and len(sessionClassifiers) > 1:
            List_Classifiers(sessionClassifiers)
            classList = []
            nameList = []
            choosingClass = True

            while choosingClass:
                classChoice = int(input('|           Enter here an classifier # or zero to finish: '))
                if classChoice == 0:
                    choosingClass = False
                else:
                    classIndex = classChoice - 1
                    classifier = sessionClassifiers[classIndex][1]
                    nickname = sessionClassifiers[classIndex][0]
                    print(f'| Adding {nickname}...')

                    classList.append(classifier)
                    nameList.append(nickname)
        elif choice == 2:
            actClassInfo = sessionClassifiers[activeClassifier]

            print('| Decide whether an algorithm should be ran repeatedly or have a  |')
            print('| changing factor.                                                |')
            batchChange = int(input('| Should there be a shifting parameter (1 for yes, 0 for no): '))
            batchNum = int(input('| How many runs should there be: '))
            if batchChange == 1:
                classList = Customize_Classifier_Batch(actClassInfo, batchNum)
            elif batchChange == 0:
                classifier = actClassInfo[1]
                classList = [classifier] * batchNum
            else:
                print('|     Unrecognized option chosen. Using default configuration.    |')
                classifier = actClassInfo[1]
                classList = [classifier] * batchNum

            nickname = actClassInfo[0]
            nameList = [nickname] * batchNum
        else:
            print('|    Unrecognized option or insufficient amount of classifiers.   |')
            print('|                        Please try again                         |')
            print('-------------------------------------------------------------------')
            classList = 0
            nameList = 0

        if classList != 0:
            print(f'| Your file will be placed in "{folder}"')
            print('| Your file will be named after the first/active classifier used. |')
            print('-------------------------------------------------------------------')
            Auto_Alg_Testing(nameList, classList, actDataInfo, folder)
    except ValueError:
        print('-------------------------------------------------------------------')
        print('|                          ERROR CAUGHT                           |')
        print('| Tip: Unless specifically asked, you will only have to use       |')
        print('|      numbers to move around and make selections. Until further  |')
        print('|      improvements, this error will result in loss of progress   |')
        print('|      or even shutdown of the program. I apologize for any       |')
        print('|      inconvenience.                                             |')
        print('-------------------------------------------------------------------')
