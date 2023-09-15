from sklearn.ensemble import RandomForestClassifier
from copy import deepcopy
from ast import literal_eval


def Customization_RF(mods=None):
    if mods is None:
        mods = {}
    rf = RandomForestClassifier()

    # Selection Loop
    selectingParams = True
    while selectingParams:
        print('-------------------------------------------------------------------')
        print('|                  PLEASE CUSTOMIZE RANDOM FOREST                 |')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. n_estimators                                                |')
        print('|  2. criterion                                                   |')
        print('|  3. max_depth                                                   |')
        print('|  4. min_samples_split                                           |')
        print('|  5. min_samples_leaf                                            |')
        print('|  6. min_weight_fraction_leaf                                    |')
        print('|  7. max_features                                                |')
        print('|  8. max_leaf_nodes                                              |')
        print('|  9. min_impurity_decrease                                       |')
        print('| 10. bootstrap                                                   |')
        print('| 11. oob_score                                                   |')
        print('| 12. n_jobs                                                      |')
        print('| 13. random_state                                                |')
        print('| 14. verbose                                                     |')
        print('| 15. warm_start                                                  |')
        print('| 16. class_weight                                                |')
        print('| 17. ccp_alpha                                                   |')
        print('| 18. max_samples                                                 |')
        print('-------------------------------------------------------------------')
        print('| Choose number here or enter 0 if you have no more modifications |')
        try:
            parameter = int(input("| Enter here: "))

            # Decision Tree
            if parameter == 0:
                selectingParams = False
            elif parameter == 1:
                print('-------------------------------------------------------------------')
                print('|                  You selected "n_estimators"                    |')
                n_estimators_input = int(input("| Select the number of trees in the forest: "))
                mods.update(n_estimators=n_estimators_input)
                rf.set_params(** {'n_estimators': n_estimators_input})
            elif parameter == 2:
                print('-------------------------------------------------------------------')
                print('|                    You selected "criterion"                     |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. gini (Default)                                              |')
                print('|  2. entropy                                                     |')
                print('|  3. log_loss                                                    |')
                criterion_input = int(input('|           Enter here or 0 if you changed your mind: '))
                if criterion_input == 1:
                    mods.update(criterion="gini")
                    rf.set_params(**{'criterion': "gini"})
                elif criterion_input == 2:
                    mods.update(criterion="entropy")
                    rf.set_params(**{'criterion': "entropy"})
                elif criterion_input == 3:
                    mods.update(criterion="log_loss")
                    rf.set_params(**{'criterion': "log_loss"})
            elif parameter == 3:
                print('-------------------------------------------------------------------')
                print('|                    You selected "max_depth"                     |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. None (Default)                                              |')
                print('|  2. Custom                                                      |')
                max_depth_input = int(input("| Select the max tree depth option: "))
                if max_depth_input == 1:
                    mods.update(max_depth=None)
                    rf.set_params(**{'max_depth': None})
                elif max_depth_input == 2:
                    max_depth_num = int(input("| Enter the number for max tree depth: "))
                    mods.update(max_depth=max_depth_num)
                    rf.set_params(**{'max_depth': max_depth_num})
            elif parameter == 4:
                print('-------------------------------------------------------------------')
                print('|                You selected "min_samples_split"                 |')
                min_samples_split_input = int(input("| Select the minimum number for sample splitting: "))
                mods.update(min_samples_split=min_samples_split_input)
                rf.set_params(**{'min_samples_split': min_samples_split_input})
            elif parameter == 5:
                print('-------------------------------------------------------------------')
                print('|                You selected "min_samples_leaf"                  |')
                min_samples_leaf_input = int(input("| Select the minimum number for leaves: "))
                mods.update(min_samples_leaf=min_samples_leaf_input)
                rf.set_params(**{'min_samples_leaf': min_samples_leaf_input})
            elif parameter == 6:
                print('-------------------------------------------------------------------')
                print('|             You selected "min_weight_fraction_leaf"             |')
                mwfl_input = float(input("| Select the minimum leaf weight: "))
                mods.update(min_weight_fraction_leaf=mwfl_input)
                rf.set_params(**{'min_weight_fraction_leaf': mwfl_input})
            elif parameter == 7:
                print('-------------------------------------------------------------------')
                print('|                   You selected "max_features"                   |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. sqrt (Default)                                              |')
                print('|  2. log2                                                        |')
                print('|  3. Custom                                                      |')
                max_features_choice = int(input('|           Enter here or 0 if you changed your mind: '))
                if max_features_choice == 1:
                    mods.update(max_features="sqrt")
                    rf.set_params(**{'max_features': "sqrt"})
                elif max_features_choice == 2:
                    mods.update(max_features="log2")
                    rf.set_params(**{'max_features': "log2"})
                elif max_features_choice == 3:
                    max_features_input = int(input("| Select the max features to consider per split: "))
                    mods.update(max_features=max_features_input)
                    rf.set_params(**{'max_features': max_features_input})
            elif parameter == 8:
                print('-------------------------------------------------------------------')
                print('|                  You selected "max_leaf_nodes"                  |')
                max_leaf_nodes_input = int(input("| Select the maximum leaf node count: "))
                mods.update(max_leaf_nodes=max_leaf_nodes_input)
                rf.set_params(**{'max_leaf_nodes': max_leaf_nodes_input})
            elif parameter == 9:
                print('-------------------------------------------------------------------')
                print('|               You selected "min_impurity_decrease"              |')
                mid_input = float(input("| Select the impurity split threshold: "))
                mods.update(min_impurity_decrease=mid_input)
                rf.set_params(**{'min_impurity_decrease': mid_input})
            elif parameter == 10:
                print('-------------------------------------------------------------------')
                print('|                     You selected "bootstrap"                    |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. True                                                        |')
                print('|  2. False                                                       |')
                bootstrap_input = int(input('| Select whether to use bootstrappign: '))
                if bootstrap_input == 1:
                    mods.update(bootstrap=True)
                    rf.set_params(**{'bootstrap': True})
                elif bootstrap_input == 2:
                    mods.update(bootstrap=False)
                    rf.set_params(**{'bootstrap': False})
            elif parameter == 11:
                print('-------------------------------------------------------------------')
                print('|                     You selected "oob_score"                    |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. True                                                        |')
                print('|  2. False                                                       |')
                oob_score_input = int(input('| Select whether to use out-of-bag sample estimating: '))
                if oob_score_input == 1:
                    mods.update(oob_score=True)
                    rf.set_params(**{'oob_score': True})
                elif oob_score_input == 2:
                    mods.update(oob_score=False)
                    rf.set_params(**{'oob_score': False})
            elif parameter == 12:
                print('-------------------------------------------------------------------')
                print('|                       You selected "n_jobs"                     |')
                n_jobs_input = int(input("| How many parallel processes are you using: "))
                mods.update(n_jobs=n_jobs_input)
                rf.set_params(**{'n_jobs': n_jobs_input})
            elif parameter == 13:
                print('-------------------------------------------------------------------')
                print('|                    You selected "random_state"                  |')
                random_state_input = int(input("| Enter in a digit for the randomizer: "))
                mods.update(random_state=random_state_input)
                rf.set_params(**{'random_state': random_state_input})
            elif parameter == 14:
                print('-------------------------------------------------------------------')
                print('|                       You selected "verbose"                    |')
                verbose_input = int(input("| Enter in a digit that represents your desired detail level: "))
                mods.update(verbose=verbose_input)
                rf.set_params(**{'verbose': verbose_input})
            elif parameter == 15:
                print('-------------------------------------------------------------------')
                print('|                     You selected "warm_start"                   |')
                print('| This can be used if you wish to refit and further train single  |')
                print('| programs using option 9.                                        |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. True                                                        |')
                print('|  2. False                                                       |')
                warm_start_input = int(input('|           Enter here or 0 if you changed your mind: '))
                if warm_start_input == 1:
                    mods.update(warm_start=True)
                    rf.set_params(**{'warm_start': True})
                elif warm_start_input == 2:
                    mods.update(warm_start=False)
                    rf.set_params(**{'warm_start': False})
            elif parameter == 16:
                print('-------------------------------------------------------------------')
                print('|                    You selected "class_weight"                  |')
                print('|     If you know your dataset\'s classes, feel free to use #2     |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  0. None                                                        |')
                print('|  1. Balanced                                                    |')
                print('|  2. Enter a list of weights for classes                         |')
                class_weight_choice = int(input('| Select the class weight option: '))
                if class_weight_choice == 1:
                    mods.update(class_weight="balanced")
                    rf.set_params(**{'class_weight': "balanced"})
                elif class_weight_choice == 2:
                    class_weight_input = input("| Enter in the class weights in dictionary or list of dicts format: ")
                    class_weight_input = literal_eval(class_weight_input)
                    mods.update(class_weight=class_weight_input)
                    rf.set_params(**{'class_weight': class_weight_input})
            elif parameter == 17:
                print('-------------------------------------------------------------------')
                print('|                     You selected "ccp_alpha"                    |')
                ccp_alpha_input = abs(float(input("| Enter in your cost complexity threshold: ")))
                mods.update(ccp_alpha=ccp_alpha_input)
                rf.set_params(**{'ccp_alpha': ccp_alpha_input})
            elif parameter == 18:
                print('-------------------------------------------------------------------')
                print('|                    You selected "max_samples"                   |')
                max_samples_input = int(input("| Enter in your max sample number: "))
                mods.update(max_samples=max_samples_input)
                rf.set_params(**{'max_samples': max_samples_input})
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')

    # Restore all old mods along with new mods
    for parameter, setting in mods.items():
        rf.set_params(**{parameter: setting})

    newMods = deepcopy(mods)
    return rf, newMods


