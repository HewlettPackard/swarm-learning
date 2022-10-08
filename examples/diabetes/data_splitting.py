############################################################################

## Licensed under the Apache License, Version 2.0 (the "License"); you may

## not use this file except in compliance with the License. You may obtain

## a copy of the License at

##

##    http://www.apache.org/licenses/LICENSE-2.0

##

## Unless required by applicable law or agreed to in writing, software

## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT

## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the

## License for the specific language governing permissions and limitations

## under the License.

############################################################################
import pandas as pd
import numpy as np
import os

def create_dir(path):
    paths = []
    for i in range(3):
        os.makedirs(path + 'node' + str(i + 1))
        paths.append(path + 'node' + str(i + 1) + '/')
    return paths
def data_splitting(data,paths):

    df = pd.read_csv(data)

    df_train = df.iloc[:761, :]
    df_test = df.iloc[761:, :]

    x_test = df_test.iloc[:, :-1]
    y_test = df_test.Diabetic

    df_children = df_train[df_train['Age'] == 0]

    x_train = df_children.iloc[:, :-1]
    y_train = df_children.Diabetic

    np.savez_compressed(paths[0] + 'diabetes', x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)

    df_train = df_train.drop(index=df_children.index)
    df_female = df_train[df_train['Gender'] == 1]

    df_female_pregnant = df_female[df_female['Pregancies'] == 1]
    df_female_non_pregnant = df_female[df_female['Pregancies'] == 0]

    df_female_pregnant80 = df_female_pregnant.iloc[:65, :]
    df_female_non_pregnant_20 = df_female_non_pregnant.iloc[:35, :]

    df_node2 = pd.concat([df_female_pregnant80, df_female_non_pregnant_20], axis=0)
    x_train = df_node2.iloc[:, :-1]
    y_train = df_node2.Diabetic

    np.savez_compressed(paths[1] + 'diabetes', x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)

    df_train = df_train.drop(index=df_node2.index)

    x_train = df_train.iloc[:, :-1]
    y_train = df_train.Diabetic

    np.savez_compressed(paths[2] + 'diabetes', x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)

def main():
    path = "app-data/"
    paths = create_dir(path)
    data_splitting(path + "data.csv",paths)


if __name__ == "__main__":
    main()