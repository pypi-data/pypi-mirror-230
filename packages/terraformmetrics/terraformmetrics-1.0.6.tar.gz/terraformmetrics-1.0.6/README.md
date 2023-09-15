<p align="center" width="100%">
    <img src="logo.png"> 
</p>


<h2 align="center">The static source code measurement tool for Terraform</h2>

**TerrafomMetrics** is a Python-based static source code measurement tool to characterize Infrastructure-as-Code.
It helps quantify the characteristics of infrastructure code to support DevOps engineers when maintaining and evolving it. 
It currently supports 25 source code metrics, though other metrics can be derived by combining the implemented ones.


## How to install

Installation is made simple by the [PyPI repository](https://pypi.org/project/terraformmetrics/).
Download the tool and install it with:

```pip install terraformmetrics```

or, alternatively from the source code project directory:

```
pip install -r requirements.txt
pip install .
```


## How to use

### **Command-line**

Run ```terraform-metrics --help``` for instructions about the usage:

```
usage: terraform-metrics [-h] [--omit-zero-metrics] [-d DEST] [-o] [-v] src

Extract metrics from Terraform scripts.

positional arguments:
  src                   source file (tf file) or
                        directory

optional arguments:
  -h, --help            show this help message and exit
  --omit-zero-metrics   omit metrics with value equal 0
  -d DEST, --dest DEST  destination path to save results
  -o, --output          shows output
  -v, --version         show program's version number and exit
```



This is an example where metrics are calculated on the main.tf file assuming that it is run from the folder where the file is located. The result will be saved in the report.json file

```terraform-metrics --omit-zero-metrics main.tf --dest report.json```
<br>

### **Python**

*TerraformMetrics* currently supports up to 25 source code metrics, implemented in Python. 
To extract the value for a given metric follow this pattern:

```python
from terraformmetrics.<general|terraformspec>.metric import Metric

script = 'a valid yaml script'
value = Metric(script).count()
```

where _metric_ and _Metric_ have to be replaced with the name of the desired metric module to compute the value of a specific metric. <br>
The difference between the *general* and the *terraformspec* modules lies in the fact that the *terraformspec* module contains metrics specific to terraform, while the *general* module contains metrics that can be generalized to other languages (for example, the lines of code).

For example, to count the number of lines of code:

```python
from terraformmetrics.terraformspec.num_resources import NumResources

script = """ 
     resource "opc_storage_container" "accs-apps" {
       name = "my-accs-apps"
     }

     resource "opc_storage_object" "example-java-app" {
       name         = "employees-web-app.zip"
       container    = "${opc_storage_container.accs-apps.name}"
       file         = "./employees-web-app.zip"
       etag         = "${md5(file("./employees-web-app.zip"))}"
       content_type = "application/zip;charset=UTF-8"
     }
     """

value = NumResources(script).count()
print('Number of resources: ', value)

```


To extract the value for the 25 metrics at once,  import the ```terraformmetrics.metrics_extractor``` package and call the method ```extract_all()``` (in this case the return value will be a json object):

```python
from terraformmetrics.metrics_extractor import extract_all

script = """ 
     resource "opc_storage_container" "accs-apps" {
       name = "my-accs-apps"
     }

     resource "opc_storage_object" "example-java-app" {
       name         = "employees-web-app.zip"
       container    = "${opc_storage_container.accs-apps.name}"
       file         = "./employees-web-app.zip"
       etag         = "${md5(file("./employees-web-app.zip"))}"
       content_type = "application/zip;charset=UTF-8"
     }
     """

metrics = extract_all(script)
print('Lines of executable code:', metrics['lines_code'])
```