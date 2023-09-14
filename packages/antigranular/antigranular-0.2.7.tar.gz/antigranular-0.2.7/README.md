# Privacy Unleashed: Working with Antigranular
Antigranular is a community-led, open-source platform that combines confidential computing with differential privacy. This integration fosters a secure environment to handle and fully utilize unseen data.
### Connect to Antigranular 
You can activate Antigranular using the magic command `%%ag`. Any code that follows `%%ag` will run on our remote server. This server operates under restricted conditions, allowing only methods that guarantee differential privacy.

Install the Antigranular package using `pip`:
```python
!pip install antigranular
```
Import the `Antigranular` library:
```python
import antigranular as ag
```
To connect to the AG Enclave Server, use your client credentials and either a dataset or competition ID:
```python
ag_client = ag.login(user_id="<user_id>", user_secret="<user_secret>",  competition="<competition_name>")
```
or
```python
ag_client = ag.login(user_id="<user_id>", user_secret="<user_secret>", dataset="<dataset_name>")
```
A succesful login will register the cell magic `%%ag`. 

### Loading Private Datasets 
Private datasets can be loaded as `PrivateDataFrames` and `PrivateSeries` using the `ag_utils` library. `ag_utils` is a package locally installed on the remote server, which eliminates the need to install anything other than the antigranular package.

The `load_dataset()` method allows for obtaining a dictionary of private objects. The structure of the response dictionary, along with the dataset path and private object names, will be specified during the competition.
```python
%%ag
from op_pandas import PrivateDataFrame, PrivateSeries
from ag_utils import load_dataset 
"""
Sample response structure
{
    train_x : priv_train_x,
    train_y : priv_train_y,
    test_x : priv_test_x
}
"""
# Obtaining the dictionary containing private objects
response = load_dataset("<path_to_dataset>")

# Unpacking the response dictionary
train_x = response["train_x"]
train_y = response["train_y"]
test_x = response["test_x"]
```
### Exporting Objects
Since the code following `%%ag` runs in a highly restricted environment, it's necessary to export differentially private objects to the local environment for further analysis. The `export` method in `ag_utils` allows data objects to be exported.
##### **API info**: `export(obj, variable_name:str)`

This command exports the remote object to the local environment and assigns it to the specified variable name. Note that `PrivateSeries` and `PrivateDataFrame` objects cannot be exported and will raise an error if you attempt to do so.

```python 
%%ag
from ag_utils import export
train_info = train_x.describe(eps=1)
export(train_info , 'variable_name')
```
Once exported, you can perform any kind of data analysis on the differentially private object.

```python
# Local code block
print(variable_name)
--------------------------------------
                    Age         Salary
    count  99987.000000   99987.000000
    mean      38.435953  120009.334336
    std       12.167379   46255.486093
    min       18.257448   40048.259037
    25%       27.185189   80057.639960
    50%       38.210860  120380.291216
    75%       49.147724  159835.637091
    max       59.282932  199920.664706
```

## Libraries Supported


- **`pandas`**: An adaptable data manipulation library offering efficient data structures and tools for data analysis and manipulation.

- **`op_pandas`**: A wrapped library specifically designed for differentially private data manipulation within the Pandas framework. It enhances privacy-preserving techniques and enables privacy-aware data processing.

- **`op_diffprivlib`**: A differentially private library that provides various privacy-preserving algorithms and mechanisms for machine learning and data analysis tasks.

- **`op_smartnoise`**: A library focused on privacy-preserving analysis using the SmartNoise framework. It provides tools for differential privacy and secure computation.

- **`op_opendp`**: A library that offers differentially private data analysis and algorithms based on the OpenDP project. It provides privacy-preserving methods and tools for statistical analysis.