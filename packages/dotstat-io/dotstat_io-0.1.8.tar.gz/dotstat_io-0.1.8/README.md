### DotStat_IO: 
A generic python package which could be integrated with other end-user applications and Gitlab runner to perform basic io with .Stat Suite. 
Its role is to mask the complexities of authentication to connect to .Stat Suite.
The user needs to provide a set of parameters and the package exposes a couple of methods which will download or upload data from/to .Stat Suite.

### This package contains three modules:
- ADFSAuthentication module
- KeycloakAuthentication module
- Download_upload module

### In ADFSAuthentication module, four methods are available:
#### 1. To initialise the module for interactive use:
```python
from dotstat_io.authentication import AdfsAuthentication
with AdfsAuthentication.interactive(
        client_id=client_id,
        sdmx_resource_id=sdmx_resource_id,
        scopes=scopes,
        authority_url=authority_url,
        redirect_port=redirect_port) as Interactive_obj:
    token = Interactive_obj.get_token()
```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite PP
* `scopes:` Scopes requested to access a protected API (a resource defined by sdmx_resource_id)
* `authority_url:` URL that identifies a token authority
* `redirect_port:` The port of the address to return to upon receiving a response from the authority

#### 2. To initialise the module for non-interactive use using a secret: 
```python
from dotstat_io.authentication import AdfsAuthentication
with AdfsAuthentication.nointeractive_with_secret(
        client_id=client_id,
        sdmx_resource_id=sdmx_resource_id,
        scopes=scopes,
        authority_url=authority_url,
        client_secret=client_secret) as Nointeractive_with_secret_obj:
    token = Nointeractive_with_secret_obj.get_token()
```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite PP
* `scopes:` Scopes requested to access a protected API (a resource defined by sdmx_resource_id)
* `authority_url:` URL that identifies a token authority
* `client_secret:` The application secret that you created during app registration in ADFS

#### 3. To initialise the module for non-interactive use using windows client authentication:
```python
from dotstat_io.authentication import AdfsAuthentication
with AdfsAuthentication.nointeractive_with_adfs(
        client_id=client_id,
        sdmx_resource_id=sdmx_resource_id,
        token_url=token_url) as Nointeractive_with_adfs_obj:
    token = Nointeractive_with_adfs_obj.get_token()
```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite PP
* `token_url:` URL of the authentication service

#### 4. To get a token after initialisation of "AdfsAuthentication" object as shown above: 
```python
token = [Authentication Object Name].get_token()
```

### In KeycloakAuthentication module, two methods are available:
#### 1. To initialise the module for Keycloak authentication:
```python
from dotstat_io.authentication import KeycloakAuthentication
with KeycloakAuthentication.nointeractive_with_secret(
        user=user,
        password=password, 
        token_url=token_url, 
        proxy=proxy) as Nointeractive_with_keycloak_obj:
    token = Nointeractive_with_keycloak_obj.get_token()
```
* `user:` User name for .Stat authentication
* `password:` User name's password
* `token_url:` URL of the authentication service
* `proxy:` URL of the SSL certificates

#### 2. To get a token after initialisation of "KeycloakAuthentication" object as shown above: 
```python
token = [Authentication Object Name].get_token()
```

### In Download_upload module, four methods are available:
#### 1. To download a file from .Stat:
```python
from dotstat_io.download_upload import Download_upload
with Download_upload(token) as Download_upload_obj:
    Returned_Message = Download_upload_obj.download_file(
        dotstat_url, content_format, Path(file_path))
```
* `dotstat_url:` URL of data to be downloaded from .Stat Suite
* `content_format:` Format of the downloaded content
* `file_path:` The full path where the file will downloaded

#### 2. To download streamed content from .Stat:
```python
from dotstat_io.download_upload import Download_upload
with Download_upload(token) as Download_upload_obj:
    Returned_Message = Download_upload_obj.download_stream(
        dotstat_url, content_format)
```
* `dotstat_url:` URL of data to be downloaded from .Stat Suite
* `content_format:` Format of the downloaded content

#### 3. To upload a data file to .Stat:
```python
from dotstat_io.download_upload import Download_upload
with Download_upload(token) as Download_upload_obj:
    Returned_Message = Download_upload_obj.upload_file(
        transfer_url, Path(file_path), space, use_filepath)
```
* `transfer_url:` URL of the transfer service
* `file_path:` The full path of the SDMX-CSV file, which will be uploaded to .Stat Suite
* `space:` Data space where the file will be uploaded
* `use_filepath:` Use a file path of a shared folder accessible by the .Stat data upload engine (for unlimited file sizes)

#### 4. To upload a structure to .Stat:
```python
from dotstat_io.download_upload import Download_upload
with Download_upload(token) as Download_upload_obj:
    Returned_Message = Download_upload_obj.upload_structure(
        transfer_url, Path(file_path))
```
* `transfer_url:` URL of the transfer service
* `file_path:` The full path of the SDMX-ML file, which will be uploaded to .Stat Suite

### For more information about how to use this package, all test cases can be accessed from this [`link`](https://gitlab.algobank.oecd.org/sdd-legacy/dotstat_io/-/blob/main/tests/test_cases.py)
