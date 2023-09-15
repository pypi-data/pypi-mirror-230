from sklearn.neural_network import MLPClassifier
from copy import deepcopy
from ast import literal_eval


def Customization_MLP(mods=None):
    if mods is None:
        mods = {}
    mlp = MLPClassifier()

    # Selection Loop
    selectingParams = True
    while selectingParams:
        print('-------------------------------------------------------------------')
        print('|             PLEASE CUSTOMIZE MULTI-LAYER PERCEPTRON             |')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. hidden_layer_sizes                                          |')
        print('|  2. activation                                                  |')
        print('|  3. solver                                                      |')
        print('|  4. alpha                                                       |')
        print('|  5. batch_size                                                  |')
        print('|  6. learning_rate                                               |')
        print('|  7. learning_rate_init                                          |')
        print('|  8. power_t                                                     |')
        print('|  9. max_iter                                                    |')
        print('| 10. shuffle                                                     |')
        print('| 11. random_state                                                |')
        print('| 12. tol                                                         |')
        print('| 13. verbose                                                     |')
        print('| 14. warm_start                                                  |')
        print('| 15. momentum                                                    |')
        print('| 16. nesterovs_momentum                                          |')
        print('| 17. early_stopping                                              |')
        print('| 18. validation_fraction                                         |')
        print('| 19. beta_1                                                      |')
        print('| 20. beta_2                                                      |')
        print('| 21. epsilon                                                     |')
        print('| 22. n_iter_no_change                                            |')
        print('| 23. max_fun                                                     |')
        try:
            parameter = int(input("| Enter here: "))

            # Decision Tree
            if parameter == 0:
                selectingParams = False
            elif parameter == 1:
                print('-------------------------------------------------------------------')
                print('|                 You selected "hidden_layer_sizes"               |')
                hls_input = input("| Enter in the hidden layers in array format (XX, XX...): ")
                hls_input = literal_eval(hls_input)
                mods.update(hidden_layer_sizes=hls_input)
                mlp.set_params(**{'hidden_layer_sizes': hls_input})
            elif parameter == 2:
                print('-------------------------------------------------------------------')
                print('|                    You selected "activation"                    |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. relu (Default)                                              |')
                print('|  2. identity                                                    |')
                print('|  3. logistic                                                    |')
                print('|  4. tanh                                                        |')
                hls_input = int(input("| Select the activation function: "))
                if hls_input == 1:
                    mods.update(activation="relu")
                    mlp.set_params(**{'activation': "relu"})
                elif hls_input == 2:
                    mods.update(activation="identity")
                    mlp.set_params(**{'activation': "identity"})
                elif hls_input == 3:
                    mods.update(activation="logistic")
                    mlp.set_params(**{'activation': "logistic"})
                elif hls_input == 4:
                    mods.update(activation="tanh")
                    mlp.set_params(**{'activation': "tanh"})
            elif parameter == 3:
                print('-------------------------------------------------------------------')
                print('|                      You selected "solver"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. adam (Default)                                              |')
                print('|  2. lbfgs                                                       |')
                print('|  3. sgd                                                         |')
                solver_input = int(input("| Select the weight optimization solver: "))
                if solver_input == 1:
                    mods.update(solver="adam")
                    mlp.set_params(**{'solver': "adam"})
                elif solver_input == 2:
                    mods.update(solver="lbfgs")
                    mlp.set_params(**{'solver': "lbfgs"})
                elif solver_input == 3:
                    mods.update(solver="sgd")
                    mlp.set_params(**{'solver': "sgd"})
            elif parameter == 4:
                print('-------------------------------------------------------------------')
                print('|                       You selected "alpha"                      |')
                alpha_input = float(input("| Enter the L2 regularization value: "))
                mods.update(alpha=alpha_input)
                mlp.set_params(**{'alpha': alpha_input})
            elif parameter == 5:
                print('-------------------------------------------------------------------')
                print('|                    You selected "batch_size"                    |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. auto (Default)                                              |')
                print('|  2. Custom                                                      |')
                batch_size_input = int(input("| Select the size of minibatches for processing: "))
                if batch_size_input == 1:
                    mods.update(batch_size="auto")
                    mlp.set_params(**{'batch_size': "auto"})
                elif batch_size_input == 2:
                    batch_size_num = int(input("| Enter the batch size: "))
                    mods.update(batch_size=batch_size_num)
                    mlp.set_params(**{'batch_size': batch_size_num})
            elif parameter == 6:
                print('-------------------------------------------------------------------')
                print('|                  You selected "learning_rate"                   |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. constant (Default)                                          |')
                print('|  2. invscaling                                                  |')
                print('|  3. adaptive                                                    |')
                learning_rate_input = int(input("| Select the learning rate setting: "))
                if learning_rate_input == 1:
                    mods.update(learning_rate="constant")
                    mlp.set_params(**{'learning_rate': "constant"})
                elif learning_rate_input == 2:
                    mods.update(learning_rate="invscaling")
                    mlp.set_params(**{'learning_rate': "invscaling"})
                elif learning_rate_input == 3:
                    mods.update(learning_rate="adaptive")
                    mlp.set_params(**{'learning_rate': "adaptive"})
            elif parameter == 7:
                print('-------------------------------------------------------------------')
                print('|                You selected "learning_rate_init"                |')
                lri_input = float(input("| Enter the initial learning rate: "))
                mods.update(learning_rate_init=lri_input)
                mlp.set_params(**{'learning_rate_init': lri_input})
            elif parameter == 8:
                print('-------------------------------------------------------------------')
                print('|                      You selected "power_t"                     |')
                power_t_input = float(input("| Enter the exponent for inverse scaling learning rate: "))
                mods.update(power_t=power_t_input)
                mlp.set_params(**{'power_t': power_t_input})
            elif parameter == 9:
                print('-------------------------------------------------------------------')
                print('|                     You selected "max_iter"                     |')
                max_iter_input = int(input("| Enter the number of iterations: "))
                mods.update(max_iter=max_iter_input)
                mlp.set_params(**{'max_iter': max_iter_input})
            elif parameter == 10:
                print('-------------------------------------------------------------------')
                print('|                     You selected "shuffle"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. true (default)                                              |')
                print('|  2. false                                                       |')
                shuffle_input = int(input("| Select whether to shuffle samples in each iteration: "))
                if shuffle_input == 1:
                    mods.update(shuffle=True)
                    mlp.set_params(**{'shuffle': True})
                elif shuffle_input == 2:
                    mods.update(shuffle=False)
                    mlp.set_params(**{'shuffle': False})
            elif parameter == 11:
                print('-------------------------------------------------------------------')
                print('|                   You selected "random_state"                   |')
                random_state_input = int(input("| Select the key for the randomizer: "))
                mods.update(random_state=random_state_input)
                mlp.set_params(**{'random_state': random_state_input})
            elif parameter == 12:
                print('-------------------------------------------------------------------')
                print('|                       You selected "tol"                        |')
                tol_input = float(input("| Enter the tolerance criterion: "))
                mods.update(tol=tol_input)
                mlp.set_params(**{'tol': tol_input})
            elif parameter == 13:
                print('-------------------------------------------------------------------')
                print('|                     You selected "verbose"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. false (default)                                             |')
                print('|  2. true                                                        |')
                verbose_input = int(input("| Select the verbose setting: "))
                if verbose_input == 1:
                    mods.update(verbose=False)
                    mlp.set_params(**{'verbose': False})
                elif verbose_input == 2:
                    mods.update(verbose=True)
                    mlp.set_params(**{'verbose': True})
            elif parameter == 14:
                print('-------------------------------------------------------------------')
                print('|                     You selected "warm_start"                   |')
                print('| This can be used if you wish to refit and further train single  |')
                print('| programs using option 9.                                        |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. True                                                        |')
                print('|  2. False (default)                                             |')
                warm_start_input = int(input('| Enter here or 0 if you changed your mind: '))
                if warm_start_input == 1:
                    mods.update(warm_start=True)
                    mlp.set_params(**{'warm_start': True})
                elif warm_start_input == 2:
                    mods.update(warm_start=False)
                    mlp.set_params(**{'warm_start': False})
            elif parameter == 15:
                print('-------------------------------------------------------------------')
                print('|                     You selected "momentum"                     |')
                momentum_input = float(input("| Enter the GD momentum setting: "))
                mods.update(momentum=momentum_input)
                mlp.set_params(**{'momentum': momentum_input})
            elif parameter == 16:
                print('-------------------------------------------------------------------')
                print('|                You selected "nesterovs_momentum"                |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. true (default)                                              |')
                print('|  2. false                                                       |')
                nesterovs_momentum_input = int(input("| Select whether to use Nesterov’s momentum: "))
                if nesterovs_momentum_input == 1:
                    mods.update(nesterovs_momentum=True)
                    mlp.set_params(**{'nesterovs_momentum': True})
                elif nesterovs_momentum_input == 2:
                    mods.update(nesterovs_momentum=False)
                    mlp.set_params(**{'nesterovs_momentum': False})
            elif parameter == 17:
                print('-------------------------------------------------------------------')
                print('|                  You selected "early_stopping"                  |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. false (default)                                             |')
                print('|  2. true                                                        |')
                early_stopping_input = int(input("| Select whether to use early stopping mechanism: "))
                if early_stopping_input == 1:
                    mods.update(early_stopping=False)
                    mlp.set_params(**{'early_stopping': False})
                elif early_stopping_input == 2:
                    mods.update(early_stopping=True)
                    mlp.set_params(**{'early_stopping': True})
            elif parameter == 18:
                print('-------------------------------------------------------------------')
                print('|                You selected "validation_fraction"               |')
                validation_fraction_input = float(input("| Enter the validation fraction: "))
                mods.update(validation_fraction=validation_fraction_input)
                mlp.set_params(**{'validation_fraction': validation_fraction_input})
            elif parameter == 19:
                print('-------------------------------------------------------------------')
                print('|                       You selected "beta_1"                     |')
                beta_1_input = float(input("| Enter the beta 1 value: "))
                mods.update(beta_1=beta_1_input)
                mlp.set_params(**{'beta_1': beta_1_input})
            elif parameter == 20:
                print('-------------------------------------------------------------------')
                print('|                       You selected "beta_2"                     |')
                beta_2_input = float(input("| Enter the beta 2 value: "))
                mods.update(beta_2=beta_2_input)
                mlp.set_params(**{'beta_2': beta_2_input})
            elif parameter == 21:
                print('-------------------------------------------------------------------')
                print('|                      You selected "epsilon"                     |')
                epsilon_input = float(input("| Enter the epsilon value: "))
                mods.update(epsilon=epsilon_input)
                mlp.set_params(**{'epsilon': epsilon_input})
            elif parameter == 22:
                print('-------------------------------------------------------------------')
                print('|                 You selected "n_iter_no_change"                 |')
                ninc_input = int(input("| Enter the epochs limit that prevents tol improvement: "))
                mods.update(n_iter_no_change=ninc_input)
                mlp.set_params(**{'n_iter_no_change': ninc_input})
            elif parameter == 23:
                print('-------------------------------------------------------------------')
                print('|                      You selected "max_fun"                     |')
                max_fun_input = float(input("| Enter the maximum number of loss function calls: "))
                mods.update(max_fun=max_fun_input)
                mlp.set_params(**{'max_fun': max_fun_input})
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
        mlp.set_params(**{parameter: setting})

    newMods = deepcopy(mods)
    return mlp, newMods


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


