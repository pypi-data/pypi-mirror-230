from copy import deepcopy


def Remove_Column(workingCopy, dataMods):
    print('|                Please Select a column to remove:                |')
    print('|                              -----                              |')

    # Autogen
    lengthFormat = len('-------------------------------------------------------------------')  # 67 hyphens
    formatSpace = 7
    listNum = 1
    for col in workingCopy.columns:
        if col not in dataMods['Stripped_columns']:
            leftoverSpace = lengthFormat - formatSpace - len(col)
            # First bit of format
            print('| ', end='')
            if listNum < 10:
                print(' ', end='')
            print(f'{listNum}. {col}', end='')

            # Leftover half of format
            for j in range(leftoverSpace):
                print(' ', end='')
            print('|')

            listNum += 1
    print('-------------------------------------------------------------------')

    rmColChoice = input('|                  Enter the name, not number: ')
    if rmColChoice in workingCopy.columns:
        dataMods['Stripped_columns'].append(rmColChoice)
        print('|                           Success!                              |')
        print('-------------------------------------------------------------------')
    else:
        print('|          Unrecognized option chosen. Please try again.          |')
        print('-------------------------------------------------------------------')


def Select_YColumn(workingCopy, dataMods):
    columns = workingCopy.columns
    columns = list(columns.values)

    print('|            Please Select a column to be the classes:            |')
    print('|                              -----                              |')

    # Autogen
    lengthFormat = len('-------------------------------------------------------------------')  # 67 hyphens
    formatSpace = 7
    listNum = 1
    for col in columns:
        leftoverSpace = lengthFormat - formatSpace - len(col)
        # First bit of format
        print('| ', end='')
        if listNum < 10:
            print(' ', end='')
        print(f'{listNum}. {col}', end='')

        # Leftover half of format
        for j in range(leftoverSpace):
            print(' ', end='')
        print('|')

        listNum += 1
    print('-------------------------------------------------------------------')

    yColChoice = int(input('|                       Enter the number: '))
    yCol = yColChoice - 1
    if 0 < yCol < len(columns):
        dataMods['Y_column'] = columns[yCol]
        print('|                           Success!                              |')
        print('-------------------------------------------------------------------')
    else:
        print('|          Unrecognized option chosen. Please try again.          |')
        print('-------------------------------------------------------------------')


def Select_Train_Test(dataMods):
    print('|             Please select the train testing method:             |')
    print('|                              -----                              |')
    print('|  1. Full set for both training and testing                      |')
    print('|  2. Split into testing and training set                         |')
    choice = int(input('|                      Enter number here: '))

    if choice == 1:
        dataMods['Train_test_option'] = "Full_Set"
    elif choice == 2:
        dataMods['Train_test_option'] = "Split_TT"
        print('|       What percentage of the set will be used for training?     |')
        choice = int(input('|                   Enter number here (0-100): '))
        dataMods['Split_train_perc'] = choice
    else:
        print('|          Unrecognized option chosen. Please try again.          |')

    print('-------------------------------------------------------------------')


def Select_Preprocess(dataMods):
    print('|               Please select the preprocess method:              |')
    print('|                              -----                              |')
    print('|  1. Max Absolute Scaler                                         |')
    print('|  2. Min-Max Scaler                                              |')
    print('|  3. Normalizer                                                  |')
    print('|  4. Power Transformer                                           |')
    print('|  5. Quantile Transformer                                        |')
    print('|  6. Robust Scaler                                               |')
    print('|  7. Standard Scaler                                             |')
    print('|  8. Principal Component Analysis (PCA)                          |')
    print('|  9. Neighborhood Components Analysis (NCA)                      |')
    choice = int(input('|                      Enter number here: '))

    if choice == 1:
        dataMods['Preprocess'] = 'Max_abs'
    elif choice == 2:
        dataMods['Preprocess'] = 'Min_max'
    elif choice == 3:
        dataMods['Preprocess'] = 'Normalizer'
    elif choice == 4:
        dataMods['Preprocess'] = 'Power_trans'
    elif choice == 5:
        dataMods['Preprocess'] = 'Quant_trans'
    elif choice == 6:
        dataMods['Preprocess'] = 'Robust_sclr'
    elif choice == 7:
        dataMods['Preprocess'] = 'Std_sclr'
    elif choice == 8:
        dataMods['Preprocess'] = 'PCA'
        choice = int(input('|              Enter number of components here: '))
        dataMods['Comp_count'] = choice
    elif choice == 9:
        dataMods['Preprocess'] = 'NCA'
        choice = int(input('|              Enter number of components here: '))
        dataMods['Comp_count'] = choice
    else:
        print('|          Unrecognized option chosen. Please try again.          |')

    print('-------------------------------------------------------------------')


def Dataset_Config(nickname, dataset, dataMods=None):
    YSelected = False
    TTSelected = False

    if dataMods is None:
        dataMods = {}

    # Default configuration
    if dataMods == {}:
        dataMods = {
            'Stripped_columns': [],
            'Y_column': None,
            'Train_test_option': None,
            'Split_train_perc': None,
            'Preprocess': None,
            'Comp_count': None
        }

    if dataMods['Y_column'] is not None:
        YSelected = True
    if dataMods['Train_test_option'] is not None:
        TTSelected = True

    workingCopy = deepcopy(dataset)

    makingEdits = True

    while makingEdits:
        print(f'| Dataset: {nickname}')
        print(f'| Removed Columns: {dataMods["Stripped_columns"]}')
        print(f'| Classifier Column: {dataMods["Y_column"]}')
        print(f'| Train-Test Method: {dataMods["Train_test_option"]} ({dataMods["Split_train_perc"]})')
        print(f'| Preprocessing Method: {dataMods["Preprocess"]} ({dataMods["Comp_count"]})')
        print('|                                                                 |')
        print('|                   Choose what you want to do!                   |')
        print('|           All leftover columns (aside from the set Y)           |')
        print('|             will be automatically used as X columns             |')
        print('|        In addition, a Y column and TT Method is required.       |')
        print('|                              -----                              |')
        print('|  0. Exit                                                        |')
        print('|  1. Reset Edits                                                 |')
        print('|  2. Remove Columns                                              |')
        print('|  3. Assign Y (Resulting Class Column)                           |')
        print('|  4. Train-Test Method                                           |')
        print('|  5. Preprocessing                                               |')
        print('-------------------------------------------------------------------')
        try:
            choice = int(input('|                          Enter here: '))
            if choice == 0:
                if YSelected and TTSelected:
                    makingEdits = False
                else:
                    print('|             Ensure necessary modifications are done.            |')
                    print('-------------------------------------------------------------------')
            elif choice == 1:
                workingCopy = deepcopy(dataset)
                dataMods = {
                    'Stripped_columns': [],
                    'Y_column': None,
                    'Train_test_option': None,
                    'Split_train_perc': None,
                    'Preprocess': None,
                    'Comp_count': None
                }
                print('|                   Dataset Modifications Reset                   |')
                print('-------------------------------------------------------------------')
            elif choice == 2:
                Remove_Column(workingCopy, dataMods)
            elif choice == 3:
                Select_YColumn(workingCopy, dataMods)
                if dataMods['Y_column'] is not None:
                    YSelected = True
            elif choice == 4:
                Select_Train_Test(dataMods)
                if dataMods['Train_test_option'] is not None:
                    TTSelected = True
            elif choice == 5:
                Select_Preprocess(dataMods)
            else:
                print('|                Do not recognize input. Try again.               |')
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

    datasetPrep = [dataset, deepcopy(dataMods)]
    return datasetPrep