def Set_Shiftlist(parameter, batchNum):
    shiftList = []
    print(f'|                  You selected {parameter}                    |')
    parameter_start = float(input("| What is the starting number: "))

    print('|  What interval would you like to use for adding/removing units? |')
    intervalChange = float(input("| Input a positive number for increase and a negative number for  |\n| decrease: "))
    parameter_end = parameter_start + (intervalChange * (batchNum - 1))

    print(f'| The number of units will start at {parameter_start} for the first classifier.')
    print(f'| This number will change by {intervalChange} units, {batchNum} times for each classifier.')
    print(f'| A total of {abs(intervalChange * (batchNum - 1))} units will be added or removed.')
    print(f'| The number will end at {parameter_end} for the last classifier. Is this okay?')

    choice = int(input('Choose 1 to confirm: '))
    if choice == 1:
        for i in range(batchNum):
            shiftList.append(parameter_start)
            parameter_start = round(parameter_start + intervalChange, 8)
        settingParam = False
    else:
        print('|             Confirmation unsuccessful. Trying again.            |')
        print('-------------------------------------------------------------------')
        settingParam = True

    print(shiftList)

    return shiftList, settingParam


def Mod_List_RF(batchNum, classMods=None):
    settingParam = True

    if classMods is None:
        classMods = {}

    workingMods = deepcopy(classMods)
    rfList = []

    while settingParam:
        print('-------------------------------------------------------------------')
        print('|                    Parameter to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. n_estimators                                                |')
        print('|  2. criterion                                                   |')
        print('|  3. max_depth                                                   |')
        print('|  4. min_samples_split                                           |')
        print('|  5. min_samples_leaf                                            |')
        print('|  6. min_weight_fraction_leaf                                    |')
        print('|  7. max_features                                                |')
        print('|  8. max_leaf_nodes                                              |')
        print('|  9. min_impurity_decrease                                       |')
        print('| 10. bootstrap                                                   |')
        print('| 11. oob_score                                                   |')
        print('| 12. n_jobs                                                      |')
        print('| 13. random_state                                                |')
        print('| 14. verbose                                                     |')
        print('| 15. warm_start                                                  |')
        print('| 16. class_weight                                                |')
        print('| 17. ccp_alpha                                                   |')
        print('| 18. max_samples                                                 |')
        print('-------------------------------------------------------------------')
        try:
            print('| Which parameter should be the shifting parameter?')
            shiftParam = int(input('(Choose number or 0 to cancel): '))

            if shiftParam == 0:
                settingParam = False
                return 0
            elif shiftParam == 1:
                shiftList, sp = Set_Shiftlist("n_estimators", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(n_estimators=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 2:
                print('| As this is a non-digit parameter, customization is not allowed. |')
                print('|     There will be three classifiers created for each option.    |')

                shiftList = ["gini", "entropy", "log_loss"]
                settingParam = False

                for desc in shiftList:
                    workingMods.update(criterion=desc)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 3:
                shiftList, sp = Set_Shiftlist("max_depth", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_depth=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 4:
                shiftList, sp = Set_Shiftlist("min_samples_split", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(min_samples_split=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 5:
                shiftList, sp = Set_Shiftlist("min_samples_leaf", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(min_samples_leaf=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 6:
                shiftList, sp = Set_Shiftlist("min_weight_fraction_leaf", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(min_weight_fraction_leaf=num)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 7:
                print('|  As this has non-digit parameters, the batch will be adjusted.  |')
                print('|         There will be two additional classifiers created.       |')

                shiftList, sp = Set_Shiftlist("max_features", batchNum)
                shiftListTwo = ["sqrt", "log2"]
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_features=num)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
                for desc in shiftListTwo:
                    workingMods.update(max_features=desc)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 8:
                shiftList, sp = Set_Shiftlist("max_leaf_nodes", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_leaf_nodes=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 9:
                shiftList, sp = Set_Shiftlist("min_impurity_decrease", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(min_impurity_decrease=num)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 10:
                print('| As this is a non-digit parameter, customization is not allowed. |')
                print('|      There will be two classifiers created for each option.     |')

                shiftList = [True, False]
                settingParam = False

                for desc in shiftList:
                    workingMods.update(bootstrap=desc)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 11:
                print('-------------------------------------------------------------------')
                print('|                     You selected "oob_score"                    |')
                print('|  Callables have not be provided yet, so this is not available.  |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 12:
                shiftList, sp = Set_Shiftlist("n_jobs", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(n_jobs=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 13:
                print('-------------------------------------------------------------------')
                print('|                    You selected "random_state"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 14:
                print('-------------------------------------------------------------------')
                print('|                    You selected "verbose"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 15:
                print('-------------------------------------------------------------------')
                print('|                     You selected "warm_start"                   |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
            elif shiftParam == 16:
                print('-------------------------------------------------------------------')
                print('|                    You selected "class_weight"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 17:
                shiftList, sp = Set_Shiftlist("ccp_alpha", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(ccp_alpha=num)
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
            elif shiftParam == 18:
                shiftList, sp = Set_Shiftlist("max_samples", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_samples=int(num))
                    rf = RandomForestClassifier()

                    for parameter, setting in workingMods.items():
                        rf.set_params(**{parameter: setting})

                    rfList.append(rf)
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')

    print(rfList)
    return rfList
