import matplotlib.pyplot as plt
import copy
import numpy as np
from Neural_network import *
import pandas as pd


class grid_search_parameter:
    def __init__(self,learning_rate,momentum,batch_size,architecture,neurons, regularization, epoch):
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.batch_size = batch_size
        self.architecture = architecture
        self.neurons = neurons
        self.regularization = regularization
        self.epoch = epoch


def print_result(misClass_error, misClass_error_evaluation,
                 squared_error, squared_error_evaluation, arc, bat, lr, mo,
                 reg, n_figure, eval_string, lossObject, save_in_dir):
    # get accuracy
    accuracy = 1 - misClass_error
    accuracy_avarage = 1 - misClass_error_evaluation
    # plot result
    plt.figure(n_figure, dpi=300)  # select figure number 'n_figure'
    plt.subplot(2, 1, 1)
    plt.plot(range(1, len(accuracy) + 1), accuracy, '--')
    plt.plot(range(1, len(accuracy_avarage) + 1), accuracy_avarage, '-')
    plt.legend(['training set', eval_string])
    plt.xlabel("epochs")
    plt.ylabel("accuracy")
    # plot squaredError
    plt.subplot(2, 1, 2)
    plt.plot(range(1, len(squared_error) + 1), squared_error, '--')
    plt.plot(range(1, len(squared_error_evaluation) + 1), squared_error_evaluation, '-')
    plt.legend(['training set', eval_string])
    plt.xlabel("epochs")
    plt.ylabel(lossObject.__class__.__name__)
    s = save_in_dir + "lr_" + transf_value(lr) + "-mo_" + transf_value(mo) + "-bat:" + transf_value(
        bat) + "-reg_" + transf_value(reg) + "-arc_" + tranf_arc(arc)
    plt.tight_layout()  # minimize overlap of subplots
    plt.savefig(s)
    plt.close()


def holdout(frac, train_data):
    """
    Splits train_data in training set and validation set. Each set has the property that
    the positive and negative example follow roughly the same distribution of the original set.
    The training set is 'frac' percent of the data whereas the validation set is the remaining
    (1-frac) percent.

    :param frac: fraction of the dataset used for training
    :param train_data: dataset
    :return: training_set and validation_set
    """
    # shuffle data set
    train_data = train_data.reindex(np.random.permutation(train_data.index))
    # devide in positive and negative examples
    positive_set = train_data[train_data["label"] == 1]
    negative_set = train_data[train_data["label"] == 0]

    # compute length of partitions given frac
    len_pos_training = int(np.round(frac * len(positive_set)))  # for training set
    len_neg_training = int(np.round(frac * len(negative_set)))  # for validation set
    len_pos_validation = len(positive_set) - len_pos_training        # for training set
    len_neg_validation = len(negative_set) - len_neg_training        # for validation set

    positive_set_partition = positive_set.head(len_pos_training)
    negative_set_partition = negative_set.head(len_neg_training)
    positive_set_other = positive_set.head(len_pos_validation)
    negative_set_other = negative_set.head(len_neg_validation)
    training_set = pd.concat([positive_set_partition, negative_set_partition])
    validation_set = pd.concat([positive_set_other, negative_set_other])

    # shuffle training and validation set
    training_set = training_set.reindex(np.random.permutation(training_set.index))
    validation_set = validation_set.reindex(np.random.permutation(validation_set.index))
    return training_set, validation_set


def transf_value(value):
    """
    transform value of variable to suitable string
    :param value: string to be transformef
    :return:
    """
    return str(value).replace(".",",")


def tranf_arc(architecture):
    """
    transoform architecture value to suitable string
    :param architecture: architecture to be transformed
    :return:
    """
    string = "["
    for i in architecture:
        string += str(i)+","
    string += "]"
    return string


def grid_search(parameter, loss_obj, tr_patterns, tr_labels, vl_patterns,vl_labels, n_trials, save_in_dir):
    """
    grid search for optimal hyperparameter
    :param network: network to be trained
    :param loss_obj: loss used
    :param reguaritazion:
    :param n_trials: n of random trails for each value
    :param tr_patterns: traning set patterns
    :param tr_labels: traning set target
    :param vl_patterns: validation set patterns
    :param vl_labels: validation set target
    :param directory where to save results (learning curves)
    :return:
    """
    total_experiments = len(parameter.regularization) * len(parameter.learning_rate) \
                        * len(parameter.momentum) * len(parameter.batch_size) * len(parameter.architecture)
    n_figure = 0  # index of figures
    # for every value
    for reg in parameter.regularization:
        for lr in parameter.learning_rate:
            for mo in parameter.momentum:
                for bat in parameter.batch_size:
                    for arc, neur in zip(parameter.architecture,parameter.neurons):
                            print n_figure, "out of", total_experiments, "experiments"
                            # initialize lists for saving reslut
                            squared_error_average = np.zeros(parameter.epoch)
                            misClass_error_average = np.zeros(parameter.epoch)
                            squared_error_validation_average = np.zeros(parameter.epoch)
                            misClass_error_validation_average = np.zeros(parameter.epoch)
                            # n_trials then average
                            for n in range(n_trials):
                                # buid a new network
                                network = Network(arc, neur)
                                # train
                                squared_error, misClass_error, \
                                squared_error_validation, misClass_error_validation = \
                                    network.train(data=tr_patterns, targets=tr_labels, eval_data=vl_patterns,
                                                  eval_targets=vl_labels, lossObject=loss_obj, epochs=parameter.epoch,
                                                  learning_rate=lr, batch_size=bat, momentum=mo, regularization=reg)

                                # append result of single epoch in list previously created
                                squared_error_average += squared_error
                                misClass_error_average += misClass_error
                                squared_error_validation_average += squared_error_validation
                                misClass_error_validation_average += misClass_error_validation

                            # taking mean error over trials and over patterns
                            squared_error_average /= float(n_trials) * len(tr_patterns)
                            misClass_error_average /= float(n_trials) * len(tr_patterns)
                            squared_error_validation_average /= float(n_trials) * len(vl_patterns)
                            misClass_error_validation_average /= float(n_trials) * len(vl_patterns)

                            print_result(misClass_error_average, misClass_error_validation_average,
                                         squared_error_average, squared_error_validation_average,
                                         arc, bat, lr, mo, reg, n_figure, "validation set", loss_obj, save_in_dir)
                            n_figure += 1  # increment to create a new figure