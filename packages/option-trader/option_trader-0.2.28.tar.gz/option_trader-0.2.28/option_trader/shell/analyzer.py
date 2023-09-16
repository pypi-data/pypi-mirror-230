
def win_rate(pos_df):
    
    df = df.loc[df['Exp Price'] >= 0]
    
    df['Class'] = ['Win' if x > 0 else 'Loss' for x in df['Profit or Loss']]

    print(df.groupby('Class').size())

    
def learn(pos_df):
    
    df = df.loc[df['Exp Price'] >= 0]
    
    df['Class'] = ['Win' if x > 0 else 'Loss' for x in df['Profit or Loss']]

    df.groupby('Class').size()

    df = df[['Symbol', 'Strategy', 'Spread', 'Profit or Loss', 'PNL', 'Win Prob %', 'Init Trend', 'Init Slope', 'Init Delta', 'Init IV', 'Class']]

    df1 = df[['Win Prob %', 'Init Slope', 'Init Delta', 'Init IV', 'Class']]

    from matplotlib import pyplot
    
    df1.hist()
    pyplot.show()

    # box and whisker plots
    df1.plot(kind='box', subplots=True, layout=(3,2), sharex=False, sharey=False)
    pyplot.show()

    from pandas.plotting import scatter_matrix
    # scatter plot matrix
    scatter_matrix(df1)
    pyplot.show()

    from sklearn.model_selection import train_test_split
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import classification_report
    from sklearn.metrics import confusion_matrix
    from sklearn.metrics import accuracy_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.naive_bayes import GaussianNB
    from sklearn.svm import SVC
    # Split-out validation dataset
    array = df1.values
    X = array[:,0:4]
    y = array[:,4]
    X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.20, random_state=1)

    ...
    # Spot Check Algorithms
    models = []
    models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
    models.append(('LDA', LinearDiscriminantAnalysis()))
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('CART', DecisionTreeClassifier()))
    models.append(('NB', GaussianNB()))
    models.append(('SVM', SVC(gamma='auto')))
    # evaluate each model in turn
    results = []
    names = []
    for name, model in models:
        kfold = StratifiedKFold(n_splits=10, random_state=1, shuffle=True)
        cv_results = cross_val_score(model, X_train, Y_train, cv=kfold, scoring='accuracy')
        results.append(cv_results)
        names.append(name)
        print('%s: %f (%f)' % (name, cv_results.mean(), cv_results.std()))


    # Compare Algorithms
    pyplot.boxplot(results, labels=names)
    pyplot.title('Algorithm Comparison')
    pyplot.show()

    # Make predictions on validation dataset
    model = SVC(gamma='auto')
    model.fit(X_train, Y_train)
    predictions = model.predict(X_validation)

    # Evaluate predictions
    print(accuracy_score(Y_validation, predictions))
    print(confusion_matrix(Y_validation, predictions))
    print(classification_report(Y_validation, predictions))