def Mod_List_MLP(batchNum, classMods=None):
    settingParam = True

    if classMods is None:
        classMods = {}

    workingMods = deepcopy(classMods)
    mlpList = []

    while settingParam:
        print('-------------------------------------------------------------------')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. hidden_layer_sizes                                          |')
        print('|  2. activation                                                  |')
        print('|  3. solver                                                      |')
        print('|  4. alpha                                                       |')
        print('|  5. batch_size                                                  |')
        print('|  6. learning_rate                                               |')
        print('|  7. learning_rate_init                                          |')
        print('|  8. power_t                                                     |')
        print('|  9. max_iter                                                    |')
        print('| 10. shuffle                                                     |')
        print('| 11. random_state                                                |')
        print('| 12. tol                                                         |')
        print('| 13. verbose                                                     |')
        print('| 14. warm_start                                                  |')
        print('| 15. momentum                                                    |')
        print('| 16. nesterovs_momentum                                          |')
        print('| 17. early_stopping                                              |')
        print('| 18. validation_fraction                                         |')
        print('| 19. beta_1                                                      |')
        print('| 20. beta_2                                                      |')
        print('| 21. epsilon                                                     |')
        print('| 22. n_iter_no_change                                            |')
        print('| 23. max_fun                                                     |')

        try:
            print('| Which parameter should be the shifting parameter?')
            shiftParam = int(input('(Choose number or 0 to cancel): '))

            if shiftParam == 0:
                settingParam = False
                return 0
            elif shiftParam == 1:
                print('-------------------------------------------------------------------')
                print('|                 You selected "hidden_layer_sizes"               |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 2:
                print('-------------------------------------------------------------------')
                print('|                     You selected "activation"                   |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 3:
                print('-------------------------------------------------------------------')
                print('|                       You selected "solver"                     |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 4:
                shiftList, sp = Set_Shiftlist("alpha", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(alpha=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})

                    mlpList.append(mlp)
            elif shiftParam == 5:
                shiftList, sp = Set_Shiftlist("batch_size", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(batch_size=int(num))
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})

                    mlpList.append(mlp)
            elif shiftParam == 6:
                print('-------------------------------------------------------------------')
                print('|                   You selected "learning_rate"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 7:
                shiftList, sp = Set_Shiftlist("learning_rate_init", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(learning_rate_init=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})

                    mlpList.append(mlp)
            elif shiftParam == 8:
                shiftList, sp = Set_Shiftlist("power_t", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(power_t=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})

                    mlpList.append(mlp)
            elif shiftParam == 9:
                shiftList, sp = Set_Shiftlist("max_iter", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_iter=int(num))
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})

                    mlpList.append(mlp)
            elif shiftParam == 10:
                print('-------------------------------------------------------------------')
                print('|                      You selected "shuffle"                     |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 11:
                print('-------------------------------------------------------------------')
                print('|                    You selected "random_state"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 12:
                shiftList, sp = Set_Shiftlist("tol", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(tol=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 13:
                print('-------------------------------------------------------------------')
                print('|                      You selected "verbose"                     |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 14:
                print('-------------------------------------------------------------------')
                print('|                     You selected "warm_start"                   |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 15:
                shiftList, sp = Set_Shiftlist("momentum", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(momentum=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 16:
                print('-------------------------------------------------------------------')
                print('|                 You selected "nesterovs_momentum"               |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 17:
                print('-------------------------------------------------------------------')
                print('|                   You selected "early_stopping"                 |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 18:
                shiftList, sp = Set_Shiftlist("validation_fraction", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(validation_fraction=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 19:
                shiftList, sp = Set_Shiftlist("beta_1", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(beta_1=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 20:
                shiftList, sp = Set_Shiftlist("beta_2", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(beta_2=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 21:
                shiftList, sp = Set_Shiftlist("epsilon", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(epsilon=num)
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 22:
                shiftList, sp = Set_Shiftlist("n_iter_no_change", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(n_iter_no_change=int(num))
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
            elif shiftParam == 23:
                shiftList, sp = Set_Shiftlist("max_fun", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_fun=int(num))
                    mlp = MLPClassifier()

                    for parameter, setting in workingMods.items():
                        mlp.set_params(**{parameter: setting})
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')

    print(mlpList)
    return mlpList
