import numpy as np
from regression_tools import * 
from preprocessing import *
from implementations import *

def build_k_indices(y, k_fold, seed):
    """
    Build k indices for k-fold cross-validation.
    """
    num_row = y.shape[0]
    interval = int(num_row / k_fold)
    np.random.seed(seed)
    indices = np.random.permutation(num_row)
    k_indices = [indices[k * interval: (k + 1) * interval]
                 for k in range(k_fold)]
    return np.array(k_indices)

def cross_validation_lasso(y, phi, k_indices, k, lambda_, gamma, max_iters, not_poly_features):
    """
    Computes one step of cross validation with lasso regression and returns the fraction of correct classifications.
    """
    # Get k'th subgroup in test, others in train    
    train_indices = np.delete(k_indices , k , 0).reshape((k_indices.shape[0]-1) * k_indices.shape[1])
    
    # Retrieve the test and train sample
    x_test = phi[k_indices[k],:]
    x_train = phi[train_indices,:]
    y_test = y[k_indices[k]]
    y_train = y[train_indices]
    
    # Cross validation to find the best w
    w, loss = lasso_regression_GD(y_train, x_train, lambda_, np.zeros(x_train.shape[1]), max_iters, gamma)
    
    # Calculate result
    result=(y_test==(x_test.dot(w)>0.5)).sum()/y_test.shape[0]
    
    return result


def cross_validation_lasso_demo(y_train,x_train,degrees,k_fold,lambdas,gammas,max_iters,seed):
    """
    Return the matrix of proportion of correct classifications obtained by cross validation from lasso regression.
    """
    
    # Split data in k fold
    k_indices = build_k_indices(y_train, k_fold, seed)
    # Clean data
    x_train_cleaned,nmc_tr=cleaning_function(x_train,-999)
    # Feature augmentation
    x_train_cleaned,noaf=features_augmentation(x_train_cleaned,not_augm_features=nmc_tr+1)

    # Cross validation
    cost_te=np.zeros((gammas.size,lambdas.size,degrees.size))
    for ind_gam,gamma in enumerate(gammas):
        for ind_lamb,lambda_ in enumerate(lambdas):
            if lambda_!=0:
                for ind_deg,degree in enumerate(degrees):
                    # Create the test sample
                    phi_train=build_polinomial(x_train_cleaned,degree,not_poly_features=noaf+nmc_tr+1)
                    phi_train=norm_data(x_train_cleaned,not_norm_features=nmc_tr+1)
                    loss_te = np.zeros(k_fold)
                    for k in range (k_fold):
                        # Calculate the result
                        result = cross_validation_lasso(y_train, phi_train, k_indices, k , lambda_, gamma, max_iters, nmc_tr+1+noaf)
                        #Store it
                        loss_te[k]= result

                    cost_te[ind_gam,ind_lamb,ind_deg]=loss_te.mean()
    return cost_te