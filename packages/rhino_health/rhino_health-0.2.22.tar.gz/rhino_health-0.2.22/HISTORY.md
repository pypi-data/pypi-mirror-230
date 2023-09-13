## Release History

### 0.2.22
> - Fix missing doc-strings for various SDK methods

### 0.2.21
> - Add quantile metrics and cloud-based aggregation

### 0.2.20
> - Several minor fixes and tweaks.

### 0.2.19
> - Added ability to get aggregate statistics for standard deviation
> - Reorganized aggregate statistics to allow custom implementations
> - Add ability to download multiple model weights files
> - Add ability to run inference using a previously trained model

### 0.2.18
> - Add ability to query external sql databases
> - Add ability to import cohorts from external sql database queries

### 0.2.17
> - Add ability to halt nvflare model run

### 0.2.16
> - Support for NVFlare 2.3

### 0.2.15
> - Improve supported range of requirements
> - Improve documentation
> - Add support for simulated federated learning

### 0.2.14
> - Add support for build status on AIModel
> - Internal code cleanup
> - Update requirements for the library to reduce chance of errors
> - Add support for Instant Containers on the Rhino Health Platform
> - Fix bug with Dataschema dataclass

### 0.2.13
> - Fix some bugs with run_code
> - Update documentation so users do not use internal only get/post/raw_response methods
> - Add alias for historic use cases of internal only methods with deprecation warnings

### 0.2.12
> - Add support for rate limiting
> - Add ability to query system resources

### 0.2.11
> - Add dataclass for AIModel run and train
> - Update dataclass for modelresult to allow waiting for asynchronous completion
> - cohort.run_code, session.aimodel.run_aimodel, and session.aimodel.train_aimodel 
now all return dataclasses instead of raw responses.
> - Fix bugs with various dataclass properties
> - Fix adding and removing collaborators

### 0.2.10
> - Update support of finding objects by versions

### 0.2.9

> - Completed dataclass for DataSchema to allow creation and pulling of objects
> - dataschema is now renamed to data_schema in the SDK to be consistent, 
old usages are still possible but you will receive a deprecation warning. Please use the new way of accessing data_schemas.
> - Experimental endpoint for getting workgroups
> - Fixed some issues with properties on projects
> - Fix issue with get_cohorts()
> - Fixed issue with project.aimodels returning incorrect dataclasses
> - Fixed issue with certain functions not working

### 0.2.8

> - Improved documentation for creating/running AI Models
> - Fixed the bug you reported about training where unset values in the input were being sent to the backend
> - Added ability to search by name as well as a regrouping utility function for the result of metrics
> - Added a new Python Code Generalized Compute Type
