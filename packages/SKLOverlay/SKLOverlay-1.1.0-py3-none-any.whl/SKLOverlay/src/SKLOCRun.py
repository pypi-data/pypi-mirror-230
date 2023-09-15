from time import time
from SKLOCMetrics import *
from sklearn.preprocessing import (
    MaxAbsScaler,
    MinMaxScaler,
    Normalizer,
    PowerTransformer,
    QuantileTransformer,
    RobustScaler,
    StandardScaler,
)
from sklearn.decomposition import PCA
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sklearn.model_selection import train_test_split


def Preprocessing(actDataInfo):
    dataset = actDataInfo[1]
    datasetMods = actDataInfo[2]

    rmColList = datasetMods.get('Stripped_columns')
    purgedDataset = dataset.drop(rmColList, axis=1)

    yCol = datasetMods.get('Y_column')
    y = purgedDataset[yCol].values
    X = purgedDataset.drop(yCol, axis=1).values

    preprocessChoice = datasetMods.get('Preprocess')
    if preprocessChoice == 'Max_abs':
        MaxAbsScaler().fit_transform(X)
    elif preprocessChoice == 'Min_max':
        MinMaxScaler().fit_transform(X)
    elif preprocessChoice == 'Normalizer':
        Normalizer().fit_transform(X)
    elif preprocessChoice == 'Power_trans':
        PowerTransformer().fit_transform(X)
    elif preprocessChoice == 'Quant_trans':
        QuantileTransformer().fit_transform(X)
    elif preprocessChoice == 'Robust_sclr':
        RobustScaler().fit_transform(X)
    elif preprocessChoice == 'Std_sclr':
        StandardScaler().fit_transform(X)
    elif preprocessChoice == 'PCA':
        print("PCA")
        compNum = datasetMods.get('Comp_count')
        pca = PCA(n_components=compNum)
        pca.fit(X)
        X = pca.transform(X)
    elif preprocessChoice == 'NCA':
        print("NCA")
        compNum = datasetMods.get('Comp_count')
        nca = NeighborhoodComponentsAnalysis(n_components=compNum)
        nca.fit(X, y)
        X = nca.transform(X)

    ttMethod = datasetMods.get('Train_test_option')
    if ttMethod == "Full_Set":
        X_train = X
        X_test = X
        y_train = y
        y_test = y
    elif ttMethod == "Split_TT":
        decPerc = datasetMods.get('Split_train_perc') / 100
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=decPerc, random_state=42)
    else:
        return None

    return [X_train, X_test, y_train, y_test]


def Fit_Test(dataPartitions, actClassInfo):
    usingData = True
    testingStatus = 'Unavailable'
    resultStatus = 'Unavailable'
    X_train = dataPartitions[0]
    X_test = dataPartitions[1]
    y_train = dataPartitions[2]
    y_test = dataPartitions[3]
    classifierNickname = actClassInfo[0]
    classifier = actClassInfo[1]
    y_guess = None
    elapsed = 0

    while usingData:
        print('-------------------------------------------------------------------')
        print('|        Data ready for use. Please choose an option below.       |')
        print('|                              -----                              |')
        print('|  1. Fitting                                                     ')
        print(f'|  2. Testing ({testingStatus})')
        print(f'|  3. Results ({resultStatus})')
        print('-------------------------------------------------------------------')
        try:
            choice = int(input('|           Enter here or 0 if you changed your mind: '))
            if choice == 0:
                usingData = False
            elif choice == 1:
                testingStatus = 'Available'
                resultStatus = 'Unavailable'

                start = time()
                classifier.fit(X_train, y_train)
                end = time()
                elapsed = round(end - start, 4)
                print('|                       Fitting Complete                          |')

            elif choice == 2:
                if testingStatus == 'Available':
                    resultStatus = 'Available'

                    y_guess = classifier.predict(X_test)
                    print('|                       Testing Complete                          |')
                else:
                    print('|            Testing Unavailable. Please Fit Algorithm            |')

            elif choice == 3:
                if resultStatus == 'Available':
                    Results(y_test, y_guess, classifierNickname, classifier, elapsed)
                else:
                    print('|           Results Unavailable. Please Test Algorithm            |')
            else:
                print('|          Unrecognized option chosen. Please try again.          |')
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')


def Auto_Fit_Test(dataPartitions, nameList, classList, folder):
    allResults = []

    X_train = dataPartitions[0]
    X_test = dataPartitions[1]
    y_train = dataPartitions[2]
    y_test = dataPartitions[3]

    # Clarity casting
    y_train = y_train.astype('int')
    y_test = y_test.astype('int')

    for i in range(len(classList)):
        classifier = classList[i]
        nickname = nameList[i]

        start = time()
        classifier.fit(X_train, y_train)
        end = time()
        elapsed = round(end - start, 6)

        y_guess = classifier.predict(X_test)
        specNickName = f'{nickname}_{i}'

        Save_CM(y_test, y_guess, specNickName, classifier, folder)

        resultList = Results_Return(y_test, y_guess, specNickName, classifier, elapsed)
        allResults.append(resultList)

    setName = nameList[1] + "_SET"
    Send_To_Excel(allResults, setName, folder)
    Generate_All_Charts(allResults, setName, folder)


def Algorithm_Testing(actClassInfo, actDataInfo):
    print(actClassInfo)
    print(actDataInfo)

    dataPartitions = Preprocessing(actDataInfo)  # [X_train, X_test, y_train, y_test]

    if dataPartitions:
        Fit_Test(dataPartitions, actClassInfo)
    else:
        print('|    Req Check failed. Please edit active items and try again.    |')
        print('-------------------------------------------------------------------')


def Auto_Alg_Testing(nameList, classList, actDataInfo, folder):
    dataPartitions = Preprocessing(actDataInfo)  # [X_train, X_test, y_train, y_test]

    if dataPartitions:
        Auto_Fit_Test(dataPartitions, nameList, classList, folder)
    else:
        print('|    Req Check failed. Please edit active items and try again.    |')
        print('-------------------------------------------------------------------')
