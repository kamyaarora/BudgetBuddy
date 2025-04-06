## BudgetBuddy

### Candidate Risk Evaluation
This model generates 500 synthetic data points representing potential homebuyers using heuristics based on attributes like credit score, debt-to-income ratio, and down payment to assign a risk level (high, medium, low). It uses a RandomForestClassifier within a scikit-learn Pipeline that includes preprocessing steps like one-hot encoding for categorical features. The model is trained, evaluated, and saved using joblib, and includes functionality to load the model and predict risk levels for new user input.

